# Arrow.it Produktdaten-Struktur Analyse

## URL
https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024

## Fahrzeugtyp
- Modell: Honda CRF 300 L 2021/2024
- Vehicle type: ND16

## Produktkategorien

### 1. SILENCERS (Schalldämpfer)
- 72528AK - Thunder aluminium silencer with carby end cap
- 72528AKN - Thunder aluminium "Dark" silencer with carby end cap
- 72528AO - Thunder aluminium silencer
- 72528AON - Thunder aluminium "Dark" silencer
- 72528PK - Thunder titanium silencer with carby end cap
- 72528PO - Thunder titanium silencer
- 72528XKI - X-Kone silencer

### 2. MID-PIPES (Mittelrohre)
- 72177PD - Racing link-pipe for X-Kone silencers (Racing)
- 72177PZ - Catalytic homologated mid-pipe for X-Kone silencers (ECE)
- 72178PD - Racing link-pipe for Thunder silencers (Racing)
- 72178PZ - Catalytic homologated mid-pipe for Thunder silencers (ECE)

### 3. COLLECTORS (Kollektoren)
- 72179PD - Racing collector (Racing)

## Produktdetails (Beispiel: 72177PD)

**Features** | **Values**
--- | ---
Mid-pipe material | stainless steel
Silencer mounting | welded mount
Silencer body lenght (mm) | 0,00
Junction (inlet) diameter (mm) | 32,00
Junction (outlet) diameter (mm) | 45,00
CO sensor plug | No
Oxygen sensor plug | No
Db Killer | No
Weight (Kg) | 0,65

## Produktkennzeichnung
- **ECE** = Homologiert (ECE-Zertifizierung)
- **Racing** = Nur für Rennstrecke

## Datenstruktur für CSV-Export

### Benötigte Felder für Shopware:
1. **Artikelnummer** (SKU)
2. **Produktname** (Name)
3. **Kategorie** (Category)
4. **Beschreibung** (Description)
5. **Technische Daten** (Properties):
   - Material
   - Montage-Typ
   - Länge
   - Einlass-Durchmesser
   - Auslass-Durchmesser
   - CO Sensor
   - Lambda Sensor
   - DB-Killer
   - Gewicht
6. **Zertifizierung** (ECE/Racing)
7. **Fahrzeugzuordnung** (Vehicle compatibility)
8. **Produktabhängigkeiten** (Compatible with)

## Herausforderungen

1. **Bilder**: Müssen manuell zugewiesen werden
2. **Produktabhängigkeiten**: Welcher Schalldämpfer passt zu welchem Mid-Pipe?
   - X-Kone Schalldämpfer → 72177PD/72177PZ Mid-Pipes
   - Thunder Schalldämpfer → 72178PD/72178PZ Mid-Pipes
3. **Vollständige Systeme**: Kombinationen aus Collector + Mid-Pipe + Silencer
4. **Mehrsprachigkeit**: Produktnamen sind auf Englisch

## Nächste Schritte

1. Alle Produktspezifikationen extrahieren (per Klick auf "Specification")
2. Datenstruktur in CSV-Format konvertieren
3. Produktabhängigkeiten dokumentieren
4. Tool entwickeln für automatische Extraktion
