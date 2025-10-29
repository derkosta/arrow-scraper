# Arrow Scraper - Synology DSM Setup

## Übersicht
Dieses Repository enthält einen vollständig konfigurierten Arrow.it Produktdaten-Extraktor für Synology DSM Docker.

## Voraussetzungen
- Synology NAS mit DSM 7.0 oder höher
- Docker Package installiert
- Port 5060 verfügbar

## Installation auf Synology DSM

### 1. Repository klonen
```bash
# SSH in Synology einloggen
ssh admin@your-synology-ip

# In den Docker-Ordner wechseln
cd /volume1/docker/

# Repository klonen
git clone https://github.com/your-username/Arrow-Parser.git arrow_scraper
cd arrow_scraper
```

### 2. Umgebungsdatei erstellen
```bash
# .env-Datei aus Beispiel erstellen
cp env.example .env

# .env-Datei bearbeiten (optional)
nano .env
```

### 3. Ordnerstruktur erstellen
```bash
# Erforderliche Ordner erstellen
mkdir -p /volume1/docker/arrow_scraper/data/exports
mkdir -p /volume1/docker/arrow_scraper/data/logs
mkdir -p /volume1/docker/arrow_scraper/data

# Berechtigungen setzen
chmod 755 /volume1/docker/arrow_scraper/data
chmod 755 /volume1/docker/arrow_scraper/data/exports
chmod 755 /volume1/docker/arrow_scraper/data/logs
```

### 4. Docker Stack erstellen

#### Option A: Über DSM Web-Interface
1. DSM öffnen → Container Manager
2. "Container" → "Erstellen" → "Mit Docker Compose"
3. Projektname: `arrow-scraper`
4. Pfad: `/volume1/docker/arrow_scraper`
5. Compose-Datei: `docker-compose.yml`
6. "Erstellen" klicken

#### Option B: Über SSH/Command Line
```bash
cd /volume1/docker/arrow_scraper
docker-compose up -d
```

## Konfiguration

### Umgebungsvariablen (.env)
Die wichtigsten Einstellungen in der `.env`-Datei:

```env
# Port-Konfiguration
WEB_PORT=5000

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/arrow_scraper.log

# Zeitzone
TZ=Europe/Berlin

# API-Einstellungen
REQUEST_TIMEOUT=30
REQUEST_DELAY=0.3
```

### Volumes
- `/volume1/docker/arrow_scraper/data/exports` → Exportierte CSV/JSON-Dateien
- `/volume1/docker/arrow_scraper/data/logs` → Log-Dateien
- `/volume1/docker/arrow_scraper/data` → Allgemeine Daten
- `/volume1/docker/arrow_scraper/.env` → Umgebungsvariablen

## Verwendung

### Web-Interface
Nach dem Start ist die Anwendung verfügbar unter:
- **URL**: `http://your-synology-ip:5060`
- **Health Check**: `http://your-synology-ip:5060/api/health`

### API-Endpunkte
- `POST /api/extract` - Produktdaten extrahieren
- `GET /api/download/<filename>` - Datei herunterladen
- `GET /api/health` - Status prüfen

### Beispiel-API-Aufruf
```bash
curl -X POST http://your-synology-ip:5060/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024",
    "load_specifications": true
  }'
```

## Wartung

### Logs anzeigen
```bash
# Container-Logs
docker logs arrow-scraper

# Log-Dateien
tail -f /volume1/docker/arrow_scraper/data/logs/arrow_scraper.log
```

### Container neu starten
```bash
docker-compose restart
```

### Updates
```bash
cd /volume1/docker/arrow_scraper
git pull
docker-compose down
docker-compose up -d --build
```

### Backup
```bash
# Daten sichern
tar -czf arrow_scraper_backup_$(date +%Y%m%d).tar.gz \
  /volume1/docker/arrow_scraper/data \
  /volume1/docker/arrow_scraper/.env
```

## Troubleshooting

### Container startet nicht
1. Logs prüfen: `docker logs arrow-scraper`
2. Port 5060 verfügbar? `netstat -tulpn | grep 5060`
3. Ordnerberechtigungen prüfen

### Keine Verbindung zur API
1. Firewall-Regeln prüfen
2. Port 5060 freigeben
3. Container-Status: `docker ps`

### Speicherplatz
```bash
# Speicherplatz prüfen
df -h /volume1/docker/arrow_scraper

# Alte Logs löschen
find /volume1/docker/arrow_scraper/data/logs -name "*.log" -mtime +30 -delete
```

## Sicherheit

### Firewall
- Port 5060 nur für interne Netzwerke freigeben
- Reverse Proxy mit SSL empfohlen

### Updates
- Regelmäßige Updates durchführen
- Sicherheits-Patches zeitnah einspielen

## Support
Bei Problemen:
1. Logs prüfen
2. GitHub Issues erstellen
3. Dokumentation durchgehen

---
**Version**: 1.0.0  
**Letzte Aktualisierung**: $(date +%Y-%m-%d)
