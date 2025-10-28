# Arrow.it Produktdaten-Extraktor (API-Version)

Dieses verbesserte Tool nutzt die offiziellen API-Endpunkte von Arrow.it, um Produktdaten direkt und zuverlässig zu extrahieren und für den Import in Shopware 5 oder 6 aufzubereiten.

## Übersicht

Im Gegensatz zur ersten Version, die Daten aus dem HTML-Text der Webseite extrahiert hat, verwendet diese Version die **Arrow.it REST API**. Dies bietet folgende Vorteile:

*   **Zuverlässigkeit**: Direkter Zugriff auf strukturierte Daten ohne Abhängigkeit von der Webseiten-Darstellung
*   **Vollständigkeit**: Zugriff auf detaillierte Produktspezifikationen (Material, Gewicht, Durchmesser, Sensoren, etc.)
*   **Mehrsprachigkeit**: Die API liefert Produktbeschreibungen in mehreren Sprachen (EN, DE, IT, FR, ES)
*   **Geschwindigkeit**: Schnellerer Datenabruf ohne Browser-Rendering

## Enthaltene Dateien

### Hauptdateien (API-basiert)

1.  **`arrow_vehicle_1749_api.csv`**: Die für Shopware formatierte CSV-Datei mit vollständigen Spezifikationen
2.  **`arrow_vehicle_1749_api.json`**: JSON-Datei mit allen API-Daten und Produktabhängigkeiten
3.  **`arrow_api_extractor.py`**: Das Python-Skript für die API-basierte Extraktion

### Vergleichsdateien (Text-basiert)

4.  **`arrow_Honda_CRF_300_L.csv`**: CSV aus der ersten Version (Text-Parsing)
5.  **`arrow_Honda_CRF_300_L.json`**: JSON aus der ersten Version
6.  **`arrow_simple_extractor.py`**: Das ursprüngliche Text-basierte Skript

## API-Endpunkte

Das Tool nutzt folgende Arrow.it API-Endpunkte:

*   **`/api/en/montaggi/{vehicle_id}`**: Listet alle Produkte für ein Fahrzeug
*   **`/api/en/montaggi/specifiche/{article_id}`**: Detaillierte Spezifikationen für ein Produkt
*   **`/api/en/montaggi/foto/{vehicle_id}/{index}`**: Produktbilder (optional)
*   **`/api/en/montaggi/schema/{vehicle_id}`**: Montage-Schema (optional)

## Verwendung des API-Extraktors

### Voraussetzungen

*   Python 3.7 oder höher
*   `requests`-Bibliothek (normalerweise vorinstalliert)

### Ausführung

```bash
python arrow_api_extractor.py [URL]
```

**Beispiel:**

```bash
python arrow_api_extractor.py "https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024"
```

Das Skript wird Sie fragen, ob Sie detaillierte Spezifikationen laden möchten. Antworten Sie mit `j` (ja) oder `n` (nein).

### Ausgabe

Das Skript erstellt zwei Dateien:

*   **CSV-Datei**: Für direkten Import in Shopware
*   **JSON-Datei**: Für manuelle Überprüfung und erweiterte Verarbeitung

## Extrahierte Daten

Die API-Version extrahiert deutlich mehr Informationen als die Text-basierte Version:

### Basis-Informationen

*   Artikelnummer (SKU)
*   Produktname (mehrsprachig)
*   Kategorie (Silencers, Mid-pipes, Collectors)
*   Zertifizierung (ECE, Euro4, Racing)

### Detaillierte Spezifikationen

*   **Material**: Körper, Innenmaterial, Endkappe
*   **Abmessungen**: Länge, Einlass-Durchmesser, Auslass-Durchmesser
*   **Gewicht**: In Kilogramm
*   **Sensoren**: Lambda-Sonde, CO-Sonde
*   **DB-Killer**: Vorhanden (Si/No)
*   **Montage**: Befestigungsart (z.B. "welded mount")

### Produktabhängigkeiten

Das Tool erkennt automatisch, welche Teile zusammen benötigt werden:

*   **Thunder Schalldämpfer** → benötigen Thunder Mid-Pipes (72178PD oder 72178PZ)
*   **X-Kone Schalldämpfer** → benötigen X-Kone Mid-Pipes (72177PD oder 72177PZ)
*   **Alle Schalldämpfer** → können optional mit Collector (72179PD) kombiniert werden

## Shopware-Import

### CSV-Struktur

Die CSV-Datei ist für Shopware 5/6 optimiert und enthält folgende Spalten:

