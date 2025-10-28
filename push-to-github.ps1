# Script zum Pushen des Projekts zu GitHub

Write-Host "=== GitHub Repository Setup ===" -ForegroundColor Cyan
Write-Host ""

$repoName = "arrow-scraper"

# Prüfe ob bereits ein Remote konfiguriert ist
$remoteExists = git remote -v 2>$null

if ($remoteExists) {
    Write-Host "[!] Ein Remote-Repository ist bereits konfiguriert:" -ForegroundColor Yellow
    Write-Host $remoteExists
    Write-Host ""
    
    $continue = Read-Host "Moechten Sie trotzdem pushen? (j/n)"
    if ($continue -ne "j" -and $continue -ne "y") {
        exit 0
    }
}

Write-Host "[*] Schritt 1: Erstellen Sie ein neues Repository auf GitHub:" -ForegroundColor Yellow
Write-Host ""
Write-Host "    1. Gehen Sie zu: https://github.com/new" -ForegroundColor White
Write-Host "    2. Repository Name: $repoName" -ForegroundColor Green
Write-Host "    3. Beschreibung: Arrow.it Web Scraper Portal - Docker-based web interface" -ForegroundColor White
Write-Host "    4. Waehlen Sie: Private oder Public" -ForegroundColor White
Write-Host "    5. NICHT initialisieren mit README, .gitignore oder Lizenz" -ForegroundColor Red
Write-Host "    6. Klicken Sie auf 'Create repository'" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Haben Sie das Repository erstellt? (j/n)"
if ($continue -ne "j" -and $continue -ne "y") {
    Write-Host "[!] Bitte erstellen Sie zuerst das Repository auf GitHub" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[*] Schritt 2: GitHub Username eingeben" -ForegroundColor Yellow
$githubUsername = Read-Host "Ihr GitHub Username"

if (-not $githubUsername) {
    Write-Host "[!] Username ist erforderlich" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[*] Schritt 3: Remote hinzufuegen und pushen..." -ForegroundColor Yellow

# Entferne alten Remote falls vorhanden
git remote remove origin 2>$null

# Füge neuen Remote hinzu
$remoteUrl = "https://github.com/$githubUsername/$repoName.git"
git remote add origin $remoteUrl

Write-Host "[OK] Remote hinzugefuegt: $remoteUrl" -ForegroundColor Green

# Setze Branch auf main (falls master verwendet wird)
$currentBranch = git branch --show-current
if ($currentBranch -eq "master") {
    Write-Host "[*] Benenne Branch von 'master' zu 'main' um..." -ForegroundColor Yellow
    git branch -M main
}

Write-Host "[*] Pushe zu GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Projekt erfolgreich zu GitHub gepusht!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[*] Repository URL:" -ForegroundColor Cyan
    Write-Host "    https://github.com/$githubUsername/$repoName" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "[!] Fehler beim Pushen" -ForegroundColor Red
    Write-Host ""
    Write-Host "[*] Moegliche Ursachen:" -ForegroundColor Yellow
    Write-Host "    1. Authentifizierung erforderlich" -ForegroundColor White
    Write-Host "    2. Falscher Username oder Repository-Name" -ForegroundColor White
    Write-Host "    3. Repository existiert nicht auf GitHub" -ForegroundColor White
    Write-Host ""
    Write-Host "[*] Alternative: Pushen Sie manuell:" -ForegroundColor Cyan
    Write-Host "    git remote add origin https://github.com/$githubUsername/$repoName.git" -ForegroundColor White
    Write-Host "    git push -u origin main" -ForegroundColor White
}

