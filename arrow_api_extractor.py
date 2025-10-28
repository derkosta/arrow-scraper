#!/usr/bin/env python3
"""
Arrow.it API Product Data Extractor
Extrahiert Produktdaten direkt über die Arrow.it API
und bereitet sie für Shopware 5/6 auf.
"""

import requests
import csv
import json
import sys
import time
from typing import List, Dict, Optional


class ArrowAPIExtractor:
    def __init__(self):
        self.base_url = "https://www.arrow.it"
        self.api_base = f"{self.base_url}/api/en"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
    def extract_vehicle_id_from_url(self, url: str) -> Optional[int]:
        """
        Extrahiert die Fahrzeug-ID aus der URL
        Beispiel: https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024
        """
        import re
        match = re.search(r'/assembled/(\d+)/', url)
        if match:
            return int(match.group(1))
        return None
    
    def get_products(self, vehicle_id: int) -> List[Dict]:
        """
        Holt alle Produkte für ein Fahrzeug über die API
        """
        url = f"{self.api_base}/montaggi/{vehicle_id}"
        
        print(f"Lade Produkte von API: {url}")
        
        try:
            # POST-Request mit den erforderlichen Parametern
            response = self.session.post(url, data={'UserId': '', 'Brand': 'Arrow'})
            response.raise_for_status()
            
            products = response.json()
            print(f"✓ {len(products)} Produkte von API geladen")
            return products
        except Exception as e:
            print(f"✗ Fehler beim Laden der Produkte: {e}")
            return []
    
    def get_product_specifications(self, article_id: int) -> Optional[Dict]:
        """
        Holt detaillierte Spezifikationen für ein Produkt
        """
        url = f"{self.api_base}/montaggi/specifiche/{article_id}"
        
        try:
            response = self.session.get(url, params={'UserId': '', 'Brand': 'Arrow'})
            response.raise_for_status()
            
            specs = response.json()
            if specs and len(specs) > 0:
                return specs[0]
            return None
        except Exception as e:
            print(f"  ✗ Fehler beim Laden der Spezifikationen: {e}")
            return None
    
    def get_vehicle_info(self, vehicle_id: int) -> Dict:
        """
        Holt Fahrzeuginformationen (optional, falls verfügbar)
        """
        # Könnte über andere API-Endpunkte erweitert werden
        return {
            'vehicle_id': vehicle_id,
            'model': '',
            'vehicle_type': ''
        }
    
    def enrich_products_with_specifications(self, products: List[Dict]) -> List[Dict]:
        """
        Reichert Produkte mit detaillierten Spezifikationen an
        """
        enriched = []
        total = len(products)
        
        print(f"\nLade Spezifikationen für {total} Produkte...")
        
        for i, product in enumerate(products):
            article_id = product.get('IDArticolo')
            sku = product.get('Codice', '')
            
            print(f"[{i+1}/{total}] {sku} - {product.get('Desc_en', '')}")
            
            # Hole Spezifikationen
            specs = self.get_product_specifications(article_id)
            
            if specs:
                product['specifications'] = specs
            
            enriched.append(product)
            
            # Höfliche Pause
            time.sleep(0.3)
        
        print("✓ Alle Spezifikationen geladen")
        return enriched
    
    def detect_certification(self, product: Dict) -> str:
        """
        Erkennt die Zertifizierung aus den API-Daten
        """
        # Euro4ECE = ECE-Homologierung
        if product.get('Euro4ECE'):
            return 'ECE'
        # Euro4 = Euro4-Homologierung
        elif product.get('Euro4'):
            return 'Euro4'
        # Wenn keine Homologierung = Racing
        elif not product.get('Omologazione') and not product.get('Euro4ECE'):
            return 'Racing'
        else:
            return ''
    
    def detect_compatibility(self, product: Dict) -> str:
        """
        Erkennt Kompatibilität aus dem Produktnamen
        """
        name = product.get('Desc_en', '').lower()
        
        if 'x-kone' in name:
            return 'X-Kone silencers'
        elif 'thunder' in name:
            return 'Thunder silencers'
        else:
            return ''
    
    def add_product_dependencies(self, products: List[Dict]) -> List[Dict]:
        """
        Fügt Produktabhängigkeiten hinzu
        """
        print("\nAnalysiere Produktabhängigkeiten...")
        
        # Erstelle Mapping nach Produkttyp
        by_type = {}
        for p in products:
            ptype = p.get('Description', 'Unknown')
            if ptype not in by_type:
                by_type[ptype] = []
            by_type[ptype].append(p)
        
        # Definiere Abhängigkeiten basierend auf Kompatibilität
        for product in products:
            sku = product.get('Codice', '')
            name = product.get('Desc_en', '').lower()
            category = product.get('Description', '')
            
            requires = []
            optional = []
            
            # Schalldämpfer benötigen Mittelrohre
            if category == 'Silencers':
                if 'x-kone' in name:
                    # X-Kone Schalldämpfer
                    for p in by_type.get('Mid-pipes', []):
                        if 'x-kone' in p.get('Desc_en', '').lower():
                            requires.append(p.get('Codice'))
                elif 'thunder' in name:
                    # Thunder Schalldämpfer
                    for p in by_type.get('Mid-pipes', []):
                        if 'thunder' in p.get('Desc_en', '').lower():
                            requires.append(p.get('Codice'))
                
                # Kollektoren sind optional
                for p in by_type.get('Collectors', []):
                    optional.append(p.get('Codice'))
            
            product['requires'] = requires
            product['optional'] = optional
        
        print("✓ Produktabhängigkeiten hinzugefügt")
        return products
    
    def export_to_csv(self, products: List[Dict], filename: str = 'arrow_products_api.csv'):
        """
        Exportiert Produkte als CSV für Shopware
        """
        if not products:
            print("Keine Produkte zum Exportieren")
            return
        
        fieldnames = [
            'ordernumber',
            'name',
            'description',
            'supplier',
            'tax',
            'price',
            'active',
            'instock',
            'categories',
            'propertyGroup1',
            'propertyValue1',
            'propertyGroup2',
            'propertyValue2',
            'propertyGroup3',
            'propertyValue3',
            'propertyGroup4',
            'propertyValue4',
            'propertyGroup5',
            'propertyValue5',
            'propertyGroup6',
            'propertyValue6',
            'propertyGroup7',
            'propertyValue7',
            'propertyGroup8',
            'propertyValue8',
            'weight',
            'requires',
            'optional'
        ]
        
        print(f"\nExportiere {len(products)} Produkte nach {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
            writer.writeheader()
            
            for product in products:
                specs = product.get('specifications', {})
                
                # Material aus Spezifikationen
                material_body = specs.get('Desc_Corp_EN', '')
                material_inner = specs.get('Desc_Int_EN', '')
                material = material_body if material_body else material_inner
                
                row = {
                    'ordernumber': product.get('Codice', ''),
                    'name': product.get('Desc_en', ''),
                    'description': product.get('Desc_en', ''),
                    'supplier': 'Arrow',
                    'tax': '19',
                    'price': '',
                    'active': '0' if product.get('Outlet') else '1',
                    'instock': '',
                    'categories': '',
                    'propertyGroup1': 'Produkttyp',
                    'propertyValue1': product.get('Description', ''),
                    'propertyGroup2': 'Material Körper',
                    'propertyValue2': material,
                    'propertyGroup3': 'Material Innen',
                    'propertyValue3': specs.get('Desc_Int_EN', ''),
                    'propertyGroup4': 'Zertifizierung',
                    'propertyValue4': self.detect_certification(product),
                    'propertyGroup5': 'Kompatibel mit',
                    'propertyValue5': self.detect_compatibility(product),
                    'propertyGroup6': 'DB-Killer',
                    'propertyValue6': specs.get('dBKiller', ''),
                    'propertyGroup7': 'Lambda-Sonde',
                    'propertyValue7': specs.get('SondaLambda', ''),
                    'propertyGroup8': 'CO-Sonde',
                    'propertyValue8': specs.get('SondaCO', ''),
                    'weight': specs.get('Peso', ''),
                    'requires': ', '.join(product.get('requires', [])),
                    'optional': ', '.join(product.get('optional', []))
                }
                
                writer.writerow(row)
        
        print(f"✓ CSV-Datei erstellt: {filename}")
    
    def export_to_json(self, products: List[Dict], vehicle_info: Dict, filename: str = 'arrow_products_api.json'):
        """
        Exportiert Produkte als JSON
        """
        print(f"\nExportiere {len(products)} Produkte nach {filename}")
        
        data = {
            'vehicle_info': vehicle_info,
            'products': products,
            'total_products': len(products)
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON-Datei erstellt: {filename}")
    
    def print_summary(self, products: List[Dict]):
        """
        Gibt eine Zusammenfassung aus
        """
        print("\n" + "=" * 60)
        print("ZUSAMMENFASSUNG")
        print("=" * 60)
        
        # Gruppiere nach Kategorie
        by_category = {}
        for product in products:
            cat = product.get('Description', 'Unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(product)
        
        for category, prods in sorted(by_category.items()):
            print(f"\n{category}: {len(prods)} Produkte")
            for p in prods:
                sku = p.get('Codice', '')
                name = p.get('Desc_en', '')
                cert = self.detect_certification(p)
                cert_str = f" [{cert}]" if cert else ""
                
                specs = p.get('specifications', {})
                material = specs.get('Desc_Corp_EN', '')
                mat_str = f" ({material})" if material else ""
                
                weight = specs.get('Peso', '')
                weight_str = f" - {weight}kg" if weight else ""
                
                print(f"  - {sku}: {name}{cert_str}{mat_str}{weight_str}")


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("Arrow.it API Product Data Extractor")
    print("=" * 60)
    
    # Standard-URL
    default_url = "https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024"
    
    if len(sys.argv) > 1:
        vehicle_url = sys.argv[1]
    else:
        vehicle_url = default_url
        print(f"\nVerwendung: python arrow_api_extractor.py [URL]")
        print(f"Standard-URL: {vehicle_url}\n")
    
    extractor = ArrowAPIExtractor()
    
    try:
        # Extrahiere Fahrzeug-ID aus URL
        vehicle_id = extractor.extract_vehicle_id_from_url(vehicle_url)
        
        if not vehicle_id:
            print("✗ Konnte Fahrzeug-ID nicht aus URL extrahieren")
            print("Beispiel-URL: https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024")
            return
        
        print(f"Fahrzeug-ID: {vehicle_id}\n")
        
        # Schritt 1: Hole Produkte
        products = extractor.get_products(vehicle_id)
        
        if not products:
            print("✗ Keine Produkte gefunden!")
            return
        
        # Schritt 2: Hole Fahrzeuginfo
        vehicle_info = extractor.get_vehicle_info(vehicle_id)
        
        # Schritt 3: Frage ob Spezifikationen geladen werden sollen
        print("\n" + "=" * 60)
        print("Möchten Sie detaillierte Spezifikationen laden?")
        print("(Dies kann einige Zeit dauern)")
        response = input("Spezifikationen laden? (j/n): ").lower()
        
        if response in ['j', 'y', 'ja', 'yes']:
            products = extractor.enrich_products_with_specifications(products)
        
        # Schritt 4: Produktabhängigkeiten
        products = extractor.add_product_dependencies(products)
        
        # Schritt 5: Zusammenfassung
        extractor.print_summary(products)
        
        # Schritt 6: Export
        print("\n" + "=" * 60)
        csv_filename = f"arrow_vehicle_{vehicle_id}_api.csv"
        json_filename = f"arrow_vehicle_{vehicle_id}_api.json"
        
        extractor.export_to_csv(products, csv_filename)
        extractor.export_to_json(products, vehicle_info, json_filename)
        
        print("\n" + "=" * 60)
        print("Extraktion abgeschlossen!")
        print("=" * 60)
        print(f"\nDateien erstellt:")
        print(f"  - {csv_filename} (für Shopware Import)")
        print(f"  - {json_filename} (für weitere Verarbeitung)")
        print(f"\n📋 NÄCHSTE SCHRITTE:")
        print(f"  1. CSV-Datei öffnen und Preise eintragen")
        print(f"  2. Lagerbestände eintragen")
        print(f"  3. Bilder manuell zuweisen (Artikelnummer als Bildname)")
        print(f"  4. Produktabhängigkeiten in Shopware konfigurieren")
        print(f"  5. CSV in Shopware importieren")
        
    except KeyboardInterrupt:
        print("\n\n✗ Abgebrochen durch Benutzer")
    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
