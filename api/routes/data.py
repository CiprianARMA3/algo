"""
Data API routes
Provides access to raw market data and symbol lists
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime, timedelta
import pandas as pd

from data.models import SymbolInfo, OHLCVData
from data.provider import data_provider

router = APIRouter()


@router.get("/symbols", response_model=List[SymbolInfo])
async def get_all_symbols():
    """
    Get list of all available symbols
    
    Returns:
        List of SymbolInfo objects (stocks + forex)
    """
    return data_provider.get_all_symbols()


@router.get("/symbols/stocks", response_model=List[str])
async def get_stock_symbols():
    """Get list of stock symbols (NASDAQ + S&P500)"""
    stocks = set(data_provider.NASDAQ_SYMBOLS + data_provider.SP500_SYMBOLS)
    return sorted(list(stocks))


@router.get("/symbols/forex", response_model=List[str])
async def get_forex_symbols():
    """Get list of forex pairs"""
    return list(data_provider.FOREX_SYMBOLS.keys())


@router.get("/ohlcv/{symbol}")
async def get_ohlcv_data(
    symbol: str,
    period: str = Query(default="1y", regex="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|max)$"),
    interval: str = Query(default="1d", regex="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$")
):
    """
    Get OHLCV data for a symbol
    
    Args:
        symbol: Stock ticker or forex pair
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)
        interval: Data interval (1d for daily, 1h for hourly, etc.)
    
    Returns:
        OHLCV data as JSON
    """
    try:
        df = data_provider.fetch_ohlcv(symbol, period=period)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Convert to records
        df_reset = df.reset_index()
        df_reset = df_reset.rename(columns={'Date': 'timestamp', 'index': 'timestamp'})
        
        records = df_reset.to_dict('records')
        
        return {
            "symbol": symbol,
            "period": period,
            "count": len(records),
            "data": records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.get("/price/{symbol}")
async def get_current_price(symbol: str):
    """
    Get current price for a symbol
    
    Args:
        symbol: Stock ticker or forex pair
    
    Returns:
        Current price and metadata
    """
    try:
        price = data_provider.get_current_price(symbol)
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
