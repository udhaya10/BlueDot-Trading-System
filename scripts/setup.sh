#!/bin/bash

# BlueDot Trading System Setup Script

echo "🚀 Setting up BlueDot Trading System..."

# Check Python version
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create and activate virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create necessary directories if they don't exist
echo "📁 Ensuring directory structure..."
mkdir -p data/{raw,processed,output}
mkdir -p logs
mkdir -p config

# Set up pre-commit hooks
echo "🔍 Setting up code quality hooks..."
pre-commit install

# Create environment file template
echo "⚙️ Creating environment configuration..."
cat > .env.template << EOL
# BlueDot Trading System Configuration
DATA_INPUT_PATH=data/raw/
DATA_OUTPUT_PATH=data/output/
LOG_LEVEL=INFO
TRADINGVIEW_NAMESPACE=your_namespace_here
EOL

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Copy .env.template to .env and configure your settings"
echo "3. Place your JSON data files in data/raw/"
echo "4. Run: python src/data_processing/json_to_csv.py"
echo ""
echo "Happy trading! 📈"