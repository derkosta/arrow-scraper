#!/usr/bin/env python3
"""
Arrow.it Product Data Extractor
Extrahiert Produktdaten von arrow.it und bereitet sie für Shopware 5/6 auf.
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import sys
from urllib.parse import urljoin

class ArrowProductExtractor:
    def __init__(self, base_url="https://www.arrow.it"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def extract_vehicle_products(self, vehicle_url):
        """
        Extrahiert alle Produkte für ein bestimmtes Fahrzeug
        """
        print(f"Lade Seite: {vehicle_url}")
        response = self.session.get(vehicle_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Fahrzeuginfo extrahieren
        vehicle_info = self._extract_vehicle_info(soup)
        print(f"Fahrzeug: {vehicle_info['model']} (Type: {vehicle_info['vehicle_type']})")
        
        # Produkte extrahieren
        products = []
        
        # Finde alle Produktkategorien
        product_sections = soup.find_all('div', class_='list-products')
        
        for section in product_sections:
            # Kategorie-Header finden
            category_header = section.find_previous_sibling(['h3', 'h4', 'div'])
            category = self._clean_text(category_header.text) if category_header else 'Unknown'
            
            # Alle Produkte in dieser Kategorie
            items = section.find_all('div', class_='list-item')
            
            for item in items:
                product = self._extract_product_basic(item, category, vehicle_info)
                if product:
                    products.append(product)
        
        print(f"Gefunden: {len(products)} Produkte")
        return products, vehicle_info
    
    def _extract_vehicle_info(self, soup):
        """Extrahiert Fahrzeuginformationen"""
        vehicle_info = {
            'model': '',
            'vehicle_type': '',
            'years': ''
        }
        
        # Modell
        model_elem = soup.find('h1')
        if model_elem:
            vehicle_info['model'] = self._clean_text(model_elem.text)
        
        # Vehicle Type
        type_elem = soup.find('h5')
        if type_elem and 'Vehicle type:' in type_elem.text:
            vehicle_info['vehicle_type'] = type_elem.text.replace('Vehicle type:', '').strip()
        
        return vehicle_info
    
    def _extract_product_basic(self, item, category, vehicle_info):
        """Extrahiert Basis-Produktinformationen"""
        product = {
            'sku': '',
            'name': '',
            'category': category,
            'vehicle_model': vehicle_info['model'],
            'vehicle_type': vehicle_info['vehicle_type'],
            'certification': '',
            'specification_url': ''
        }
        
        # SKU (Artikelnummer)
        code_elem = item.find('div', class_='code')
        if code_elem:
            product['sku'] = self._clean_text(code_elem.text)
        
        # Produktname
        name_elem = item.find('div', class_='name')
        if name_elem:
            product['name'] = self._clean_text(name_elem.text)
        
        # Zertifizierung (ECE oder Racing)
        cert_elem = item.find('span', class_=['homologation', 'racing'])
        if cert_elem:
            if 'racing' in cert_elem.get('class', []):
                product['certification'] = 'Racing'
            else:
                product['certification'] = 'ECE'
        
        # Specification Button URL
        spec_button = item.find('a', class_='specification')
        if spec_button and spec_button.get('data-url'):
            product['specification_url'] = spec_button['data-url']
        
        return product if product['sku'] else None
    
    def extract_product_specifications(self, spec_url):
        """
        Extrahiert detaillierte Spezifikationen für ein Produkt
        """
        if not spec_url:
            return {}
        
        full_url = urljoin(self.base_url, spec_url)
        print(f"  Lade Spezifikationen: {spec_url}")
        
        try:
            response = self.session.get(full_url)
            response.raise_for_status()
            
            # Die Antwort könnte JSON oder HTML sein
            try:
                data = response.json()
                return self._parse_specification_json(data)
            except json.JSONDecodeError:
                soup = BeautifulSoup(response.content, 'html.parser')
                return self._parse_specification_html(soup)
        except Exception as e:
            print(f"  Fehler beim Laden der Spezifikationen: {e}")
            return {}
    
    def _parse_specification_html(self, soup):
        """Parst Spezifikationen aus HTML"""
        specs = {}
        
        # Suche nach Tabellen mit Features/Values
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) == 2:
                feature = self._clean_text(cells[0].text)
                value = self._clean_text(cells[1].text)
                specs[feature] = value
        
        return specs
    
    def _parse_specification_json(self, data):
        """Parst Spezifikationen aus JSON"""
        # Implementierung abhängig von der JSON-Struktur
        return data
    
    def enrich_products_with_specifications(self, products, max_products=None):
        """
        Reichert Produkte mit detaillierten Spezifikationen an
        """
        enriched = []
        total = len(products) if max_products is None else min(len(products), max_products)
        
        for i, product in enumerate(products[:total]):
            print(f"[{i+1}/{total}] {product['sku']} - {product['name']}")
            
            if product.get('specification_url'):
                specs = self.extract_product_specifications(product['specification_url'])
                product['specifications'] = specs
                
                # Wichtige Spezifikationen als separate Felder
                product['material'] = specs.get('Mid-pipe material', specs.get('Material', ''))
                product['weight_kg'] = specs.get('Weight (Kg)', '')
                product['db_killer'] = specs.get('Db Killer', '')
                product['co_sensor'] = specs.get('CO sensor plug', '')
                product['oxygen_sensor'] = specs.get('Oxygen sensor plug', '')
            
            enriched.append(product)
            time.sleep(0.5)  # Höfliche Pause zwischen Anfragen
        
        return enriched
    
    def export_to_csv(self, products, filename='arrow_products.csv'):
        """
        Exportiert Produkte als CSV für Shopware
        """
        if not products:
            print("Keine Produkte zum Exportieren")
            return
        
        # Alle möglichen Felder sammeln
        all_fields = set()
        for product in products:
            all_fields.update(product.keys())
            if 'specifications' in product:
                for spec_key in product['specifications'].keys():
                    all_fields.add(f"spec_{spec_key.replace(' ', '_').replace('(', '').replace(')', '')}")
        
        # Entferne 'specifications' aus den Hauptfeldern
        all_fields.discard('specifications')
        all_fields.discard('specification_url')
        
        # Sortiere Felder für bessere Lesbarkeit
        base_fields = ['sku', 'name', 'category', 'vehicle_model', 'vehicle_type', 
                       'certification', 'material', 'weight_kg', 'db_killer', 
                       'co_sensor', 'oxygen_sensor']
        
        ordered_fields = [f for f in base_fields if f in all_fields]
        spec_fields = sorted([f for f in all_fields if f.startswith('spec_')])
        other_fields = sorted([f for f in all_fields if f not in ordered_fields and not f.startswith('spec_')])
        
        fieldnames = ordered_fields + other_fields + spec_fields
        
        print(f"\nExportiere {len(products)} Produkte nach {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            
            for product in products:
                row = {}
                
                # Basis-Felder
                for field in fieldnames:
                    if field.startswith('spec_'):
                        # Spezifikationen
                        spec_name = field.replace('spec_', '').replace('_', ' ')
                        if 'specifications' in product:
                            # Suche nach dem passenden Schlüssel (case-insensitive)
                            for key, value in product['specifications'].items():
                                if key.replace(' ', '_').replace('(', '').replace(')', '').lower() == spec_name.lower():
                                    row[field] = value
                                    break
                        if field not in row:
                            row[field] = ''
                    else:
                        row[field] = product.get(field, '')
                
                writer.writerow(row)
        
        print(f"✓ CSV-Datei erstellt: {filename}")
    
    def export_to_json(self, products, filename='arrow_products.json'):
        """
        Exportiert Produkte als JSON für weitere Verarbeitung
        """
        print(f"\nExportiere {len(products)} Produkte nach {filename}")
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON-Datei erstellt: {filename}")
    
    @staticmethod
    def _clean_text(text):
        """Bereinigt Text von Whitespace und Sonderzeichen"""
        return ' '.join(text.strip().split())


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("Arrow.it Product Data Extractor")
    print("=" * 60)
    
    # Beispiel-URL
    default_url = "https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024"
    
    if len(sys.argv) > 1:
        vehicle_url = sys.argv[1]
    else:
        vehicle_url = default_url
        print(f"\nVerwendung: python arrow_extractor.py [URL]")
        print(f"Standard-URL: {vehicle_url}\n")
    
    extractor = ArrowProductExtractor()
    
    try:
        # Schritt 1: Basis-Produktdaten extrahieren
        products, vehicle_info = extractor.extract_vehicle_products(vehicle_url)
        
        if not products:
            print("Keine Produkte gefunden!")
            return
        
        # Schritt 2: Frage ob Spezifikationen geladen werden sollen
        print("\n" + "=" * 60)
        print("Möchten Sie detaillierte Spezifikationen laden?")
        print("(Dies kann einige Zeit dauern)")
        response = input("Spezifikationen laden? (j/n): ").lower()
        
        if response in ['j', 'y', 'ja', 'yes']:
            print("\nLade Spezifikationen...")
            products = extractor.enrich_products_with_specifications(products)
        
        # Schritt 3: Export
        print("\n" + "=" * 60)
        vehicle_slug = vehicle_info['model'].replace(' ', '_').replace('/', '-')
        csv_filename = f"arrow_{vehicle_slug}.csv"
        json_filename = f"arrow_{vehicle_slug}.json"
        
        extractor.export_to_csv(products, csv_filename)
        extractor.export_to_json(products, json_filename)
        
        print("\n" + "=" * 60)
        print("Extraktion abgeschlossen!")
        print("=" * 60)
        print(f"\nDateien erstellt:")
        print(f"  - {csv_filename} (für Shopware Import)")
        print(f"  - {json_filename} (für weitere Verarbeitung)")
        
    except Exception as e:
        print(f"\nFehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
