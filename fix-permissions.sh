#!/bin/bash

# Arrow Scraper - Berechtigungen korrigieren
# Für Synology DSM

set -e

echo "🔧 Arrow Scraper - Berechtigungen korrigieren"
echo "=============================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktionen
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe ob als Root ausgeführt
if [ "$EUID" -ne 0 ]; then
    log_error "Bitte als Root oder mit sudo ausführen"
    exit 1
fi

# Basis-Pfad
BASE_PATH="/volume1/docker/arrow_scraper"

log_info "Korrigiere Berechtigungen für: $BASE_PATH"

# Container stoppen
log_info "Stoppe Container..."
docker-compose -f "$BASE_PATH/docker-compose.yml" down 2>/dev/null || true

# Berechtigungen setzen
log_info "Setze Ordnerberechtigungen..."
chmod -R 755 "$BASE_PATH/data"
chmod -R 755 "$BASE_PATH/data/exports"
chmod -R 755 "$BASE_PATH/data/logs"

# Besitzer setzen (falls nötig)
log_info "Setze Besitzer..."
chown -R 1000:1000 "$BASE_PATH/data" 2>/dev/null || true

# Container neu starten
log_info "Starte Container neu..."
cd "$BASE_PATH"
docker-compose up -d --build

# Status prüfen
sleep 10
if docker ps | grep -q "arrow-scraper"; then
    log_info "✅ Container erfolgreich neu gestartet!"
    log_info "🌐 Web-Interface: http://$(hostname -I | awk '{print $1}'):8080"
else
    log_error "❌ Container konnte nicht gestartet werden"
    log_error "Logs anzeigen mit: docker logs arrow-scraper"
    exit 1
fi

# Test-Schreibzugriff
log_info "Teste Schreibzugriff..."
docker exec arrow-scraper touch /app/exports/test_write.txt 2>/dev/null && \
    docker exec arrow-scraper rm /app/exports/test_write.txt 2>/dev/null && \
    log_info "✅ Schreibzugriff funktioniert!" || \
    log_error "❌ Schreibzugriff funktioniert nicht"

echo ""
log_info "🎉 Berechtigungen korrigiert!"
echo ""
echo "Nützliche Befehle:"
echo "  Container-Logs:    docker logs arrow-scraper"
echo "  Container-Status:  docker ps | grep arrow-scraper"
echo "  Ordner-Inhalt:     ls -la $BASE_PATH/data/exports"
echo ""
