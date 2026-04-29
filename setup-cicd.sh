#!/bin/bash
# Setup script for CI/CD pipeline
# Run this after cloning to set up local development environment

set -e

echo "🚀 Setting up CI/CD pipeline..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install production dependencies
echo "📚 Installing production dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development dependencies..."
pip install pytest pytest-cov black flake8 isort mypy pylint bandit safety pip-audit

# Install pre-commit hooks
echo "🔐 Setting up pre-commit hooks..."
pip install pre-commit
pre-commit install

echo ""
echo "✅ Setup complete! Next steps:"
echo ""
echo "1. Run local CI checks:"
echo "   make ci-local"
echo ""
echo "2. Run Docker services:"
echo "   make docker-up"
echo ""
echo "3. View available commands:"
echo "   make help"
echo ""
echo "4. For detailed guide, see: CI_CD_GUIDE.md"
echo ""
