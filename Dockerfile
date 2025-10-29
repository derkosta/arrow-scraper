FROM python:3.11-slim

# Metadaten
LABEL maintainer="Arrow Scraper"
LABEL description="Arrow.it Produktdaten-Extraktor"
LABEL version="1.0.0"

# Arbeitsverzeichnis
WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY app.py .
COPY templates/ ./templates/

# Verzeichnisse erstellen
RUN mkdir -p exports logs data

# Berechtigungen für gemountete Volumes setzen
RUN chmod 755 exports logs data

# Port exponieren
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Starte Gunicorn mit optimierten Einstellungen
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
