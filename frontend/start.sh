#!/bin/bash

# Screen to Song - Frontend Startup Script

echo "🎸 Screen to Song - Starting Frontend"
echo "====================================="
echo ""

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "   Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "✓ Node detected: $(node --version)"
echo "✓ npm detected: $(npm --version)"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Check for .env.local file
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
fi

# Start development server
echo ""
echo "🚀 Starting Next.js development server"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000 (ensure it's running)"
echo ""
npm run dev
