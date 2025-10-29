# Arrow.it Produktdaten-Extraktor

Ein modernes Web-Tool zum Scannen, Bearbeiten und Exportieren von Produktdaten von Arrow.it.

## 🚀 Features

- **🔍 Produkt-Scanner**: Automatisches Extrahieren von Produktdaten aus Arrow.it URLs
- **👁️ Vorschau**: Übersichtliche Darstellung aller gesammelten Informationen
- **🖼️ Bilder**: Hotlinked Produktbilder direkt in der Ansicht
- **✏️ Bearbeitung**: Inline-Bearbeitung aller Produktdaten vor dem Export
- **📥 CSV-Export**: Export der bearbeiteten Daten als CSV-Datei
- **🐳 Docker**: Einfache Bereitstellung mit Docker Compose
- **📱 Responsive**: Optimiert für Desktop und Mobile

## 🎯 Verwendung

1. **URL eingeben**: Arrow.it Produkt-URL in das Eingabefeld einfügen
2. **Scannen**: Auf "Produkte scannen" klicken
3. **Vorschau**: Alle Produktdaten werden übersichtlich angezeigt
4. **Bearbeiten**: Daten direkt in der Ansicht anpassen
5. **Exportieren**: Als CSV-Datei herunterladen

## 🛠️ Installation

### Docker (Empfohlen)

```bash
# Repository klonen
git clone https://github.com/derkosta/arrow-scraper.git
cd arrow-scraper

# Container starten
docker-compose up -d
```

### Lokale Installation

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Anwendung starten
python app.py
```

## 🌐 Zugriff

- **Web-Interface**: http://localhost:8080
- **Health Check**: http://localhost:8080/api/health

## 📁 Projektstruktur

```
arrow-scraper/
├── app.py                 # Hauptanwendung
├── templates/
│   └── index.html        # Web-Interface
├── docker-compose.yml    # Docker-Konfiguration
├── Dockerfile           # Container-Definition
├── requirements.txt     # Python-Abhängigkeiten
├── env.example         # Umgebungsvariablen-Vorlage
├── setup-synology.sh   # Synology Setup-Script
├── fix-permissions.sh  # Berechtigungs-Fix-Script
└── SYNOLOGY_SETUP.md   # Synology-Anleitung
```

## 🔧 API-Endpunkte

- `POST /api/scan` - Produktdaten scannen
- `POST /api/export` - Bearbeitete Daten exportieren
- `GET /api/download/<filename>` - CSV-Datei herunterladen
- `GET /api/health` - Status prüfen

## 🐳 Docker-Konfiguration

### Umgebungsvariablen

```env
FLASK_ENV=production
DEBUG=false
WEB_HOST=0.0.0.0
WEB_PORT=5000
LOG_LEVEL=INFO
TZ=Europe/Berlin
```

### Volumes

- `./data/exports` → Exportierte CSV-Dateien
- `./data/logs` → Log-Dateien
- `./data` → Allgemeine Daten

## 📋 Beispiel-URLs

```
https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024
https://www.arrow.it/en/assembled/1975/BMW-S-1000-R---M-1000-R-2025
https://www.arrow.it/en/assembled/1970/Ducati-Panigale-V2---V2S-2025
```

## 🔒 Sicherheit

- Container läuft mit eingeschränkten Berechtigungen
- Keine sensiblen Daten in Logs
- Input-Validierung für alle API-Endpunkte

## 🚀 Synology DSM

Für Synology NAS-Systeme siehe [SYNOLOGY_SETUP.md](SYNOLOGY_SETUP.md)

## 📝 Lizenz

MIT License

## 🤝 Beitragen

1. Fork des Repositories
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen

## 📞 Support

Bei Problemen oder Fragen:
1. GitHub Issues erstellen
2. Logs prüfen: `docker logs arrow-scraper`
3. Dokumentation durchgehen

---

**Version**: 2.0.0  
**Letzte Aktualisierung**: $(date +%Y-%m-%d)