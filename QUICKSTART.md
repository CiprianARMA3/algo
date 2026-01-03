# Quick Start Guide

## Running the System

### Option 1: Automated Startup (Recommended)

```bash
./start.sh
```

This script will:
1. Create Python virtual environment (if needed)
2. Install Python dependencies
3. Start the FastAPI backend on port 8000
4. Start the Next.js dashboard on port 3001

### Option 2: Manual Startup

**Terminal 1 - API Server:**
```bash
cd api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Dashboard:**
```bash
npm install  # First time only
npm run dev
```

## Access Points

- **Dashboard**: http://localhost:3001
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Quick Test

1. Open http://localhost:3001 in your browser
2. Select "Stocks" tab
3. Click on "AAPL"
4. View the candlestick chart and statistical analysis

## Available Symbols

### Stocks (NASDAQ/S&P 500)
AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK-B, V, JPM, and 60+ more

### Forex
- EURUSD - Euro / US Dollar
- GBPUSD - British Pound / US Dollar
- USDJPY - US Dollar / Japanese Yen
- XAUUSD - Gold / US Dollar
- XAGUSD - Silver / US Dollar

## Troubleshooting

**Port Already in Use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3001
lsof -ti:3001 | xargs kill -9
```

**Missing Dependencies:**
```bash
# Backend
cd api && pip install -r requirements.txt

# Frontend
npm install
```

**Python Version:**
Requires Python 3.9 or higher. Check with:
```bash
python3 --version
```