| Spalte | Beschreibung | Manuell auszufüllen |
|--------|--------------|---------------------|
| `ordernumber` | Artikelnummer (SKU) | ✗ |
| `name` | Produktname | ✗ |
| `description` | Beschreibung | ✗ |
| `supplier` | Lieferant (Arrow) | ✗ |
| `tax` | Steuersatz (19%) | ✗ |
| `price` | Verkaufspreis | ✓ |
| `active` | Aktiv (1=ja, 0=nein) | ✗ |
| `instock` | Lagerbestand | ✓ |
| `categories` | Kategorien | ✓ |
| `propertyGroup1-8` | Eigenschaften | ✗ |
| `propertyValue1-8` | Eigenschaftswerte | ✗ |
| `weight` | Gewicht | ✗ |
| `requires` | Benötigte Artikel | ✗ |
| `optional` | Optionale Artikel | ✗ |

### Eigenschaften (Properties)

Die CSV enthält folgende Produkt-Eigenschaften:

1.  **Produkttyp**: Silencers, Mid-pipes, Collectors
2.  **Material Körper**: Aluminium, Titan, Edelstahl
3.  **Material Innen**: Edelstahl
4.  **Zertifizierung**: ECE, Euro4, Racing
5.  **Kompatibel mit**: Thunder/X-Kone silencers
6.  **DB-Killer**: Si/No
7.  **Lambda-Sonde**: Si/No
8.  **CO-Sonde**: Si/No

## Nächste Schritte

### 1. CSV-Datei bearbeiten

Öffnen Sie `arrow_vehicle_1749_api.csv` und füllen Sie aus:

*   **`price`**: Verkaufspreise
*   **`instock`**: Lagerbestände
*   **`categories`**: Shopware-Kategorien (z.B. "Motorrad > Auspuff > Honda")

### 2. Bilder zuweisen

Laden Sie Produktbilder in Shopware hoch. Benennen Sie die Bilder nach der Artikelnummer:

*   `72528AK.jpg`
*   `72528XKI.jpg`
*   etc.

Shopware kann dann automatisch die Bilder zuordnen.

### 3. Produktabhängigkeiten konfigurieren

Die Spalten `requires` und `optional` zeigen, welche Artikel zusammengehören:

**Beispiel:**

*   Artikel `72528XKI` (X-Kone Schalldämpfer)
    *   **Benötigt**: `72177PD, 72177PZ` (Mid-Pipes)
    *   **Optional**: `72179PD` (Collector)

Konfigurieren Sie diese Abhängigkeiten in Shopware als:

*   **Produkt-Sets** (Bundle)
*   **Varianten** (wenn verschiedene Kombinationen möglich sind)
*   **Cross-Selling** (für optionale Teile)

### 4. Import in Shopware

1.  Gehen Sie zu **Einstellungen → Import/Export**
2.  Wählen Sie ein Artikelprofil
3.  Laden Sie die CSV-Datei hoch
4.  Ordnen Sie die Spalten zu (sollte automatisch funktionieren)
5.  Starten Sie den Import

## Vergleich: API vs. Text-Extraktion

| Feature | Text-Extraktion | API-Extraktion |
|---------|-----------------|----------------|
| Zuverlässigkeit | Mittel | Hoch |
| Spezifikationen | Begrenzt | Vollständig |
| Gewicht | ✗ | ✓ |
| Material-Details | Teilweise | Vollständig |
| DB-Killer Info | ✗ | ✓ |
| Sensoren | ✗ | ✓ |
| Mehrsprachig | ✗ | ✓ |
| Geschwindigkeit | Langsam | Schnell |

**Empfehlung**: Verwenden Sie die API-Version (`arrow_api_extractor.py`) für neue Extractions.

## Weitere Fahrzeuge extrahieren

Um Daten für andere Fahrzeuge zu extrahieren:

1.  Besuchen Sie die Arrow.it Webseite
2.  Wählen Sie das gewünschte Fahrzeug
3.  Kopieren Sie die URL (z.B. `https://www.arrow.it/en/assembled/XXXX/...`)
4.  Führen Sie das Skript aus:

```bash
python arrow_api_extractor.py "https://www.arrow.it/en/assembled/XXXX/..."
```

## Technische Details

### API-Authentifizierung

Die Arrow.it API benötigt keine Authentifizierung für öffentliche Produktdaten. Die Anfragen werden mit folgenden Parametern gesendet:

*   `UserId`: Leer (für öffentlichen Zugriff)
*   `Brand`: "Arrow"

### Rate Limiting

Das Skript fügt eine Pause von 0,3 Sekunden zwischen API-Anfragen ein, um die Server nicht zu überlasten.

### Fehlerbehandlung

Das Skript behandelt folgende Fehler:

*   Netzwerkfehler
*   Ungültige Fahrzeug-IDs
*   Fehlende Spezifikationen
*   API-Timeouts

## Support

Bei Fragen oder Problemen:

1.  Überprüfen Sie die JSON-Datei für detaillierte API-Antworten
2.  Testen Sie die API-Endpunkte direkt mit `curl`
3.  Prüfen Sie die Shopware-Logs nach dem Import

## Lizenz

Dieses Tool wurde für den persönlichen Gebrauch entwickelt. Die Produktdaten gehören Arrow Special Parts.
