"""
Data provider abstraction layer
Fetches financial data from various sources (Yahoo Finance, Alpha Vantage, etc.)
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Dict
from config import settings
from data.models import OHLCVData, SymbolInfo


class DataProvider:
    """Financial data provider with caching"""
    
    # Major NASDAQ and S&P 500 symbols (subset for initial implementation)
    NASDAQ_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AVGO",
        "COST", "NFLX", "AMD", "PEP", "CSCO", "ADBE", "CMCSA", "INTC",
        "QCOM", "TXN", "INTU", "AMGN", "AMAT", "HON", "SBUX", "GILD",
        "ADI", "PYPL", "MDLZ", "VRTX", "REGN", "ISRG", "MU", "LRCX"
    ]
    
    SP500_SYMBOLS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "BRK-B", "META", "TSLA",
        "V", "UNH", "XOM", "LLY", "JNJ", "JPM", "WMT", "MA", "PG",
        "AVGO", "HD", "CVX", "MRK", "COST", "ABBV", "KO", "PEP",
        "BAC", "CRM", "NFLX", "TMO", "AMD", "ACN", "MCD", "CSCO",
        "DHR", "ABT", "LIN", "ADBE", "DIS", "WFC", "VZ", "CMCSA"
    ]
    
    # Major forex pairs (as Yahoo Finance tickers)
    FOREX_SYMBOLS = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X",
        "AUDUSD": "AUDUSD=X",
        "USDCAD": "CAD=X",
        "USDCHF": "CHF=X",
        "XAUUSD": "GC=F",  # Gold futures
        "XAGUSD": "SI=F",  # Silver futures
    }
    
    def __init__(self):
        self.cache = {}
    
    def get_all_symbols(self) -> List[SymbolInfo]:
        """Get all available symbols"""
        symbols = []
        
        # Add stocks
        for symbol in set(self.NASDAQ_SYMBOLS + self.SP500_SYMBOLS):
            symbols.append(SymbolInfo(
                symbol=symbol,
                name=symbol,
                type="stock",
                exchange="NASDAQ/NYSE"
            ))
        
        # Add forex
        for name, ticker in self.FOREX_SYMBOLS.items():
            symbols.append(SymbolInfo(
                symbol=name,
                name=name,
                type="forex"
            ))
        
        return symbols
    
    def _get_ticker_symbol(self, symbol: str) -> str:
        """Convert symbol to Yahoo Finance ticker"""
        # Check if it's a forex pair
        if symbol in self.FOREX_SYMBOLS:
            return self.FOREX_SYMBOLS[symbol]
        return symbol
    
    def fetch_ohlcv(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        period: str = "1y"
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol
        
        Args:
            symbol: Stock ticker or forex pair
            start_date: Start date for data
            end_date: End date for data
            period: Period string (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with columns: Open, High, Low, Close, Volume
        """
        ticker_symbol = self._get_ticker_symbol(symbol)
        
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            if start_date and end_date:
                df = ticker.history(start=start_date, end=end_date)
            else:
                df = ticker.history(period=period)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Rename columns to standard format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Keep only OHLCV columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error fetching data for {symbol}: {str(e)}")
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        period: str = "1y"
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols
        
        Returns:
            Dictionary mapping symbol to DataFrame
        """
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = self.fetch_ohlcv(symbol, period=period)
            except Exception as e:
                print(f"Warning: Could not fetch {symbol}: {str(e)}")
                continue
        return result
    
    def get_current_price(self, symbol: str) -> float:
        """Get current/latest price for a symbol"""
        ticker_symbol = self._get_ticker_symbol(symbol)
        ticker = yf.Ticker(ticker_symbol)
        
        # Try to get real-time price
        try:
            info = ticker.info
            if 'currentPrice' in info:
                return float(info['currentPrice'])
            elif 'regularMarketPrice' in info:
                return float(info['regularMarketPrice'])
        except:
            pass
        
        # Fallback to last close
        df = self.fetch_ohlcv(symbol, period="1d")
        return float(df['close'].iloc[-1])
    
    def calculate_returns(self, df: pd.DataFrame, column: str = 'close') -> pd.Series:
        """Calculate log returns"""
        return np.log(df[column] / df[column].shift(1)).dropna()


# Global provider instance
data_provider = DataProvider()
