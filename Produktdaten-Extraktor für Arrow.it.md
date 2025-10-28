# Produktdaten-Extraktor für Arrow.it

Dieses Projekt enthält ein Tool zur Extraktion von Produktdaten von der Arrow.it Webseite und zur Aufbereitung dieser Daten für den Import in Shopware 5 oder 6.

## Übersicht

Das Hauptziel ist es, den Prozess der Datenerfassung zu automatisieren, um die manuelle Eingabe zu reduzieren. Das bereitgestellte Tool extrahiert Produktdetails für ein bestimmtes Fahrzeugmodell und exportiert sie in eine Shopware-kompatible CSV-Datei sowie eine detaillierte JSON-Datei.

## Enthaltene Dateien

1.  **`arrow_Honda_CRF_300_L.csv`**: Die für Shopware formatierte CSV-Datei. Diese Datei enthält die extrahierten Produktdaten für das Modell "Honda CRF 300 L (2021-2024)".
2.  **`arrow_Honda_CRF_300_L.json`**: Eine JSON-Datei mit den vollständigen extrahierten Daten, einschließlich der erkannten Produktabhängigkeiten. Diese Datei ist nützlich für die manuelle Überprüfung und Konfiguration von Produkt-Sets in Shopware.
3.  **`arrow_simple_extractor.py`**: Das Python-Skript, das zur Extraktion der Daten verwendet wurde. Es liest eine gespeicherte Textversion der Webseite und parst die darin enthaltenen Informationen.
4.  **`README.md`**: Diese Anleitungsdatei.

## Schritt-für-Schritt-Anleitung zur Verwendung

Der Extraktionsprozess wurde bereits für Sie durchgeführt. Die resultierenden Dateien (`.csv` und `.json`) sind diesem Ergebnis beigefügt. Hier sind die nächsten Schritte, die Sie durchführen müssen:

### 1. CSV-Datei bearbeiten

Öffnen Sie die Datei `arrow_Honda_CRF_300_L.csv` mit einem Tabellenkalkulationsprogramm (z.B. Microsoft Excel, LibreOffice Calc, Google Sheets).

Folgende Spalten müssen manuell ausgefüllt werden:

*   **`price`**: Tragen Sie hier die Verkaufspreise für die jeweiligen Produkte ein.
*   **`instock`**: Geben Sie hier die Lagerbestände für die Produkte an.

### 2. Bilder zuweisen

Laden Sie die Produktbilder in Ihr Shopware-System hoch. Nach dem Import der CSV-Datei müssen Sie die Bilder den entsprechenden Produkten manuell zuweisen. Der einfachste Weg ist die Verwendung der Artikelnummer (`ordernumber`) als Bildname (z.B. `72528AK.jpg`).

### 3. Produktabhängigkeiten konfigurieren

Die CSV-Datei enthält die Spalten `requires` und `optional`, die die erkannten Abhängigkeiten auflisten. Zum Beispiel muss ein Schalldämpfer mit einem bestimmten Mittelrohr kombiniert werden.

*   **Beispiel**: Der Schalldämpfer `72528XKI` (X-Kone) benötigt entweder das Mid-Pipe `72177PD` (Racing) oder `72177PZ` (Homologiert).

Diese Abhängigkeiten müssen in Shopware konfiguriert werden. Dies kann über Produkt-Sets, Varianten oder benutzerdefinierte Optionen geschehen, je nachdem, wie Ihr Shop eingerichtet ist. Die `arrow_Honda_CRF_300_L.json`-Datei bietet eine klarere, strukturierte Ansicht dieser Beziehungen.

### 4. Import in Shopware

Nachdem Sie die CSV-Datei vervollständigt haben, können Sie sie über das Import/Export-Modul in Shopware importieren. Verwenden Sie ein Standardprofil für den Artikelimport und stellen Sie sicher, dass die Spaltentrennzeichen und Kopfzeilen korrekt zugeordnet sind.

## Technische Details zum Extraktions-Tool

Das Skript `arrow_simple_extractor.py` wurde entwickelt, um die Produktdaten aus einer zuvor gespeicherten Markdown-Datei der Webseite zu parsen. Dieser Ansatz wurde gewählt, da die Webseite ihre Inhalte dynamisch mit JavaScript lädt, was eine direkte Extraktion aus dem HTML-Quellcode unzuverlässig macht.

Das Skript führt folgende Schritte aus:

1.  **Lesen der Markdown-Datei**: Lädt den gesamten Textinhalt der Seite.
2.  **Extrahieren von Fahrzeuginformationen**: Identifiziert das Fahrzeugmodell und den Typ.
3.  **Extrahieren von Produkten**: Durchsucht den Text nach Produktkategorien (Silencers, Mid-pipes, Collectors) und den dazugehörigen Produkten anhand ihrer Artikelnummern.
4.  **Analysieren von Abhängigkeiten**: Erkennt aus den Produktnamen, welche Teile miteinander kompatibel sind (z.B. "link-pipe for X-Kone silencers").
5.  **Export**: Schreibt die aufbereiteten Daten in eine CSV- und eine JSON-Datei.

Dieser Ansatz ist schnell und robust, solange die Struktur der Webseite und die Benennung der Produkte konsistent bleiben.
