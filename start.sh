#!/bin/bash

# Quantitative Analysis System - Startup Script

echo "🚀 Starting Quantitative Analysis System..."
echo ""

# Check if Python virtual environment exists
if [ ! -d "api/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd api
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Python virtual environment found"
fi

# Start the API server in the background
echo "🔧 Starting FastAPI backend..."
cd api
source venv/bin/activate
python main.py &
API_PID=$!
cd ..

echo "Backend PID: $API_PID"
echo "API running at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
echo ""

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
sleep 5

# Start the Next.js dashboard
echo "🎨 Starting Next.js dashboard..."
echo "Dashboard will be at: http://localhost:3001"
echo ""

npm run dev

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT
