># 🌐 **bridge‑spoof** – 802.1X‑Testtool mit Bridge & MAC‑Spoofing  
> **Ein interaktives Python‑Script, das eine virtuelle Switch‑Brücke erstellt, die MAC eines Interfaces spoofet und optional tcpdump startet.**

---

## 🚀 Features

| Feature | Was du bekommst |
|---------|-----------------|
| **Bridge (br0)** zwischen zwei beliebigen Interfaces (ethX / enpY…) | Erzeugt einen virtuellen Switch‑Port – ideal für 802.1X‑Tests. |
| **MAC‑Spoofing** | Ändert die MAC deines ersten Interfaces, damit es im Netzwerk „versteckt“ wirkt. |
| **IP auf der Bridge** (optional) | Du kannst dem Bridge‑Interface selbst eine IP/Zulassung zuweisen – dein Host bleibt im selben Subnetz. |
| **tcpdump‑Monitoring** | Live‑Sniffing mit einem voreingestellten Filter für 802.1X, DHCP und HTTP/HTTPS. |
| **Automatisches Root‑Handling** | Das Skript startet sich selbst mit `sudo`, falls es nicht bereits als root läuft. |
| **Sauberes Cleanup** | MAC‑Rücksetzung, tcpdump‑Beenden & Bridge‑Löschen beim Exit oder Ctrl+C. |

---

## 📋 Voraussetzungen (Debian/Ubuntu)

```bash
sudo apt-get update && sudo apt-get install -y \
    python3            # Python‑Interpreter 3.x
    iproute2           # 'ip' – für Bridge/Interface‑Management
    tcpdump            # Live‑Sniffing / Logging
    sudo               # Root‑Aufruf (falls nicht schon root)
```

> **Optional** – falls du das Tool per `pipx` installieren willst:  
> ```bash
> sudo apt-get install -y python3-pip
> pipx ensurepath   # Pfad in die Shell laden
> ```

---

## 📦 Installation über pipx

```bash
# 1️⃣ Projekt klonen (oder als Release‑Tarball holen)
git clone https://github.com/Dx3One/bridge-spoof.git
cd bridge-spoof

# 2️⃣ In einer isolierten Umgebung installieren
pipx install .

# 3️⃣ Jetzt ist der Befehl verfügbar:
bridge-spoof
```

---

## 🔧 Benutzung

```bash
bridge-spoof
```

### Interaktive Menü‑Auswahl

1. **Welches Interface steckt an dem Switch?** – Wähle z. B. `eth0`.
2. **An welchem Interface hängt dein Notebook?** – Wähle z. B. `enp2s0`.
3. **Bridge‑Name (optional)** – Standard: `br0`.
4. **MAC‑Adresse für eth0** – Zufall oder eigene.
5. **IP/Maske für die Bridge (optional)** – z. B. `192.168.1.100/24`.  
   *Wenn du das hier eingibst, bekommst dein Host eine IP im selben Subnetz und bleibt online.*
6. **tcpdump starten?** – `y` / `n`.  
   *Falls ja:* Auswahl des Interfaces für die Aufzeichnung, optional Log‑Datei und Filter.

### Beispiel‑Befehl (ohne Interaktion)

```bash
sudo bridge-spoof \
  --iface-a eth0 \
  --iface-b enp2s0 \
  --host-ip 192.168.1.100/24 \
  --monitor-eth eth1 \
  --filter "eapol or arp or (udp portrange 67-68) or tcp port 80 or tcp port 443"
```

> **Filter‑Beispiel**  
> - `eapol` – 802.1X‑Handshake  
> - `arp` / `udp portrange 67-68` – DHCP  
> - `tcp port 80/443` – HTTP/HTTPS

---

## 📡 Netzwerk‑Setup nach dem Start

| Was passiert | Was du bekommst |
|--------------|----------------|
| **Bridge** (`br0`) ist aktiv. | Alle Pakete zwischen den beiden Interfaces werden weitergeleitet. |
| Optional: IP auf `br0`. | Dein Host erhält eine eigene Adresse im selben Subnetz – nutzt `br0` als normales Interface. |
| tcpdump läuft (falls aktiviert). | Live‑Output oder Logdatei mit allen gefilterten Paketen. |

### Weiterführende Konfiguration

- **NAT / Routing**: Wenn du möchtest, dass dein Host die Internetverbindung anderer Geräte weiterleitet, aktiviere IP‑Forwarding (`sudo sysctl -w net.ipv4.ip_forward=1`) und füge entsprechende iptables‑Regeln hinzu.
- **Separate WAN‑NIC**: Falls dein Host eine andere NIC (z. B. `wlan0`) für das Internet nutzt, bleibt diese völlig unberührt.

---

## 🧩 Troubleshooting

| Problem | Ursache & Lösung |
|---------|------------------|
| Das Skript startet nicht oder liefert „command not found“ | Stelle sicher, dass `$HOME/.local/bin` in deinem PATH liegt (`pipx ensurepath`). Oder führe es explizit mit `sudo $(which bridge-spoof)` aus. |
| Keine Pakete im tcpdump‑Output | Prüfe den Filter – vielleicht ist er zu restriktiv. Starte ohne Filter (`--filter ""`) und schaue, ob überhaupt Traffic erscheint. |
| Bridge wird nicht erstellt | Möglicherweise existiert bereits eine Bridge mit demselben Namen. Der Skript‑Code löscht sie vorher automatisch, aber prüfe mit `ip link show br0`. |
| MAC‑Spoofing funktioniert nicht | Manche NICs erlauben das Spoofing erst nach `ip link set dev <iface> down` – das Skript tut dies bereits. Stelle sicher, dass keine anderen Security‑Features (z. B. macvlans) aktiv sind. |

---

## 🤝 Mitwirken

Beiträge sind gern gesehen!  
Bitte erstelle Issues für Bugs/Feature‑Requests und Pull‑Requests zur Verbesserung des Codes.

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT‑Lizenz** veröffentlicht – frei nutzbar, modifizierbar und verbreitern.  

--- 

Viel Spaß beim Testen von 802.1X! 🚀
