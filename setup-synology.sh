#!/bin/bash

# Arrow Scraper - Synology DSM Setup Script
# Automatische Einrichtung für Synology NAS

set -e

echo "🚀 Arrow Scraper - Synology DSM Setup"
echo "======================================"

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
PROJECT_NAME="arrow-scraper"

log_info "Setup für Pfad: $BASE_PATH"

# 1. Ordnerstruktur erstellen
log_info "Erstelle Ordnerstruktur..."
mkdir -p "$BASE_PATH/data/exports"
mkdir -p "$BASE_PATH/data/logs"
mkdir -p "$BASE_PATH/data"

# 2. Berechtigungen setzen
log_info "Setze Berechtigungen..."
chmod 755 "$BASE_PATH"
chmod 755 "$BASE_PATH/data"
chmod 755 "$BASE_PATH/data/exports"
chmod 755 "$BASE_PATH/data/logs"

# 3. .env-Datei erstellen falls nicht vorhanden
if [ ! -f "$BASE_PATH/.env" ]; then
    log_info "Erstelle .env-Datei..."
    if [ -f "$BASE_PATH/env.example" ]; then
        cp "$BASE_PATH/env.example" "$BASE_PATH/.env"
        log_info ".env-Datei aus env.example erstellt"
    else
        cat > "$BASE_PATH/.env" << EOF
# Arrow Scraper Environment Configuration
# Synology DSM Docker Stack Configuration

# Application Settings
FLASK_ENV=production
DEBUG=false
WEB_HOST=0.0.0.0
WEB_PORT=5000

# Database Configuration
DATABASE_PATH=/app/data/arrow_scraper.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/arrow_scraper.log

# Timezone
TZ=Europe/Berlin

# Arrow.it API Configuration
ARROW_BASE_URL=https://www.arrow.it
ARROW_API_BASE=https://www.arrow.it/api/en
REQUEST_TIMEOUT=30
REQUEST_DELAY=0.3

# Export Configuration
EXPORT_FORMAT=csv
EXPORT_DELIMITER=;
EXPORT_ENCODING=utf-8

# Security
SECRET_KEY=arrow_scraper_secret_key_$(date +%s)

# Performance Settings
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=300
GUNICORN_BIND=0.0.0.0:5000

# Health Check
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10
HEALTH_CHECK_RETRIES=3
HEALTH_CHECK_START_PERIOD=40
EOF
    log_info ".env-Datei erstellt"
else
    log_warn ".env-Datei existiert bereits"
fi

# 4. Docker Compose prüfen
if [ ! -f "$BASE_PATH/docker-compose.yml" ]; then
    log_error "docker-compose.yml nicht gefunden in $BASE_PATH"
    log_error "Bitte Repository in $BASE_PATH klonen"
    exit 1
fi

# 5. Port 5060 prüfen
if netstat -tulpn 2>/dev/null | grep -q ":5060 "; then
    log_warn "Port 5060 ist bereits in Verwendung"
    log_warn "Bitte anderen Port in docker-compose.yml konfigurieren"
fi

# 6. Docker Container stoppen falls läuft
log_info "Stoppe existierende Container..."
docker-compose -f "$BASE_PATH/docker-compose.yml" down 2>/dev/null || true

# 7. Container bauen und starten
log_info "Baue und starte Container..."
cd "$BASE_PATH"
docker-compose up -d --build

# 8. Status prüfen
sleep 10
if docker ps | grep -q "$PROJECT_NAME"; then
    log_info "✅ Container erfolgreich gestartet!"
    log_info "🌐 Web-Interface: http://$(hostname -I | awk '{print $1}'):5060"
    log_info "🔍 Health Check: http://$(hostname -I | awk '{print $1}'):5060/api/health"
else
    log_error "❌ Container konnte nicht gestartet werden"
    log_error "Logs anzeigen mit: docker logs $PROJECT_NAME"
    exit 1
fi

# 9. Logs anzeigen
log_info "Container-Logs (letzte 20 Zeilen):"
docker logs --tail 20 "$PROJECT_NAME"

echo ""
log_info "🎉 Setup abgeschlossen!"
echo ""
echo "Nützliche Befehle:"
echo "  Logs anzeigen:    docker logs $PROJECT_NAME"
echo "  Container stoppen: docker-compose -f $BASE_PATH/docker-compose.yml down"
echo "  Container starten: docker-compose -f $BASE_PATH/docker-compose.yml up -d"
echo "  Status prüfen:    docker ps | grep $PROJECT_NAME"
echo ""
echo "📁 Daten werden gespeichert in:"
echo "  Exports: $BASE_PATH/data/exports"
echo "  Logs:    $BASE_PATH/data/logs"
echo ""
