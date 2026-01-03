#!/bin/bash

# Script to run the development servers for both frontend and backend

# --- Change to the script's directory ---
# This allows the script to be run from anywhere.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

# Function to clean up background processes on exit
cleanup() {
    echo -e "\nShutting down servers..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID
        echo "Backend server stopped."
    fi
    exit
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Backend (Python API) ---
echo "---------------------------------"
echo "🚀 Starting Python backend server..."
echo "---------------------------------"

# Check if virtual environment exists
if [ ! -d "api/venv" ]; then
    echo "Python virtual environment not found in api/venv."
    echo "Please create it first by running the following commands from the 'my-app' directory:"
    echo "cd api"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    echo "deactivate"
    exit 1
fi

# Activate virtual environment
source api/venv/bin/activate

# Install/update Python dependencies
echo "🐍 Installing/updating Python dependencies..."
pip install -r api/requirements.txt -q

# Start the backend server in the background
(cd api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload &)
BACKEND_PID=$!
echo "✅ Backend server started with PID: $BACKEND_PID"
echo "   Running at: http://localhost:8000"


# --- Frontend (Next.js) ---
echo ""
echo "----------------------------------"
echo "🚀 Starting Next.js frontend server..."
echo "----------------------------------"

# Install/update Node.js dependencies
echo "📦 Installing/updating Node.js dependencies..."
npm install > /dev/null 2>&1

# Start the frontend server in the foreground
echo "✅ Frontend server starting..."
echo "   Running at: http://localhost:3001"
npm run dev

# The script will block here until `npm run dev` is stopped.
# The `trap` at the top will ensure the `cleanup` function is called on exit.