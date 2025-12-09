#!/bin/bash

# Közéleti Pontozó - macOS Installer
# Created by: Wratschko Peter

set -e

echo "======================================"
echo "Közéleti Pontozó Telepítő (macOS)"
echo "======================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nincs telepítve!"
    echo ""
    echo "Kérlek telepítsd a Python 3-at:"
    echo "1. Látogass el: https://www.python.org/downloads/"
    echo "2. Töltsd le és telepítsd a legújabb Python 3 verziót"
    echo "3. Futtasd újra ezt a telepítőt"
    echo ""
    read -p "Nyomj Enter-t a böngésző megnyitásához..."
    open "https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python 3 megtalálva: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Virtuális környezet létrehozása..."
    python3 -m venv .venv
    echo "✓ Virtuális környezet elkészült"
else
    echo "✓ Virtuális környezet már létezik"
fi
echo ""

# Activate virtual environment
echo "🔧 Virtuális környezet aktiválása..."
source .venv/bin/activate
echo "✓ Aktiválva"
echo ""

# Upgrade pip
echo "📦 pip frissítése..."
python -m pip install --upgrade pip --quiet
echo "✓ pip frissítve"
echo ""

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Követelmények telepítése..."
    pip install -r requirements.txt --quiet
    echo "✓ Követelmények telepítve"
else
    echo "⚠️  requirements.txt nem található, alapértelmezett csomagok telepítése..."
    pip install streamlit pandas python-docx openpyxl --quiet
    echo "✓ Alapértelmezett csomagok telepítve"
fi
echo ""

# Create necessary directories
echo "📁 Doksi mappa létrehozása..."
mkdir -p filled_documents
echo "✓ Doksi mappa elkészült"
echo ""

# Check for required files
echo "📄 Szükséges fájlok ellenőrzése..."
if [ ! -f "data.csv" ]; then
    echo "⚠️  data.csv nem található - létre kell hoznod mielőtt használnád a programot"
fi
if [ ! -f "sablon.docx" ]; then
    echo "⚠️  sablon.docx nem található - létre kell hoznod mielőtt használnád a programot"
fi
if [ ! -f "scores.json" ]; then
    echo "📝 scores.json létrehozása..."
    echo "[]" > scores.json
fi
echo ""

# Create launcher script
echo "🚀 Indító script létrehozása..."
cat > run_app.command << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
source .venv/bin/activate
python start.py
EOF
chmod +x run_app.command
echo "✓ Indító script elkészült"
echo ""

echo "======================================"
echo "✅ TELEPÍTÉS SIKERES!"
echo "======================================"
echo ""
echo "A program indításához:"
echo "  • Dupla klikk a 'run_app.command' fájlon"
echo "  VAGY"
echo "  • Terminálban: ./run_app.command"
echo ""
echo "Első indításnál a macOS kérheti az engedélyed."
echo ""
read -p "Nyomj Enter-t a kilépéshez..."
