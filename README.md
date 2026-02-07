># 🚀 **bridge‑spoof** – Dein interaktives 802.1X‑Testwerkzeug  
> **Einfach. Schnell. Sicher.**  

```
┌─────────────────────────────┐
│  eth0 ──▶ br0 ──▶ eth1     │   ←  Bridge mit MAC‑Spoofing
└─────────────────────────────┘
        ▲                     ▼
     tcpdump (ARP/DHCP/HTTP)   802.1X‑authentifiziertes Gerät
```

**Was ist das?**  
`bridge-spoof` ist ein kleines, aber mächtiges Python‑Tool, das:

* **Eine Bridge (`br0`) zwischen zwei beliebigen Interfaces erstellt** – so bekommst du einen virtuellen Switch unter deinem Host.
* **Die MAC eines Interfaces spooft**, sodass du das Gerät im Netzwerk „verstecken“ kannst (z. B. beim Testen von 802.1X‑Policies).
* **Optional einen `tcpdump`‑Filter** startet, damit du nur ARP, DHCP und HTTP/HTTPS‑Pakete in Echtzeit siehst.
* **Beim Beenden alle Änderungen rückgängig macht** – MAC wiederherstellen, tcpdump stoppen und die Bridge entfernen.

> ⚠️  **Root‑Rechte nötig!**  
> Das Tool verändert Netzwerkschnittstellen.  
> ```bash
> bridge-spoof
> ```

---

## 🎯 Warum solltest du `bridge-spoof` verwenden?

| Feature | Nutzen |
|---------|--------|
| **Interaktive Interface‑Auswahl** | Keine langen Befehlszeilen‑Flags – einfach auswählen, was du brauchst. |
| **MAC‑Spoofing** | Teste 802.1X‑Authentifizierungsmechanismen ohne echte Geräte zu ersetzen. |
| **Bridge‑Erstellung** | Simuliere einen Switch‑Port zwischen zwei Geräten (z. B. Notebook & Attacker). |
| **tcpdump mit Filter** | Nur die Pakete, die dich interessieren – kein Durcheinander. |
| **Automatisches Cleanup** | Du brauchst dir keine Sorgen um Rückstände zu machen. |
| **pipx‑bereit** | Installiere es in einer isolierten Umgebung und halte deinen System‑Python sauber. |

---

## 📦 Installation (mit pipx)

```bash
# 1️⃣ Projekt klonen oder als Release herunterladen
git clone https://github.com/Dx3One/bridge-spoof.git
cd bridge-spoof

# 2️⃣ In einer isolierten Umgebung installieren
pipx install .

# 3️⃣ Jetzt steht der Befehl zur Verfügung:
bridge-spoof
```

> **Hinweis**: Nach der Installation musst du `sudo bridge-spoof` ausführen, weil das Tool Netzwerk‑Interfaces manipuliert.

---

## 🔧 Benutzung

```bash
sudo bridge-spoof
```

1️⃣ Wähle die beiden Interfaces (z. B. `eth0`, `enp2s0`).  
2️⃣ Optional: Gib einen Brückennamen ein – Standard ist `br0`.  
3️⃣ Spoofing‑Option: Gib eine MAC an oder drücke ENTER für Zufall.  
4️⃣ Optional: Eine IP/Maske für die Bridge (z. B. `192.168.1.100/24`).  
5️⃣ Möchtest du tcpdump starten? Ja → Wähle das Interface, ggf. ein Logfile und einen Filter (Standard‑Filter ist ARP/DHCP/HTTP).  
6️⃣ Sobald alles steht – drücke STRG+C zum Beenden.

> 💡 **Tipps**  
> * Um die Bridge später manuell zu entfernen: `sudo ip link delete br0 type bridge`.  
> * Für dynamisches IP‑Zuweisen kannst du stattdessen `dhclient -i br0` starten.

---

## 🤝 Contributing

Du hast Ideen oder Verbesserungen?  
- **Issues** öffnen, wenn du ein Problem findest.  
- **Pull‑Requests** sind herzlich willkommen!  

---

## 📄 Lizenz

Dieses Projekt ist unter der **MIT‑Lizenz** veröffentlicht – frei nutzbar, modifizierbar und verbreitern.

--- 

> **Happy hacking & testing 802.1X!** 🎉  


