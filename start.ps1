# Startskript für Arrow Scraper Webportal (PowerShell)

Write-Host "[*] Starte Arrow.it Produktdaten-Extraktor Webportal..." -ForegroundColor Green

# Prüfe ob Docker installiert ist
$dockerInstalled = $false
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0 -and $dockerVersion) {
        $dockerInstalled = $true
        Write-Host "[OK] Docker gefunden: $dockerVersion" -ForegroundColor Green
    }
} catch {
    $dockerInstalled = $false
}

if (-not $dockerInstalled) {
    Write-Host "[!] Docker ist nicht verfügbar!" -ForegroundColor Red
    Write-Host ""
    Write-Host "[*] Moegliche Ursachen:" -ForegroundColor Yellow
    Write-Host "    1. Docker Desktop wurde noch nicht gestartet" -ForegroundColor White
    Write-Host "    2. Docker Desktop ist nicht installiert" -ForegroundColor White
    Write-Host ""
    Write-Host "[*] Loesung:" -ForegroundColor Cyan
    Write-Host "    1. Starten Sie Docker Desktop (Startmenue -> Docker Desktop)" -ForegroundColor White
    Write-Host "    2. Warten Sie, bis das Docker-Icon in der Taskleiste gruen ist" -ForegroundColor White
    Write-Host "    3. Oeffnen Sie ein neues PowerShell-Fenster" -ForegroundColor White
    Write-Host "    4. Fuehren Sie dieses Skript erneut aus" -ForegroundColor White
    Write-Host ""
    
    $startDocker = Read-Host "Moechten Sie Docker Desktop jetzt starten? (j/n)"
    if ($startDocker -eq "j" -or $startDocker -eq "y" -or $startDocker -eq "J" -or $startDocker -eq "Y") {
        Write-Host "[*] Starte Docker Desktop..." -ForegroundColor Yellow
        Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue
        
        Write-Host "[*] Warten Sie bitte ca. 30-60 Sekunden, bis Docker Desktop gestartet ist..." -ForegroundColor Yellow
        Write-Host "[*] Das Docker-Icon sollte in der Taskleiste erscheinen" -ForegroundColor Yellow
        Write-Host ""
        
        # Warte auf Docker
        $timeout = 120 # 2 Minuten
        $elapsed = 0
        $dockerRunning = $false
        
        while ($elapsed -lt $timeout -and -not $dockerRunning) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            
            try {
                docker info 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    $dockerRunning = $true
                    Write-Host "[OK] Docker Desktop ist bereit!" -ForegroundColor Green
                } else {
                    Write-Host "[*] Warte auf Docker Desktop... ($elapsed/$timeout Sekunden)" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "[*] Warte auf Docker Desktop... ($elapsed/$timeout Sekunden)" -ForegroundColor Yellow
            }
        }
        
        if (-not $dockerRunning) {
            Write-Host "[!] Docker Desktop konnte nicht gestartet werden" -ForegroundColor Red
            Write-Host "[*] Bitte starten Sie Docker Desktop manuell und versuchen Sie es erneut" -ForegroundColor Yellow
            exit 1
        }
    } else {
        exit 1
    }
}

# Prüfe ob Docker Compose installiert ist
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "[!] Docker Compose ist nicht installiert!" -ForegroundColor Red
    exit 1
}

# Erstelle exports Verzeichnis falls nicht vorhanden
if (-not (Test-Path "exports")) {
    New-Item -ItemType Directory -Path "exports" | Out-Null
}

# Baue und starte Container
Write-Host "[*] Baue Docker Container..." -ForegroundColor Yellow
docker-compose build

Write-Host "[*] Starte Container..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "[OK] Webportal wurde gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "[*] Öffnen Sie in Ihrem Browser:" -ForegroundColor Cyan
Write-Host "    http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "[*] Zum Stoppen verwenden Sie:" -ForegroundColor Cyan
Write-Host "    docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "[*] Container Status:" -ForegroundColor Cyan
docker-compose ps
