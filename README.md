# Arrow.it Produktdaten-Extraktor Webportal

Ein Docker-basiertes Webportal zum Extrahieren von Produktdaten von Arrow.it und Exportieren als CSV für Shopware 5.

## Features

- 🌐 Einfaches Web-Interface zur Eingabe von Arrow.it URLs
- 🔄 Direkter Zugriff auf die Arrow.it API (schnell und zuverlässig)
- 📊 Export als Shopware 5-kompatible CSV-Datei
- 🐳 Docker-basiert, läuft auf Synology NAS
- 📦 Automatische Extraktion von Produktspezifikationen
- 🔗 Produktabhängigkeiten werden automatisch erkannt

## Installation auf Synology NAS

### Voraussetzungen

- Synology NAS mit Docker Package installiert
- Docker Compose (meist bereits enthalten)

### Schritt 1: Dateien hochladen

Laden Sie alle Projektdateien auf Ihr Synology NAS hoch, z.B. in:
```
/docker/arrow-scraper/
```

### Schritt 2: Docker Container starten

1. Öffnen Sie Docker in der Synology DSM
2. Navigieren Sie zu "Container" > "Image" > "Erstellen"
3. Wählen Sie "docker-compose.yml" aus dem Projektverzeichnis
4. Klicken Sie auf "Erstellen"

Oder über SSH:

```bash
cd /docker/arrow-scraper
docker-compose up -d
```

### Schritt 3: Webportal aufrufen

Öffnen Sie in Ihrem Browser:
```
http://[IHR-NAS-IP]:5000
```

## Verwendung

1. Öffnen Sie das Webportal
2. Kopieren Sie eine Arrow.it Produkt-URL, z.B.:
   ```
   https://www.arrow.it/en/assembled/1975/BMW-S-1000-R---M-1000-R-2025
   ```
3. Fügen Sie die URL in das Eingabefeld ein
4. (Optional) Aktivieren/deaktivieren Sie "Detaillierte Spezifikationen laden"
5. Klicken Sie auf "Produkte extrahieren"
6. Warten Sie, bis die Extraktion abgeschlossen ist
7. Laden Sie die CSV-Datei herunter

## Exportierte Daten

Die CSV-Datei enthält folgende Felder:

- `ordernumber` - Artikelnummer (SKU)
- `name` - Produktname
- `description` - Beschreibung
- `supplier` - Lieferant (Arrow)
- `tax` - Steuersatz (19%)
- `price` - Verkaufspreis (muss manuell ausgefüllt werden)
- `active` - Aktiv (1=ja, 0=nein)
- `instock` - Lagerbestand (muss manuell ausgefüllt werden)
- `categories` - Kategorien
- `propertyGroup1-8` / `propertyValue1-8` - Produkteigenschaften
- `weight` - Gewicht
- `requires` - Benötigte Artikel (kommagetrennt)
- `optional` - Optionale Artikel (kommagetrennt)

### Produkteigenschaften

1. **Produkttyp**: Silencers, Mid-pipes, Collectors
2. **Material Körper**: Aluminium, Titan, Edelstahl
3. **Material Innen**: Edelstahl
4. **Zertifizierung**: ECE, Euro4, Racing
5. **Kompatibel mit**: Thunder/X-Kone silencers
6. **DB-Killer**: Si/No
7. **Lambda-Sonde**: Si/No
8. **CO-Sonde**: Si/No

## Shopware 5 Import

1. Öffnen Sie die CSV-Datei in Excel oder einem CSV-Editor
2. Füllen Sie folgende Felder aus:
   - `price` - Verkaufspreise
   - `instock` - Lagerbestände
   - `categories` - Shopware-Kategorien
3. Importieren Sie die CSV in Shopware:
   - Einstellungen → Import/Export
   - Artikelprofil auswählen
   - CSV-Datei hochladen
   - Spalten zuordnen (sollte automatisch funktionieren)
   - Import starten

## Verzeichnisstruktur

```
arrow-scraper/
├── app.py                 # Flask Backend
├── requirements.txt       # Python Abhängigkeiten
├── Dockerfile            # Docker Image Definition
├── docker-compose.yml    # Docker Compose Konfiguration
├── templates/
│   └── index.html        # Frontend Web-Interface
└── exports/              # Exportierte CSV-Dateien (wird automatisch erstellt)
```

## API Endpunkte

### POST /api/extract
Extrahiert Produktdaten von einer Arrow.it URL.

**Request:**
```json
{
  "url": "https://www.arrow.it/en/assembled/1975/...",
  "load_specifications": true
}
```

**Response:**
```json
{
  "success": true,
  "vehicle_id": 1975,
  "total_products": 15,
  "filename": "arrow_vehicle_1975_20241201_143022.csv",
  "download_url": "/api/download/arrow_vehicle_1975_20241201_143022.csv"
}
```

### GET /api/download/<filename>
Lädt eine exportierte CSV-Datei herunter.

### GET /api/health
Health Check Endpunkt.

## Fehlerbehebung

### Container startet nicht
- Überprüfen Sie, ob Port 5000 bereits belegt ist
- Ändern Sie den Port in `docker-compose.yml` falls nötig

### Keine Produkte gefunden
- Überprüfen Sie, ob die URL korrekt ist
- Stellen Sie sicher, dass die URL das Format `/assembled/{ID}/` enthält

### Timeout-Fehler
- Erhöhen Sie den Timeout in `Dockerfile` (Zeile: `--timeout 300`)
- Bei vielen Produkten kann die Extraktion länger dauern

## Technische Details

- **Backend**: Flask mit Gunicorn
- **API**: Arrow.it REST API
- **Datenformat**: CSV mit Semikolon-Trennung (Shopware 5 kompatibel)
- **Encoding**: UTF-8

## Sicherheit

- Das Webportal läuft nur im lokalen Netzwerk
- Keine Authentifizierung erforderlich (nur für lokalen Gebrauch)
- Bei Bedarf kann eine Authentifizierung hinzugefügt werden

## Updates

Um auf die neueste Version zu aktualisieren:

```bash
cd /docker/arrow-scraper
docker-compose down
docker-compose pull
docker-compose up -d
```

## Lizenz

Dieses Tool wurde für den persönlichen Gebrauch entwickelt. Die Produktdaten gehören Arrow Special Parts.
