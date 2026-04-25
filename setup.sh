#!/bin/bash

# Setup script for Gemini API Wrapper - Linux/Mac

echo ""
echo "========================================"
echo "Gemini API Wrapper - Setup Script"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[1/4] Python found:"
python3 --version
echo ""

# Create virtual environment
echo "[2/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi
echo ""

# Activate virtual environment
echo "[3/4] Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated."
echo ""

# Install dependencies
echo "[4/4] Installing dependencies..."
pip install -r requirements.txt
echo "Dependencies installed."
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Create a .env file and add your Gemini API key:"
echo "   cp .env.example .env"
echo "   Edit .env and add your key from: https://aistudio.google.com/app/apikeys"
echo ""
echo "2. Start the API server:"
echo "   python main.py"
echo ""
echo "3. In another terminal, start Streamlit UI:"
echo "   streamlit run app.py"
echo ""
echo "4. Test with Postman:"
echo "   Import Gemini_API_Wrapper.postman_collection.json"
echo ""
echo "5. Optional security scan:"
echo "   ./security_scan.sh"
echo ""
