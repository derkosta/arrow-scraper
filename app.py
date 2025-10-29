#!/usr/bin/env python3
"""
Arrow.it Web Scraper Portal
Webportal zum Extrahieren, Anzeigen und Bearbeiten von Produktdaten von Arrow.it
"""

import os
import re
import requests
import csv
import json
import time
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from typing import List, Dict, Optional
from datetime import datetime
import io

app = Flask(__name__)
CORS(app)

# Konfiguration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')
os.makedirs(EXPORTS_DIR, exist_ok=True)


class ArrowAPIExtractor:
    """Arrow API Extraktor"""
    
    def __init__(self):
        self.base_url = "https://www.arrow.it"
        self.api_base = f"{self.base_url}/api/en"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
    def extract_vehicle_id_from_url(self, url: str) -> Optional[int]:
        """Extrahiert die Fahrzeug-ID aus der URL"""
        match = re.search(r'/assembled/(\d+)/', url)
        if match:
            return int(match.group(1))
        return None
    
    def get_products(self, vehicle_id: int) -> List[Dict]:
        """Holt alle Produkte für ein Fahrzeug über die API"""
        url = f"{self.api_base}/montaggi/{vehicle_id}"
        
        try:
            response = self.session.post(url, data={'UserId': '', 'Brand': 'Arrow'})
            response.raise_for_status()
            products = response.json()
            return products if isinstance(products, list) else []
        except Exception as e:
            print(f"Fehler beim Laden der Produkte: {e}")
            return []
    
    def get_product_specifications(self, article_id: int) -> Optional[Dict]:
        """Holt detaillierte Spezifikationen für ein Produkt"""
        url = f"{self.api_base}/montaggi/specifiche/{article_id}"
        
        try:
            response = self.session.get(url, params={'UserId': '', 'Brand': 'Arrow'})
            response.raise_for_status()
            specs = response.json()
            if specs and len(specs) > 0:
                return specs[0]
            return None
        except Exception as e:
            print(f"Fehler beim Laden der Spezifikationen: {e}")
            return None
    
    def enrich_products_with_specifications(self, products: List[Dict]) -> List[Dict]:
        """Reichert Produkte mit detaillierten Spezifikationen an"""
        enriched = []
        total = len(products)
        
        for i, product in enumerate(products):
            article_id = product.get('IDArticolo')
            if article_id:
                specs = self.get_product_specifications(article_id)
                if specs:
                    product['specifications'] = specs
            enriched.append(product)
            time.sleep(0.3)  # Höfliche Pause
        
        return enriched
    
    def format_product_data(self, products: List[Dict]) -> List[Dict]:
        """Formatiert Produktdaten für die Anzeige"""
        formatted_products = []
        
        for product in products:
            specs = product.get('specifications', {})
            
            # Bilder-URLs extrahieren
            images = []
            if product.get('Immagine'):
                images.append(f"{self.base_url}{product['Immagine']}")
            
            formatted_product = {
                'id': product.get('IDArticolo', ''),
                'code': product.get('Codice', ''),
                'name': product.get('Desc_en', ''),
                'description': product.get('Desc_en', ''),
                'category': product.get('Description', ''),
                'price': product.get('Prezzo', ''),
                'images': images,
                'specifications': {
                    'material_body': specs.get('Desc_Corp_EN', ''),
                    'material_inner': specs.get('Desc_Int_EN', ''),
                    'weight': specs.get('Peso', ''),
                    'db_killer': specs.get('dBKiller', ''),
                    'lambda_sensor': specs.get('SondaLambda', ''),
                    'co_sensor': specs.get('SondaCO', ''),
                    'certification': self.detect_certification(product),
                    'compatibility': self.detect_compatibility(product)
                },
                'outlet': product.get('Outlet', False),
                'raw_data': product  # Originaldaten für Bearbeitung
            }
            
            formatted_products.append(formatted_product)
        
        return formatted_products
    
    def detect_certification(self, product: Dict) -> str:
        """Erkennt die Zertifizierung aus den API-Daten"""
        if product.get('Euro4ECE'):
            return 'ECE'
        elif product.get('Euro4'):
            return 'Euro4'
        elif not product.get('Omologazione') and not product.get('Euro4ECE'):
            return 'Racing'
        else:
            return ''
    
    def detect_compatibility(self, product: Dict) -> str:
        """Erkennt Kompatibilität aus dem Produktnamen"""
        name = product.get('Desc_en', '').lower()
        if 'x-kone' in name:
            return 'X-Kone silencers'
        elif 'thunder' in name:
            return 'Thunder silencers'
        else:
            return ''
    
    def export_to_csv(self, products: List[Dict], filename: str) -> str:
        """Exportiert bearbeitete Produkte als CSV"""
        fieldnames = [
            'code', 'name', 'description', 'category', 'price', 'active',
            'material_body', 'material_inner', 'weight', 'certification',
            'compatibility', 'db_killer', 'lambda_sensor', 'co_sensor'
        ]
        
        filepath = os.path.join(EXPORTS_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', extrasaction='ignore')
            writer.writeheader()
            
            for product in products:
                specs = product.get('specifications', {})
                
                row = {
                    'code': product.get('code', ''),
                    'name': product.get('name', ''),
                    'description': product.get('description', ''),
                    'category': product.get('category', ''),
                    'price': product.get('price', ''),
                    'active': '0' if product.get('outlet') else '1',
                    'material_body': specs.get('material_body', ''),
                    'material_inner': specs.get('material_inner', ''),
                    'weight': specs.get('weight', ''),
                    'certification': specs.get('certification', ''),
                    'compatibility': specs.get('compatibility', ''),
                    'db_killer': specs.get('db_killer', ''),
                    'lambda_sensor': specs.get('lambda_sensor', ''),
                    'co_sensor': specs.get('co_sensor', '')
                }
                
                writer.writerow(row)
        
        return filepath


extractor = ArrowAPIExtractor()


@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def scan_products():
    """API-Endpunkt zum Scannen von Produktdaten"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL ist erforderlich'}), 400
        
        # Validiere URL
        if 'arrow.it' not in url or '/assembled/' not in url:
            return jsonify({'error': 'Ungültige Arrow.it URL'}), 400
        
        # Extrahiere Fahrzeug-ID
        vehicle_id = extractor.extract_vehicle_id_from_url(url)
        if not vehicle_id:
            return jsonify({'error': 'Konnte Fahrzeug-ID nicht aus URL extrahieren'}), 400
        
        # Hole Produkte
        products = extractor.get_products(vehicle_id)
        if not products:
            return jsonify({'error': 'Keine Produkte gefunden'}), 404
        
        # Frage ob Spezifikationen geladen werden sollen
        load_specs = data.get('load_specifications', True)
        
        if load_specs:
            products = extractor.enrich_products_with_specifications(products)
        
        # Formatiere für Anzeige
        formatted_products = extractor.format_product_data(products)
        
        return jsonify({
            'success': True,
            'vehicle_id': vehicle_id,
            'url': url,
            'total_products': len(formatted_products),
            'products': formatted_products
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_products():
    """API-Endpunkt zum Exportieren bearbeiteter Produktdaten"""
    try:
        data = request.get_json()
        products = data.get('products', [])
        
        if not products:
            return jsonify({'error': 'Keine Produktdaten zum Exportieren'}), 400
        
        # Erstelle CSV-Datei
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'arrow_products_{timestamp}.csv'
        filepath = extractor.export_to_csv(products, filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'download_url': f'/api/download/{filename}',
            'total_products': len(products)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """Download-Endpunkt für CSV-Dateien"""
    try:
        filepath = os.path.join(EXPORTS_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Datei nicht gefunden'}), 404
        
        return send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health Check Endpunkt"""
    return jsonify({'status': 'ok', 'version': '2.0.0'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)