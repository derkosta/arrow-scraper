#!/bin/bash
# Startskript für Arrow Scraper Webportal

echo "🚀 Starte Arrow.it Produktdaten-Extraktor Webportal..."

# Prüfe ob Docker installiert ist
if ! command -v docker &> /dev/null; then
    echo "❌ Docker ist nicht installiert!"
    exit 1
fi

# Prüfe ob Docker Compose installiert ist
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose ist nicht installiert!"
    exit 1
fi

# Erstelle exports Verzeichnis falls nicht vorhanden
mkdir -p exports

# Baue und starte Container
echo "📦 Baue Docker Container..."
docker-compose build

echo "▶️  Starte Container..."
docker-compose up -d

echo ""
echo "✅ Webportal wurde gestartet!"
echo ""
echo "🌐 Öffnen Sie in Ihrem Browser:"
echo "   http://localhost:5000"
echo ""
echo "📊 Zum Stoppen verwenden Sie:"
echo "   docker-compose down"
echo ""
echo "📋 Container Status:"
docker-compose ps
