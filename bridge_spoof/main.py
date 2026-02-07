#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bridge_spoof/main.py
--------------------

Ein interaktives Tool zum Erstellen einer Bridge (br0) zwischen zwei Interfaces,
MAC‑Spoofing, optionaler IP auf der Bridge und tcpdump‑Monitoring.
Das Skript startet sich selbst mit `sudo`, falls es nicht als Root läuft.
"""

import subprocess
import sys
import os
import random
import atexit
import signal
import re
import ipaddress

# --------------------------------------------------------------------------- #
#  Hilfsfunktionen ---------------------------------------------------------- #
def run(cmd):
    """Befehl ausführen – bei Fehler aborten."""
    print(f"[▶] {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"[❌] Befehl fehlgeschlagen: {cmd}", file=sys.stderr)
        sys.exit(1)

def random_mac():
    """Zufällige, lokal verwaltete MAC‑Adresse erzeugen."""
    mac = [0x02,
           *[random.randint(0x00, 0xff) for _ in range(5)]]
    return ':'.join(f"{b:02x}" for b in mac)

def get_mac(iface):
    """Aktuelle MAC‑Adresse des Interfaces auslesen."""
    with open(f"/sys/class/net/{iface}/address") as f:
        return f.read().strip()

def set_mac(iface, new_mac):
    """MAC‑Adresse eines Interfaces setzen (down → address → up)."""
    run(["ip", "link", "set", iface, "down"])
    run(["ip", "link", "set", iface, "address", new_mac])
    run(["ip", "link", "set", iface, "up"])

# --------------------------------------------------------------------------- #
#  Live‑Logging (tcpdump) --------------------------------------------------- #
tcpdump_processes = []

def start_tcpdump(iface, logfile=None, filter_expr=""):
    """Startet tcpdump auf *iface* – live oder in Logfile."""
    cmd = ["tcpdump", "-i", iface, "-n", "-l", "-vv"] + filter_expr.split()
    if logfile:
        f_out = open(logfile, "w")
        p = subprocess.Popen(cmd,
                             stdout=f_out,
                             stderr=subprocess.STDOUT)
        print(f"[📦] tcpdump läuft (Log: {logfile}) …")
    else:
        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             universal_newlines=True)
        print("[📦] tcpdump läuft (Live‑Output). Drücke STRG+C zum Beenden.")
        import threading
        def stream_output(proc):
            for line in proc.stdout:
                print(line, end='')
        t = threading.Thread(target=stream_output, args=(p,),
                             daemon=True)
        t.start()
    tcpdump_processes.append(p)

def stop_tcpdump():
    """Stoppt alle laufenden tcpdump‑Prozesse."""
    for p in tcpdump_processes:
        if p.poll() is None:      # läuft noch
            print(f"[🛑] Beende tcpdump (PID {p.pid}) …")
            try:
                p.terminate()
                p.wait(timeout=5)
            except Exception as e:
                print(f"  → {e}")
    tcpdump_processes.clear()

# --------------------------------------------------------------------------- #
#  Aufräumen bei Exit ------------------------------------------------------- #
def cleanup(old_mac_iface, old_mac_value, bridge_nm):
    """MAC wiederherstellen, tcpdump beenden und Bridge löschen."""
    print("\n[🧹] Wiederherstellung der Original‑MAC …")
    set_mac(old_mac_iface, old_mac_value)
    stop_tcpdump()

    # Bridge entfernen
    delete_bridge_if_exists(bridge_nm)
    print("[✅] Alles bereinigt. Script beendet.")

def handle_sigint(sig, frame):
    sys.exit(0)   # sorgt dafür, dass atexit aufgerufen wird

# --------------------------------------------------------------------------- #
#  MAC‑Validierung und Eingabe ---------------------------------------------- #
MAC_RE = re.compile(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")

def prompt_mac():
    """Fragt interaktiv nach einer gültigen MAC‑Adresse."""
    while True:
        inp = input("Bitte gib die gewünschte MAC-Adresse für das erste Interface ein "
                    "(z. B. 02:12:34:56:78:90) oder ENTER für Zufall: ").strip()
        if not inp:
            return random_mac()
        if MAC_RE.match(inp):
            return inp.lower()
        print("[⚠️] Ungültiges Format! Bitte erneut versuchen.")

# --------------------------------------------------------------------------- #
#  Bridge‑Management -------------------------------------------------------- #
def delete_bridge_if_exists(name: str):
    """Löscht eine vorhandene Bridge (falls existiert)."""
    proc = subprocess.run(["ip", "link", "show", name],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if proc.returncode != 0:
        return          # nicht vorhanden
    run(["ip", "link", "set", name, "down"])
    run(["ip", "link", "delete", name, "type", "bridge"])

def detach_from_any_bridge(iface: str):
    """Entfernt ein Interface von jeder vorhandenen Bridge."""
    run(["ip", "link", "set", iface, "nomaster"])

# --------------------------------------------------------------------------- #
#  Interaktive Auswahl der Interfaces ------------------------------------- #
def list_interfaces():
    """Alle Interfaces im System ausgeben (ohne Loopback)."""
    return [d for d in os.listdir("/sys/class/net") if d != "lo"]

def pick_interface(prompt_text):
    """Menü‑Auswahl eines Interfaces."""
    interfaces = list_interfaces()
    print("\nVerfügbare Netzwerk‑Interfaces:")
    for idx, iface in enumerate(interfaces):
        print(f"  {idx}) {iface}")
    while True:
        choice = input(prompt_text + " (Index): ").strip()
        if not choice:
            return None
        try:
            idx = int(choice)
            if 0 <= idx < len(interfaces):
                return interfaces[idx]
        except ValueError:
            pass
        print("Ungültige Auswahl – bitte erneut versuchen.")

# --------------------------------------------------------------------------- #
#  Root‑Wrapper ------------------------------------------------------------- #
def ensure_root():
    """Falls nicht als root, das Skript mit sudo neu starten."""
    if os.geteuid() != 0:
        # Wir bauen den Befehl: sudo python -m bridge_spoof.main "$@"
        cmd = ['sudo', sys.executable, '-m', 'bridge_spoof.main'] + sys.argv[1:]
        print("[🔄] Neustart mit sudo …")
        os.execvp('sudo', cmd)

# --------------------------------------------------------------------------- #
#  Hauptlogik --------------------------------------------------------------- #
def main():
    # ---- Interface‑Auswahl (interaktiv) ----
    iface_a = pick_interface("Wähle Interface für eth0")
    if not iface_a:
        print("[⚠️] Kein Interface gewählt – Script wird beendet.", file=sys.stderr)
        sys.exit(1)

    iface_b = pick_interface("Wähle Interface für eth1")
    if not iface_b:
        print("[⚠️] Kein Interface gewählt – Script wird beendet.", file=sys.stderr)
        sys.exit(1)

    # ---- Bridge‑Name (default br0) ----
    bridge_nm = input("Bridge-Name (Standard: br0): ").strip() or "br0"

    # ---- Original‑MAC sichern ----
    old_mac_val = get_mac(iface_a)
    print(f"[ℹ️] Aktuelle MAC von {iface_a}: {old_mac_val}")

    # ---- Neue MAC setzen (interaktiv) ----
    new_mac = prompt_mac()
    print(f"[🕵️‍♂️] Spoofing von {iface_a} → {new_mac}")
    set_mac(iface_a, new_mac)

    # ---- Host‑IP auf der Bridge (optional) ----
    while True:
        inp = input("IP/Maske für die Bridge eintragen? (z. B. 192.168.1.100/24) oder ENTER: ").strip()
        if not inp:
            host_ip = None
            break
        try:
            ipaddress.ip_interface(inp)   # Validierung
            host_ip = inp
            break
        except ValueError:
            print("[⚠️] Ungültiges Format! Bitte erneut versuchen.")

    # ---- tcpdump? (optional) ----
    monitor = input("Willst du tcpdump starten? (y/N): ").strip().lower()
    if monitor in ('y', 'yes'):
        monitor_iface = pick_interface("Wähle Interface für tcpdump")
        logfile_inp = input("Logfile angeben (oder ENTER für Live‑Ausgabe): ").strip()
        logfile = logfile_inp or None
        DEFAULT_FILTER = "arp or (udp portrange 67-68) or tcp port 80 or tcp port 443"
        filter_expr = input(f"Filter eingeben oder ENTER für Standard [{DEFAULT_FILTER}]: ").strip() or DEFAULT_FILTER
    else:
        monitor_iface = None
        logfile = None
        filter_expr = ""

    # ---- Aufräumen registrieren ----
    atexit.register(cleanup, iface_a, old_mac_val, bridge_nm)

    signal.signal(signal.SIGINT, handle_sigint)

    # ------------------------------------------------------------------- #
    # 1️⃣ Vorherige Bridge ggf. entfernen --------------------------------
    delete_bridge_if_exists(bridge_nm)

    # 2️⃣ Interfaces von vorherigen Bridges trennen ----------------------
    detach_from_any_bridge(iface_a)
    detach_from_any_bridge(iface_b)

    # ------------------------------------------------------------------- #
    # 3️⃣ Bridge erstellen ------------------------------------------------
    print(f"[⚙️] Erstelle Bridge {bridge_nm}")
    run(["ip", "link", "add", bridge_nm, "type", "bridge"])

    for iface in (iface_a, iface_b):
        run(["ip", "link", "set", iface, "down"])
        run(["ip", "link", "set", iface, "master", bridge_nm])
        run(["ip", "link", "set", iface, "up"])

    run(["ip", "link", "set", bridge_nm, "up"])

    # ──────── IP an die Bridge binden (falls gewünscht) ─────────────
    if host_ip:
        print(f"[⚙️] Weise {host_ip} der Bridge {bridge_nm} zu")
        run(["ip", "addr", "add", host_ip, "dev", bridge_nm])

    print(f"[✅] Bridge {bridge_nm} mit {iface_a}/{iface_b} fertig.\n")

    # ---- Live‑Log starten (falls gewünscht) ----
    if monitor_iface:
        start_tcpdump(monitor_iface, logfile=logfile,
                      filter_expr=filter_expr)

    print("[🚀] Alles läuft. Drücke STRG+C zum Beenden …")
    try:
        signal.pause()
    except KeyboardInterrupt:
        pass

# --------------------------------------------------------------------------- #
#  Start – immer ausführen, egal ob mit `-m` oder direkt importiert   ------
ensure_root()
main()
