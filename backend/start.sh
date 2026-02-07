#!/bin/bash

# Screen to Song - Backend Startup Script

echo "🎸 Screen to Song - Starting Backend"
echo "===================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✓ Python detected: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp ../.env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
    echo ""
fi

# Check API keys
if ! grep -q "ANTHROPIC_API_KEY=sk-" .env && ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: No API keys configured in .env"
    echo "   Add either ANTHROPIC_API_KEY or OPENAI_API_KEY"
    echo ""
fi

# Start server
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo ""
python main.py
