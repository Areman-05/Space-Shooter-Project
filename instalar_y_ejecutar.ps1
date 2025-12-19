# Script para instalar dependencias y ejecutar el juego Space Shooter

Write-Host "=== Space Shooter - Instalador y Ejecutor ===" -ForegroundColor Cyan
Write-Host ""

# Buscar Python en ubicaciones comunes
$pythonPaths = @(
    "python",
    "python3",
    "py",
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "C:\Python*\python.exe",
    "$env:ProgramFiles\Python*\python.exe"
)

$python = $null
foreach ($path in $pythonPaths) {
    try {
        if ($path -like "*\*") {
            # Es un patrón, buscar archivos
            $found = Get-ChildItem -Path (Split-Path $path) -Filter (Split-Path -Leaf $path) -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found) {
                $test = & $found.FullName --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $python = $found.FullName
                    break
                }
            }
        } else {
            $test = & $path --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $python = $path
                break
            }
        }
    } catch {
        continue
    }
}

if (-not $python) {
    Write-Host "Python no está instalado." -ForegroundColor Yellow
    Write-Host ""
    
    # Intentar instalar con winget
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "Intentando instalar Python con winget..." -ForegroundColor Cyan
        Write-Host "Esto puede tardar unos minutos..." -ForegroundColor Yellow
        Write-Host ""
        
        # Instalar Python
        & winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Python instalado correctamente." -ForegroundColor Green
            Write-Host "Buscando Python instalado..." -ForegroundColor Cyan
            
            # Esperar un momento y buscar Python nuevamente
            Start-Sleep -Seconds 3
            
            # Buscar en ubicaciones comunes después de la instalación
            $newPaths = @(
                "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
                "$env:ProgramFiles\Python*\python.exe"
            )
            
            foreach ($path in $newPaths) {
                $found = Get-ChildItem -Path (Split-Path $path -ErrorAction SilentlyContinue) -Filter (Split-Path -Leaf $path) -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($found) {
                    $test = & $found.FullName --version 2>&1
                    if ($LASTEXITCODE -eq 0) {
                        $python = $found.FullName
                        break
                    }
                }
            }
            
            # También intentar con 'python' ahora que está instalado
            if (-not $python) {
                $test = & python --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    $python = "python"
                }
            }
        } else {
            Write-Host "No se pudo instalar Python automáticamente." -ForegroundColor Red
        }
    }
    
    if (-not $python) {
        Write-Host ""
        Write-Host "ERROR: Python no está instalado y no se pudo instalar automáticamente." -ForegroundColor Red
        Write-Host ""
        Write-Host "Opciones para instalar Python manualmente:" -ForegroundColor Yellow
        Write-Host "1. Descargar desde: https://www.python.org/downloads/" -ForegroundColor White
        Write-Host "2. Instalar desde Microsoft Store (buscar 'Python')" -ForegroundColor White
        Write-Host "3. Usar winget manualmente: winget install Python.Python.3.12" -ForegroundColor White
        Write-Host ""
        Write-Host "Después de instalar Python, ejecuta este script nuevamente." -ForegroundColor Yellow
        pause
        exit 1
    }
}

Write-Host "Python encontrado: $python" -ForegroundColor Green
$version = & $python --version
Write-Host "Versión: $version" -ForegroundColor Green
Write-Host ""

# Verificar e instalar pygame
Write-Host "Verificando pygame..." -ForegroundColor Cyan
$pygameCheck = & $python -c "import pygame; print(pygame.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "pygame no está instalado. Instalando..." -ForegroundColor Yellow
    & $python -m pip install --upgrade pip
    & $python -m pip install pygame
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudo instalar pygame." -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "pygame instalado correctamente." -ForegroundColor Green
} else {
    Write-Host "pygame ya está instalado (versión: $($pygameCheck.Trim()))" -ForegroundColor Green
}
Write-Host ""

# Ejecutar el juego
Write-Host "Iniciando el juego..." -ForegroundColor Cyan
Write-Host ""
& $python "Juego Space Shooters\main.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: El juego no se pudo ejecutar." -ForegroundColor Red
    pause
}

