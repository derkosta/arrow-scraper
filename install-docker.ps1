# Docker Installation Script für Windows
# Führen Sie dieses Script als Administrator aus

Write-Host "=== Docker Installation für Windows ===" -ForegroundColor Cyan
Write-Host ""

# Prüfe ob Script als Administrator ausgeführt wird
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[!] Bitte führen Sie dieses Script als Administrator aus!" -ForegroundColor Red
    Write-Host "[*] Rechtsklick auf PowerShell -> Als Administrator ausführen" -ForegroundColor Yellow
    pause
    exit 1
}

# Option 1: Versuche Winget (Windows 10/11)
Write-Host "[1/3] Prüfe Winget (Windows Package Manager)..." -ForegroundColor Yellow
$wingetAvailable = $false

try {
    $wingetCheck = winget --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $wingetAvailable = $true
        Write-Host "[OK] Winget ist verfügbar" -ForegroundColor Green
        
        Write-Host "[*] Installiere Docker Desktop mit Winget..." -ForegroundColor Yellow
        winget install Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Docker Desktop wurde installiert!" -ForegroundColor Green
            Write-Host "[*] Bitte starten Sie Docker Desktop und warten Sie, bis es vollständig geladen ist." -ForegroundColor Yellow
            Write-Host "[*] Starten Sie danach PowerShell neu." -ForegroundColor Yellow
            pause
            exit 0
        }
    }
} catch {
    Write-Host "[!] Winget nicht verfügbar" -ForegroundColor Yellow
}

# Option 2: Prüfe Chocolatey
Write-Host ""
Write-Host "[2/3] Prüfe Chocolatey..." -ForegroundColor Yellow
$chocoAvailable = $false

try {
    $chocoCheck = choco --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $chocoAvailable = $true
        Write-Host "[OK] Chocolatey ist verfügbar" -ForegroundColor Green
        
        $install = Read-Host "Möchten Sie Docker Desktop mit Chocolatey installieren? (j/n)"
        if ($install -eq "j" -or $install -eq "y" -or $install -eq "J" -or $install -eq "Y") {
            Write-Host "[*] Installiere Docker Desktop mit Chocolatey..." -ForegroundColor Yellow
            choco install docker-desktop -y
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Docker Desktop wurde installiert!" -ForegroundColor Green
                Write-Host "[*] Bitte starten Sie Docker Desktop und warten Sie, bis es vollständig geladen ist." -ForegroundColor Yellow
                pause
                exit 0
            }
        }
    }
} catch {
    Write-Host "[!] Chocolatey nicht verfügbar" -ForegroundColor Yellow
}

# Option 3: Manuelle Installation
Write-Host ""
Write-Host "[3/3] Manuelle Installation erforderlich" -ForegroundColor Yellow
Write-Host ""

if (-not $wingetAvailable -and -not $chocoAvailable) {
    Write-Host "[*] Automatische Installation nicht möglich." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Bitte installieren Sie Docker Desktop manuell:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Laden Sie Docker Desktop herunter:" -ForegroundColor White
    Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Green
    Write-Host ""
    Write-Host "2. Führen Sie die Installationsdatei aus" -ForegroundColor White
    Write-Host ""
    Write-Host "3. WICHTIG: Docker benötigt WSL 2!" -ForegroundColor Yellow
    Write-Host ""
    
    $installWSL = Read-Host "Soll WSL 2 jetzt installiert werden? (j/n)"
    if ($installWSL -eq "j" -or $installWSL -eq "y" -or $installWSL -eq "J" -or $installWSL -eq "Y") {
        Write-Host "[*] Installiere WSL 2..." -ForegroundColor Yellow
        
        # WSL installieren
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
        
        Write-Host "[OK] WSL Features aktiviert!" -ForegroundColor Green
        Write-Host "[!] Bitte starten Sie Windows NEU und führen Sie dann erneut aus:" -ForegroundColor Yellow
        Write-Host "    wsl --install" -ForegroundColor White
        Write-Host "    wsl --set-default-version 2" -ForegroundColor White
        Write-Host ""
        Write-Host "Danach können Sie Docker Desktop installieren." -ForegroundColor Cyan
    }
    
    pause
    exit 0
}

# Prüfe WSL 2
Write-Host ""
Write-Host "[*] Prüfe WSL 2 Status..." -ForegroundColor Yellow

try {
    $wslStatus = wsl --status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] WSL ist installiert" -ForegroundColor Green
    } else {
        Write-Host "[!] WSL 2 nicht gefunden" -ForegroundColor Yellow
        Write-Host "[*] Docker benötigt WSL 2!" -ForegroundColor Yellow
        
        $installWSL = Read-Host "Soll WSL 2 jetzt installiert werden? (j/n)"
        if ($installWSL -eq "j" -or $installWSL -eq "y") {
            Write-Host "[*] Installiere WSL 2..." -ForegroundColor Yellow
            wsl --install
            
            Write-Host "[!] Bitte starten Sie Windows NEU!" -ForegroundColor Yellow
            pause
            exit 0
        }
    }
} catch {
    Write-Host "[!] WSL Status konnte nicht geprüft werden" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Installation abgeschlossen ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Yellow
Write-Host "1. Starten Sie Docker Desktop (Startmenü -> Docker Desktop)" -ForegroundColor White
Write-Host "2. Warten Sie, bis Docker vollständig geladen ist" -ForegroundColor White
Write-Host "3. Öffnen Sie ein neues PowerShell-Fenster" -ForegroundColor White
Write-Host "4. Prüfen Sie die Installation: docker --version" -ForegroundColor White
Write-Host ""
pause
