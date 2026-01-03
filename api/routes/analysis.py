"""
Analysis API routes
Provides endpoints for quantitative analysis
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd
from datetime import datetime, timedelta

from data.models import (
    AnalysisResponse,
    BatchAnalysisRequest,
    ErrorResponse,
    MicrostructureMetrics
)
from data.provider import data_provider
from analyzers.cointegration import combined_stationarity_test
from analyzers.volatility import forecast_volatility
from analyzers.signal_processing import (
    fractional_diff,
    find_min_ffd,
    wavelet_denoise,
    fft_analysis,
    calculate_hurst_exponent
)
from analyzers.regime import detect_regime
from analyzers.recommendation import calculate_trading_signal
from config import settings

router = APIRouter()


@router.get("/analyze/{symbol}", response_model=AnalysisResponse)
async def analyze_symbol(
    symbol: str,
    lookback_days: int = Query(default=252, ge=30, le=2520),
    include_signal_processing: bool = True,
    include_regime: bool = True
):
    """
    Perform comprehensive quantitative analysis on a symbol
    
    Args:
        symbol: Stock ticker or forex pair (e.g., AAPL, EURUSD)
        lookback_days: Number of days to analyze (default: 252 = 1 year)
        include_signal_processing: Include fractional diff, wavelets, etc.
        include_regime: Include HMM regime detection
    
    Returns:
        AnalysisResponse with all computed indicators
    """
    try:
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days + 100)  # Buffer for calculations
        
        df = data_provider.fetch_ohlcv(symbol, start_date=start_date, end_date=end_date)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate returns
        returns = data_provider.calculate_returns(df)
        
        # Current price and change
        current_price = float(df['close'].iloc[-1])
        price_change_pct = float(((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100)
        
        # Initialize response
        response = AnalysisResponse(
            symbol=symbol,
            lookback_days=lookback_days,
            current_price=current_price,
            price_change_pct=price_change_pct,
            metrics={}
        )
        
        # 1. Stationarity Tests (Cointegration analysis)
        try:
            cointegration_result = combined_stationarity_test(df['close'])
            response.cointegration = cointegration_result
        except Exception as e:
            print(f"Cointegration error: {str(e)}")
        
        # 2. Volatility Analysis
        try:
            vol_forecast = forecast_volatility(
                returns,
                horizon=10,
                model_type='GARCH',
                p=1,
                q=1
            )
            response.volatility = vol_forecast
        except Exception as e:
            print(f"Volatility error: {str(e)}")
        
        # 3. Signal Processing
        if include_signal_processing:
            try:
                # Find optimal fractional differentiation order
                ffd_d = find_min_ffd(df['close'], max_d=1.0)
                
                # Apply fractional differentiation
                ffd_series = fractional_diff(df['close'], d=ffd_d)
                
                # Wavelet denoising
                denoised = wavelet_denoise(df['close'])
                
                # FFT analysis
                fft_result = fft_analysis(df['close'])
                
                # Hurst exponent
                hurst = calculate_hurst_exponent(df['close'])
                
                from data.models import SignalProcessingResult
                response.signal_processing = SignalProcessingResult(
                    fractional_diff_order=float(ffd_d),
                    fractional_diff_series=ffd_series.tail(50).tolist() if len(ffd_series) > 0 else [],
                    wavelet_denoised=denoised.tail(50).tolist() if len(denoised) > 0 else [],
                    dominant_frequency=fft_result['dominant_frequency'],
                    hurst_exponent=float(hurst)
                )
                
                # Add to metrics
                response.metrics['hurst_exponent'] = float(hurst)
                response.metrics['dominant_period_days'] = float(fft_result['period'])
                
            except Exception as e:
                print(f"Signal processing error: {str(e)}")
        
        # 4. Regime Detection
        if include_regime:
            try:
                regime_result = detect_regime(returns, n_states=3)
                response.regime = regime_result
            except Exception as e:
                print(f"Regime detection error: {str(e)}")
        
        # 5. Additional Metrics
        response.metrics['sharpe_ratio'] = float(returns.mean() / returns.std() * np.sqrt(252)) if returns.std() > 0 else 0.0
        response.metrics['max_drawdown'] = float(calculate_max_drawdown(df['close']))
        response.metrics['skewness'] = float(returns.skew())
        response.metrics['kurtosis'] = float(returns.kurtosis())
        
        # 6. Trading Recommendation
        try:
            analysis_dict = {
                'signal_processing': response.signal_processing.dict() if response.signal_processing else {},
                'regime': response.regime.dict() if response.regime else {},
                'volatility': response.volatility.dict() if response.volatility else {},
                'price_change_pct': response.price_change_pct,
                'metrics': response.metrics,
                'cointegration': response.cointegration.dict() if response.cointegration else {}
            }
            
            recommendation_result = calculate_trading_signal(
                analysis_dict,
                df['close'],
                returns
            )
            
            from data.models import TradingRecommendation
            response.recommendation = TradingRecommendation(**recommendation_result)
        except Exception as e:
            print(f"Recommendation error: {str(e)}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/batch-analyze", response_model=List[AnalysisResponse])
async def batch_analyze(request: BatchAnalysisRequest):
    """
    Analyze multiple symbols in batch
    
    Args:
        request: BatchAnalysisRequest with list of symbols
    
    Returns:
        List of AnalysisResponse objects
    """
    results = []
    
    for symbol in request.symbols:
        try:
            result = await analyze_symbol(
                symbol=symbol,
                lookback_days=request.lookback_days,
                include_signal_processing=True,
                include_regime=True
            )
            results.append(result)
        except Exception as e:
            print(f"Error analyzing {symbol}: {str(e)}")
            continue
    
    return results


@router.get("/indicators/{symbol}/volatility")
async def get_volatility_forecast(
    symbol: str,
    horizon: int = Query(default=10, ge=1, le=30),
    model_type: str = Query(default="GARCH")
):
    """Get volatility forecast for a symbol"""
    try:
        df = data_provider.fetch_ohlcv(symbol, period="1y")
        returns = data_provider.calculate_returns(df)
        
        vol_forecast = forecast_volatility(
            returns,
            horizon=horizon,
            model_type=model_type
        )
        
        return vol_forecast
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indicators/{symbol}/regime")
async def get_regime_detection(
    symbol: str,
    n_states: int = Query(default=3, ge=2, le=5)
):
    """Get regime detection for a symbol"""
    try:
        df = data_provider.fetch_ohlcv(symbol, period="1y")
        returns = data_provider.calculate_returns(df)
        
        regime_result = detect_regime(returns, n_states=n_states)
        
        return regime_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_max_drawdown(prices: pd.Series) -> float:
    """Calculate maximum drawdown"""
    cummax = prices.cummax()
    drawdown = (prices - cummax) / cummax
    return abs(float(drawdown.min()))


import numpy as np
