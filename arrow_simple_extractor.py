#!/usr/bin/env python3
"""
Arrow.it Simple Product Data Extractor
Extrahiert Produktdaten aus der bereits vorhandenen Markdown-Datei
und bereitet sie für Shopware 5/6 auf.
"""

import csv
import json
import re
import sys


class ArrowSimpleExtractor:
    def __init__(self):
        self.products = []
        self.vehicle_info = {}
    
    def parse_markdown_file(self, markdown_file):
        """
        Parst die Markdown-Datei und extrahiert Produktdaten
        """
        print(f"Lese Datei: {markdown_file}")
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrahiere Fahrzeuginformationen
        self._extract_vehicle_info_from_markdown(content)
        
        # Extrahiere Produkte
        self._extract_products_from_markdown(content)
        
        print(f"Fahrzeug: {self.vehicle_info.get('model', 'Unknown')}")
        print(f"Gefunden: {len(self.products)} Produkte")
        
        return self.products, self.vehicle_info
    
    def _extract_vehicle_info_from_markdown(self, content):
        """Extrahiert Fahrzeuginformationen aus Markdown"""
        # Modell
        model_match = re.search(r'HONDA\s+(.+?)\s+\d{4}', content, re.IGNORECASE)
        if model_match:
            self.vehicle_info['model'] = f"Honda {model_match.group(1).strip()}"
        
        # Vehicle Type
        type_match = re.search(r'Vehicle type:\s*\*?\*?([A-Z0-9]+)\*?\*?', content)
        if type_match:
            self.vehicle_info['vehicle_type'] = type_match.group(1).strip()
        
        # Jahre
        years_match = re.search(r'(\d{4})/(\d{4})', content)
        if years_match:
            self.vehicle_info['years'] = f"{years_match.group(1)}-{years_match.group(2)}"
    
    def _extract_products_from_markdown(self, content):
        """Extrahiert Produkte aus Markdown"""
        
        # Definiere Kategorien
        categories = {
            'SILENCERS': 'Silencers',
            'MID-PIPES': 'Mid-pipes',
            'COLLECTORS': 'Collectors'
        }
        
        current_category = None
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Erkenne Kategorien
            for cat_key, cat_name in categories.items():
                if cat_key in line.upper():
                    current_category = cat_name
                    break
            
            # Erkenne Artikelnummern (Format: 72528AK, 72177PD, etc.)
            sku_match = re.match(r'^(72\d{3,}[A-Z]{1,3})$', line)
            if sku_match:
                sku = sku_match.group(1)
                
                # Nächste Zeile ist der Produktname
                name = ''
                if i + 1 < len(lines):
                    name = lines[i + 1].strip()
                
                # Erkenne Zertifizierung
                certification = self._detect_certification(name, line)
                
                # Erkenne kompatible Produkte
                compatible_with = self._detect_compatibility(name)
                
                product = {
                    'sku': sku,
                    'name': name,
                    'category': current_category or 'Unknown',
                    'vehicle_model': self.vehicle_info.get('model', ''),
                    'vehicle_type': self.vehicle_info.get('vehicle_type', ''),
                    'certification': certification,
                    'compatible_with': compatible_with,
                    'material': self._detect_material(name),
                    'specifications': {}
                }
                
                self.products.append(product)
            
            i += 1
    
    def _detect_certification(self, name, context=''):
        """Erkennt die Zertifizierung aus dem Produktnamen"""
        name_lower = name.lower()
        context_lower = context.lower()
        
        if 'racing' in name_lower or 'racing' in context_lower:
            return 'Racing'
        elif 'homologated' in name_lower or 'catalytic' in name_lower:
            return 'ECE'
        else:
            return ''
    
    def _detect_material(self, name):
        """Erkennt das Material aus dem Produktnamen"""
        name_lower = name.lower()
        
        if 'titanium' in name_lower:
            return 'Titanium'
        elif 'aluminium' in name_lower or 'aluminum' in name_lower:
            return 'Aluminium'
        elif 'stainless steel' in name_lower:
            return 'Stainless Steel'
        elif 'carbon' in name_lower:
            return 'Carbon'
        else:
            return ''
    
    def _detect_compatibility(self, name):
        """Erkennt kompatible Produkte aus dem Namen"""
        name_lower = name.lower()
        
        if 'x-kone' in name_lower:
            return 'X-Kone silencers'
        elif 'thunder' in name_lower:
            return 'Thunder silencers'
        else:
            return ''
    
    def add_product_dependencies(self):
        """
        Fügt Produktabhängigkeiten hinzu basierend auf Kompatibilität
        """
        print("\nAnalysiere Produktabhängigkeiten...")
        
        # Erstelle Mapping
        silencers = {p['sku']: p for p in self.products if p['category'] == 'Silencers'}
        midpipes = {p['sku']: p for p in self.products if p['category'] == 'Mid-pipes'}
        collectors = {p['sku']: p for p in self.products if p['category'] == 'Collectors'}
        
        # Definiere Abhängigkeiten
        dependencies = {
            # X-Kone System
            '72528XKI': {  # X-Kone silencer
                'requires': ['72177PD', '72177PZ'],  # Mid-pipes
                'optional': ['72179PD']  # Collector
            },
            # Thunder System
            '72528AK': {  # Thunder aluminium with carby
                'requires': ['72178PD', '72178PZ'],
                'optional': ['72179PD']
            },
            '72528AKN': {  # Thunder aluminium Dark with carby
                'requires': ['72178PD', '72178PZ'],
                'optional': ['72179PD']
            },
            '72528AO': {  # Thunder aluminium
                'requires': ['72178PD', '72178PZ'],
                'optional': ['72179PD']
            },
            '72528AON': {  # Thunder aluminium Dark
                'requires': ['72178PD', '72178PZ'],
                'optional': ['72179PD']
            },
            '72528PK': {  # Thunder titanium with carby
                'requires': ['72178PD', '72178PZ'],
                'optional': ['72179PD']
            },
            '72528PO': {  # Thunder titanium
                'requires': ['72178PD', '72178PZ'],
                'optional': ['72179PD']
            }
        }
        
        # Füge Abhängigkeiten zu Produkten hinzu
        for product in self.products:
            sku = product['sku']
            if sku in dependencies:
                product['requires'] = dependencies[sku].get('requires', [])
                product['optional'] = dependencies[sku].get('optional', [])
        
        print("✓ Produktabhängigkeiten hinzugefügt")
    
    def export_to_csv(self, filename='arrow_products.csv'):
        """
        Exportiert Produkte als CSV für Shopware
        """
        if not self.products:
            print("Keine Produkte zum Exportieren")
            return
        
        # Shopware-kompatible Felder
        fieldnames = [
            'ordernumber',  # SKU
            'name',
            'description',
            'supplier',
            'tax',
            'price',
            'active',
            'instock',
            'categories',
            'propertyGroup1',  # Kategorie
            'propertyValue1',
            'propertyGroup2',  # Material
            'propertyValue2',
            'propertyGroup3',  # Zertifizierung
            'propertyValue3',
            'propertyGroup4',  # Fahrzeugtyp
            'propertyValue4',
            'propertyGroup5',  # Kompatibilität
            'propertyValue5',
            'requires',  # Benötigte Produkte
            'optional'   # Optionale Produkte
        ]
        
        print(f"\nExportiere {len(self.products)} Produkte nach {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
            writer.writeheader()
            
            for product in self.products:
                row = {
                    'ordernumber': product.get('sku', ''),
                    'name': product.get('name', ''),
                    'description': product.get('name', ''),
                    'supplier': 'Arrow',
                    'tax': '19',
                    'price': '',  # Muss manuell eingegeben werden
                    'active': '1',
                    'instock': '',  # Muss manuell eingegeben werden
                    'categories': product.get('vehicle_model', ''),
                    'propertyGroup1': 'Produkttyp',
                    'propertyValue1': product.get('category', ''),
                    'propertyGroup2': 'Material',
                    'propertyValue2': product.get('material', ''),
                    'propertyGroup3': 'Zertifizierung',
                    'propertyValue3': product.get('certification', ''),
                    'propertyGroup4': 'Fahrzeugtyp',
                    'propertyValue4': product.get('vehicle_type', ''),
                    'propertyGroup5': 'Kompatibel mit',
                    'propertyValue5': product.get('compatible_with', ''),
                    'requires': ', '.join(product.get('requires', [])),
                    'optional': ', '.join(product.get('optional', []))
                }
                
                writer.writerow(row)
        
        print(f"✓ CSV-Datei erstellt: {filename}")
    
    def export_to_json(self, filename='arrow_products.json'):
        """
        Exportiert Produkte als JSON für weitere Verarbeitung
        """
        print(f"\nExportiere {len(self.products)} Produkte nach {filename}")
        
        data = {
            'vehicle_info': self.vehicle_info,
            'products': self.products
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON-Datei erstellt: {filename}")
    
    def print_summary(self):
        """Gibt eine Zusammenfassung aus"""
        print("\n" + "=" * 60)
        print("ZUSAMMENFASSUNG")
        print("=" * 60)
        
        # Gruppiere nach Kategorie
        by_category = {}
        for product in self.products:
            cat = product['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(product)
        
        for category, products in by_category.items():
            print(f"\n{category}: {len(products)} Produkte")
            for p in products:
                cert = f" [{p['certification']}]" if p['certification'] else ""
                mat = f" ({p['material']})" if p['material'] else ""
                print(f"  - {p['sku']}: {p['name']}{cert}{mat}")


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("Arrow.it Simple Product Data Extractor")
    print("=" * 60)
    
    # Markdown-Datei
    markdown_file = "/home/ubuntu/page_texts/www.arrow.it_en_assembled_1749_Honda-CRF-300-L-2021-2024.md"
    
    if len(sys.argv) > 1:
        markdown_file = sys.argv[1]
    
    print(f"\nVerwendung: python arrow_simple_extractor.py [markdown_file]")
    print(f"Standard-Datei: {markdown_file}\n")
    
    extractor = ArrowSimpleExtractor()
    
    try:
        # Schritt 1: Parse Markdown
        products, vehicle_info = extractor.parse_markdown_file(markdown_file)
        
        if not products:
            print("Keine Produkte gefunden!")
            return
        
        # Schritt 2: Produktabhängigkeiten hinzufügen
        extractor.add_product_dependencies()
        
        # Schritt 3: Zusammenfassung anzeigen
        extractor.print_summary()
        
        # Schritt 4: Export
        print("\n" + "=" * 60)
        vehicle_slug = vehicle_info.get('model', 'unknown').replace(' ', '_').replace('/', '-')
        csv_filename = f"arrow_{vehicle_slug}.csv"
        json_filename = f"arrow_{vehicle_slug}.json"
        
        extractor.export_to_csv(csv_filename)
        extractor.export_to_json(json_filename)
        
        print("\n" + "=" * 60)
        print("Extraktion abgeschlossen!")
        print("=" * 60)
        print(f"\nDateien erstellt:")
        print(f"  - {csv_filename} (für Shopware Import)")
        print(f"  - {json_filename} (für weitere Verarbeitung)")
        print(f"\n📋 NÄCHSTE SCHRITTE:")
        print(f"  1. CSV-Datei öffnen und Preise eintragen")
        print(f"  2. Lagerbestände eintragen")
        print(f"  3. Bilder manuell zuweisen")
        print(f"  4. Produktabhängigkeiten in Shopware konfigurieren")
        print(f"     (siehe 'requires' und 'optional' Spalten)")
        print(f"  5. CSV in Shopware importieren")
        
    except Exception as e:
        print(f"\nFehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
