# Script para instalar nmap y configurar PATH
# Ejecutar como Administrador

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Instalador de nmap para BlueTeamBot" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

# Verificar si se ejecuta como administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠ Este script debe ejecutarse como Administrador" -ForegroundColor Yellow
    Write-Host "`nPor favor:" -ForegroundColor Yellow
    Write-Host "1. Click derecho en PowerShell" -ForegroundColor White
    Write-Host "2. Selecciona 'Ejecutar como administrador'" -ForegroundColor White
    Write-Host "3. Ejecuta nuevamente este script`n" -ForegroundColor White
    pause
    exit
}

Write-Host "✓ Ejecutando como Administrador`n" -ForegroundColor Green

# Opción 1: Instalar con Chocolatey
Write-Host "[1/3] Intentando instalar nmap con Chocolatey..." -ForegroundColor Cyan
try {
    choco install nmap -y --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ nmap instalado correctamente con Chocolatey" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ Error con Chocolatey: $_" -ForegroundColor Yellow
}

# Buscar nmap instalado
Write-Host "`n[2/3] Buscando nmap.exe..." -ForegroundColor Cyan
$nmapPaths = @(
    "C:\Program Files (x86)\Nmap",
    "C:\Program Files\Nmap",
    "C:\ProgramData\chocolatey\lib\nmap\tools",
    "C:\ProgramData\chocolatey\lib\nmap\tools\nmap-7.97.0"
)

$nmapFound = $false
$nmapPath = $null

foreach ($path in $nmapPaths) {
    if (Test-Path "$path\nmap.exe") {
        $nmapPath = $path
        $nmapFound = $true
        Write-Host "✓ nmap encontrado en: $nmapPath" -ForegroundColor Green
        break
    }
}

if (-not $nmapFound) {
    Write-Host "✗ nmap no encontrado en rutas estándar" -ForegroundColor Red
    Write-Host "`nDescargando instalador oficial..." -ForegroundColor Yellow
    
    # Descargar instalador oficial
    $installerUrl = "https://nmap.org/dist/nmap-7.95-setup.exe"
    $installerPath = "$env:TEMP\nmap-setup.exe"
    
    Write-Host "Descargando de: $installerUrl" -ForegroundColor Cyan
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    
    Write-Host "Ejecutando instalador..." -ForegroundColor Cyan
    Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
    
    # Buscar de nuevo
    Start-Sleep -Seconds 3
    foreach ($path in $nmapPaths) {
        if (Test-Path "$path\nmap.exe") {
            $nmapPath = $path
            $nmapFound = $true
            Write-Host "✓ nmap instalado correctamente" -ForegroundColor Green
            break
        }
    }
}

# Agregar al PATH
if ($nmapFound) {
    Write-Host "`n[3/3] Configurando PATH..." -ForegroundColor Cyan
    
    # PATH del Sistema
    $systemPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($systemPath -notlike "*$nmapPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$systemPath;$nmapPath", "Machine")
        Write-Host "✓ Agregado al PATH del Sistema" -ForegroundColor Green
    } else {
        Write-Host "⚠ Ya está en el PATH del Sistema" -ForegroundColor Yellow
    }
    
    # PATH del Usuario (backup)
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$nmapPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$nmapPath", "User")
        Write-Host "✓ Agregado al PATH del Usuario" -ForegroundColor Green
    }
    
    # PATH de la sesión actual
    $env:Path += ";$nmapPath"
    
    # Verificar instalación
    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host "  Verificación" -ForegroundColor Cyan
    Write-Host "============================================`n" -ForegroundColor Cyan
    
    & "$nmapPath\nmap.exe" --version
    
    Write-Host "`n✅ INSTALACIÓN COMPLETA" -ForegroundColor Green
    Write-Host "`nPara usar nmap:" -ForegroundColor White
    Write-Host "1. Cierra TODAS las terminales/VSCode" -ForegroundColor Yellow
    Write-Host "2. Abre una nueva terminal" -ForegroundColor Yellow
    Write-Host "3. Ejecuta: nmap --version`n" -ForegroundColor Yellow
    
} else {
    Write-Host "`n❌ ERROR: No se pudo instalar nmap" -ForegroundColor Red
    Write-Host "Por favor, instala manualmente desde: https://nmap.org/download.html`n" -ForegroundColor Yellow
}

Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
