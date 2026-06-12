#!/bin/bash

# Start the Threat Modeling Web UI

cd "$(dirname "$0")/web/backend"

# Activate virtual environment
source venv/bin/activate 2>/dev/null || true

echo "🔐 Starting Threat Modeling Agent Web UI..."
echo "📱 Open your browser and go to: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python run.py
