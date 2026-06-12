#!/bin/bash

# Setup script for Threat Modeling Web UI

echo "🔐 Setting up Threat Modeling Agent Web UI..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/web/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing web server dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn pydantic python-dotenv

echo "📥 Installing agent dependencies..."
pip install langchain langgraph langchain-google-genai tavily-python

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has GOOGLE_API_KEY and TAVILY_API_KEY"
echo "2. Run: bash run-web.sh"
echo ""
