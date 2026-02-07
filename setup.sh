#!/bin/bash

# Screen to Song - Automated Setup Script
# This script sets up the entire project automatically

set -e  # Exit on any error

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║          🎸 Screen to Song - Setup Script             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Check prerequisites
print_info "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
print_success "Python detected: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi
print_success "Node.js detected: $(node --version)"

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg is not installed"
    echo "Video generation will not work without FFmpeg"
    echo "Install with:"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/"
    echo ""
    read -p "Continue without FFmpeg? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success "FFmpeg detected"
fi

# Setup Backend
print_info "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt --quiet
print_success "Python dependencies installed"

# Setup environment file
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cp ../.env.example .env
    print_warning "Please edit backend/.env and add your API keys"
    print_info "You need either ANTHROPIC_API_KEY or OPENAI_API_KEY"
    echo ""
    echo "Get keys from:"
    echo "  Anthropic: https://console.anthropic.com/"
    echo "  OpenAI: https://platform.openai.com/"
    echo ""
    read -p "Press Enter to continue after adding API keys..."
else
    print_success ".env file exists"
fi

# Create outputs directory
mkdir -p outputs
print_success "Backend setup complete"

cd ..

# Setup Frontend
print_info "Setting up frontend..."
cd frontend

# Install dependencies
print_info "Installing Node.js dependencies..."
npm install --quiet
print_success "Node.js dependencies installed"

# Setup environment file
if [ ! -f ".env.local" ]; then
    print_info "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
    print_success ".env.local created"
else
    print_success ".env.local exists"
fi

cd ..

# Run system test
print_info "Running system test..."
python3 scripts/test_system.py

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║              🎉 Setup Complete!                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Next steps:"
echo "  1. Make sure you've added API keys to backend/.env"
echo "  2. Start the backend:"
echo "     cd backend && ./start.sh"
echo "  3. In a new terminal, start the frontend:"
echo "     cd frontend && ./start.sh"
echo "  4. Open http://localhost:3000 in your browser"
echo ""
echo "For more info, see QUICKSTART.md"
echo ""
