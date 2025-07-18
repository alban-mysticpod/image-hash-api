#!/bin/bash

echo "🚀 Starting Image Hash Template API"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed"
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error installing dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt file not found"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/uploads
echo "✅ Directories created"

# Start the API
echo "🌟 Starting API on http://localhost:8080"
echo "📚 Documentation available at http://localhost:8080/docs"
echo ""
echo "To stop the API, press Ctrl+C"
echo ""

uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload 