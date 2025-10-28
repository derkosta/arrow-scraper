#!/usr/bin/env python3
"""
Arrow.it Product Data Extractor v2
Extrahiert Produktdaten von arrow.it mit Selenium (für dynamisch geladene Inhalte)
und bereitet sie für Shopware 5/6 auf.
"""

import csv
import json
import time
import sys
import re
from urllib.parse import urljoin, urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError:
    print("Selenium nicht installiert. Installiere mit: pip3 install selenium")
    sys.exit(1)


class ArrowProductExtractorV2:
    def __init__(self):
        self.driver = None
        self.base_url = "https://www.arrow.it"
        
    def setup_driver(self, headless=True):
        """Initialisiert den Selenium WebDriver"""
        print("Initialisiere Browser...")
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
    def close_driver(self):
        """Schließt den Browser"""
        if self.driver:
            self.driver.quit()
    
    def extract_vehicle_products(self, vehicle_url):
        """
        Extrahiert alle Produkte für ein bestimmtes Fahrzeug
        """
        print(f"\nLade Seite: {vehicle_url}")
        self.driver.get(vehicle_url)
        
        # Warte bis die Seite geladen ist
        time.sleep(3)
        
        # Fahrzeuginfo extrahieren
        vehicle_info = self._extract_vehicle_info()
        print(f"Fahrzeug: {vehicle_info['model']} (Type: {vehicle_info['vehicle_type']})")
        
        # Klicke auf den "Products" Tab
        try:
            products_tab = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Products') or contains(@href, '#prodotti')]")
            products_tab.click()
            time.sleep(2)
        except NoSuchElementException:
            print("Products Tab nicht gefunden, versuche direkt zu scrapen...")
        
        # Produkte extrahieren
        products = []
        
        # Methode 1: Aus dem Markdown-Text extrahieren (bereits vorhanden)
        products_from_text = self._extract_from_page_text()
        
        # Methode 2: Aus dem DOM extrahieren
        products_from_dom = self._extract_from_dom(vehicle_info)
        
        # Kombiniere beide Methoden
        products = products_from_dom if products_from_dom else products_from_text
        
        print(f"Gefunden: {len(products)} Produkte")
        return products, vehicle_info
    
    def _extract_vehicle_info(self):
        """Extrahiert Fahrzeuginformationen"""
        vehicle_info = {
            'model': '',
            'vehicle_type': '',
            'years': ''
        }
        
        try:
            # Modell
            model_elem = self.driver.find_element(By.TAG_NAME, 'h1')
            vehicle_info['model'] = model_elem.text.strip()
            
            # Vehicle Type
            type_elem = self.driver.find_element(By.XPATH, "//h5[contains(text(), 'Vehicle type')]")
            vehicle_info['vehicle_type'] = type_elem.text.replace('Vehicle type:', '').strip()
        except NoSuchElementException:
            pass
        
        return vehicle_info
    
    def _extract_from_page_text(self):
        """Extrahiert Produkte aus dem Seitentext (Fallback-Methode)"""
        products = []
        
        # Hole den gesamten Seitentext
        page_text = self.driver.find_element(By.TAG_NAME, 'body').text
        
        # Definiere die Kategorien
        categories = {
            'Silencers': [],
            'Mid-pipes': [],
            'Collectors': []
        }
        
        current_category = None
        
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Erkenne Kategorien
            if line in categories:
                current_category = line
                continue
            
            # Erkenne Artikelnummern (Format: 72528AK, 72177PD, etc.)
            if re.match(r'^72\d{3,}[A-Z]{1,3}$', line):
                sku = line
                # Nächste Zeile ist normalerweise der Name
                name = ''
                if i + 1 < len(lines):
                    name = lines[i + 1].strip()
                
                # Erkenne Zertifizierung aus dem Namen oder Context
                certification = ''
                if 'racing' in name.lower():
                    certification = 'Racing'
                elif 'homologated' in name.lower() or 'catalytic' in name.lower():
                    certification = 'ECE'
                
                products.append({
                    'sku': sku,
                    'name': name,
                    'category': current_category or 'Unknown',
                    'certification': certification
                })
        
        return products
    
    def _extract_from_dom(self, vehicle_info):
        """Extrahiert Produkte aus dem DOM"""
        products = []
        
        try:
            # Warte auf Produktcontainer
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "ElencoProdotti"))
            )
            
            # Finde alle Produktkategorien
            categories = self.driver.find_elements(By.CSS_SELECTOR, ".list-products, [class*='product-list']")
            
            for category_elem in categories:
                # Finde Kategorie-Header
                try:
                    category_header = category_elem.find_element(By.XPATH, "./preceding-sibling::*[1]")
                    category = category_header.text.strip()
                except:
                    category = "Unknown"
                
                # Finde alle Produkte in dieser Kategorie
                items = category_elem.find_elements(By.CSS_SELECTOR, ".list-item, [class*='item']")
                
                for item in items:
                    try:
                        # SKU
                        sku_elem = item.find_element(By.CSS_SELECTOR, ".code, [class*='code']")
                        sku = sku_elem.text.strip()
                        
                        # Name
                        name_elem = item.find_element(By.CSS_SELECTOR, ".name, [class*='name']")
                        name = name_elem.text.strip()
                        
                        # Zertifizierung
                        certification = ''
                        try:
                            cert_elem = item.find_element(By.CSS_SELECTOR, ".racing, .homologation, [class*='cert']")
                            cert_class = cert_elem.get_attribute('class')
                            if 'racing' in cert_class.lower():
                                certification = 'Racing'
                            else:
                                certification = 'ECE'
                        except:
                            pass
                        
                        # Specification URL
                        spec_url = ''
                        try:
                            spec_button = item.find_element(By.CSS_SELECTOR, "a.specification, [class*='specification']")
                            spec_url = spec_button.get_attribute('data-url') or spec_button.get_attribute('href')
                        except:
                            pass
                        
                        products.append({
                            'sku': sku,
                            'name': name,
                            'category': category,
                            'vehicle_model': vehicle_info['model'],
                            'vehicle_type': vehicle_info['vehicle_type'],
                            'certification': certification,
                            'specification_url': spec_url
                        })
                    except Exception as e:
                        continue
        except TimeoutException:
            print("Timeout beim Warten auf Produktliste, verwende Text-Extraktion...")
            return []
        
        return products
    
    def extract_product_specifications(self, product):
        """
        Extrahiert detaillierte Spezifikationen für ein Produkt
        """
        spec_url = product.get('specification_url', '')
        if not spec_url:
            return {}
        
        # Klicke auf Specification Button
        try:
            # Finde das Produkt im DOM
            sku = product['sku']
            spec_buttons = self.driver.find_elements(By.CSS_SELECTOR, "a.specification")
            
            for button in spec_buttons:
                parent = button.find_element(By.XPATH, "./ancestor::*[contains(@class, 'item')]")
                if sku in parent.text:
                    print(f"  Lade Spezifikationen für {sku}...")
                    button.click()
                    time.sleep(2)
                    
                    # Extrahiere Spezifikationen aus dem Modal
                    specs = self._extract_specs_from_modal()
                    
                    # Schließe Modal
                    try:
                        close_button = self.driver.find_element(By.CSS_SELECTOR, ".modal .close, button[aria-label='Close']")
                        close_button.click()
                        time.sleep(1)
                    except:
                        pass
                    
                    return specs
        except Exception as e:
            print(f"  Fehler beim Laden der Spezifikationen: {e}")
        
        return {}
    
    def _extract_specs_from_modal(self):
        """Extrahiert Spezifikationen aus dem Modal-Dialog"""
        specs = {}
        
        try:
            # Warte auf Modal
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".modal, [class*='popup']"))
            )
            
            # Finde Tabelle mit Spezifikationen
            rows = self.driver.find_elements(By.CSS_SELECTOR, ".modal tr, [class*='popup'] tr")
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 2:
                    feature = cells[0].text.strip()
                    value = cells[1].text.strip()
                    if feature and value:
                        specs[feature] = value
        except:
            pass
        
        return specs
    
    def enrich_products_with_specifications(self, products, max_products=None):
        """
        Reichert Produkte mit detaillierten Spezifikationen an
        """
        enriched = []
        total = len(products) if max_products is None else min(len(products), max_products)
        
        for i, product in enumerate(products[:total]):
            print(f"[{i+1}/{total}] {product['sku']} - {product['name']}")
            
            specs = self.extract_product_specifications(product)
            if specs:
                product['specifications'] = specs
                
                # Wichtige Spezifikationen als separate Felder
                product['material'] = specs.get('Mid-pipe material', specs.get('Material', ''))
                product['weight_kg'] = specs.get('Weight (Kg)', '')
                product['db_killer'] = specs.get('Db Killer', '')
                product['co_sensor'] = specs.get('CO sensor plug', '')
                product['oxygen_sensor'] = specs.get('Oxygen sensor plug', '')
            
            enriched.append(product)
        
        return enriched
    
    def export_to_csv(self, products, filename='arrow_products.csv'):
        """
        Exportiert Produkte als CSV für Shopware
        """
        if not products:
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
            'propertyGroup1',  # Kategorie (Silencers/Mid-pipes/Collectors)
            'propertyValue1',
            'propertyGroup2',  # Material
            'propertyValue2',
            'propertyGroup3',  # Zertifizierung
            'propertyValue3',
            'propertyGroup4',  # Fahrzeugtyp
            'propertyValue4',
            'weight',
            'db_killer',
            'co_sensor',
            'oxygen_sensor'
        ]
        
        print(f"\nExportiere {len(products)} Produkte nach {filename}")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
            writer.writeheader()
            
            for product in products:
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
                    'weight': product.get('weight_kg', ''),
                    'db_killer': product.get('db_killer', ''),
                    'co_sensor': product.get('co_sensor', ''),
                    'oxygen_sensor': product.get('oxygen_sensor', '')
                }
                
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


def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("Arrow.it Product Data Extractor v2 (Selenium)")
    print("=" * 60)
    
    # Beispiel-URL
    default_url = "https://www.arrow.it/en/assembled/1749/Honda-CRF-300-L-2021-2024"
    
    if len(sys.argv) > 1:
        vehicle_url = sys.argv[1]
    else:
        vehicle_url = default_url
        print(f"\nVerwendung: python arrow_extractor_v2.py [URL]")
        print(f"Standard-URL: {vehicle_url}\n")
    
    extractor = ArrowProductExtractorV2()
    
    try:
        # Setup Browser
        extractor.setup_driver(headless=True)
        
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
        print(f"\nHinweise:")
        print(f"  - Preise müssen manuell eingepflegt werden")
        print(f"  - Lagerbestände müssen manuell eingepflegt werden")
        print(f"  - Bilder müssen manuell zugewiesen werden")
        print(f"  - Produktabhängigkeiten prüfen (siehe JSON-Datei)")
        
    except Exception as e:
        print(f"\nFehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        extractor.close_driver()


if __name__ == "__main__":
    main()
