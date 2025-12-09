@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Közéleti Pontozó - Windows Installer
REM Created by: Wratschko Peter

echo ======================================
echo Közéleti Pontozó Telepítő (Windows)
echo ======================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nincs telepítve!
    echo.
    echo Kérlek telepítsd a Python-t:
    echo 1. Látogass el: https://www.python.org/downloads/
    echo 2. Töltsd le és telepítsd a legújabb Python 3 verziót
    echo 3. FONTOS: Pipáld be az "Add Python to PATH" opciót!
    echo 4. Futtasd újra ezt a telepítőt
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✓ Python megtalálva: !PYTHON_VERSION!
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Virtuális környezet létrehozása...
    python -m venv .venv
    echo ✓ Virtuális környezet elkészült
) else (
    echo ✓ Virtuális környezet már létezik
)
echo.

REM Activate virtual environment
echo 🔧 Virtuális környezet aktiválása...
call .venv\Scripts\activate.bat
echo ✓ Aktiválva
echo.

REM Upgrade pip
echo 📦 pip frissítése...
python -m pip install --upgrade pip >nul 2>&1
echo ✓ pip frissítve
echo.

REM Install requirements
if exist "requirements.txt" (
    echo 📦 Függőségek telepítése...
    echo    (Ez eltarthat néhány percig...)
    pip install -r requirements.txt >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✓ Függőségek telepítve
    ) else (
        echo ⚠️  Hiba a függőségek telepítésekor
        pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    echo ⚠️  requirements.txt nem található, alapértelmezett csomagok telepítése...
    pip install streamlit pandas python-docx >nul 2>&1
    echo ✓ Alapértelmezett csomagok telepítve
)
echo.

REM Create necessary directories
echo 📁 Doksi mappa létrehozása...
if not exist "filled_documents" mkdir filled_documents
echo ✓ Doksi mappa elkészült
echo.

REM Check for required files
echo 📄 Szükséges fájlok ellenőrzése...
if not exist "data.csv" (
    echo ⚠️  data.csv nem található - létre kell hoznod mielőtt használnád a programot
)
if not exist "sablon.docx" (
    echo ⚠️  sablon.docx nem található - létre kell hoznod mielőtt használnád a programot
)
if not exist "scores.json" (
    echo 📝 scores.json létrehozása...
    echo [] > scores.json
)
echo.

REM Create launcher script
echo 🚀 Indító script létrehozása...
(
echo @echo off
echo cd /d "%%~dp0"
echo call .venv\Scripts\activate.bat
echo python start.py
echo pause
) > run_app.bat
echo ✓ Indító script elkészült
echo.

echo ======================================
echo ✅ TELEPÍTÉS SIKERES!
echo ======================================
echo.
echo A program indításához:
echo   • Dupla klikk a 'run_app.bat' fájlon
echo.
echo.
pause
