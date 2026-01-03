"""
Volatility modeling using GARCH family models
Implements GARCH, GJR-GARCH for volatility forecasting
"""
import numpy as np
import pandas as pd
from arch import arch_model
from typing import Dict, List, Optional
from data.models import VolatilityForecast


def fit_garch(
    returns: pd.Series,
    p: int = 1,
    q: int = 1,
    model_type: str = 'GARCH',
    dist: str = 'normal'
) -> Dict[str, any]:
    """
    Fit GARCH model to returns
    
    Args:
        returns: Return series (should be percentage returns * 100)
        p: GARCH order
        q: ARCH order
        model_type: 'GARCH', 'GJR', 'EGARCH', 'FIGARCH'
        dist: Error distribution ('normal', 't', 'skewt')
    
    Returns:
        Dictionary with model results
    """
    # Scale returns to percentage
    returns_pct = returns * 100
    returns_clean = returns_pct.dropna()
    
    if len(returns_clean) < 100:
        raise ValueError("Insufficient data for GARCH estimation (need at least 100 points)")
    
    # Fit model
    model = arch_model(
        returns_clean,
        vol=model_type,
        p=p,
        q=q,
        dist=dist
    )
    
    result = model.fit(disp='off', show_warning=False)
    
    return {
        'model': result,
        'params': result.params.to_dict(),
        'conditional_volatility': result.conditional_volatility,
        'aic': result.aic,
        'bic': result.bic
    }


def forecast_volatility(
    returns: pd.Series,
    horizon: int = 10,
    model_type: str = 'GARCH',
    p: int = 1,
    q: int = 1
) -> VolatilityForecast:
    """
    Forecast volatility using GARCH models
    
    Args:
        returns: Historical returns
        horizon: Forecast horizon (days)
        model_type: 'GARCH', 'GJR', 'EGARCH'
        p: GARCH order
        q: ARCH order
    
    Returns:
        VolatilityForecast object
    """
    # Fit model
    garch_result = fit_garch(returns, p=p, q=q, model_type=model_type)
    model_fit = garch_result['model']
    
    # Generate forecast
    forecast = model_fit.forecast(horizon=horizon)
    forecasted_variance = forecast.variance.values[-1, :]
    forecasted_volatility = np.sqrt(forecasted_variance)
    
    # Current volatility (last conditional vol)
    current_vol = float(garch_result['conditional_volatility'].iloc[-1])
    
    # Annualized volatility (assuming 252 trading days)
    annualized_vol = current_vol * np.sqrt(252) / 100
    
    return VolatilityForecast(
        model_type=model_type,
        current_volatility=current_vol / 100,  # Convert back to decimal
        forecast_horizon=horizon,
        forecasted_volatility=(forecasted_volatility / 100).tolist(),
        annualized_volatility=float(annualized_vol),
        parameters=garch_result['params']
    )


def calculate_realized_volatility(
    returns: pd.Series,
    window: int = 20,
    annualize: bool = True
) -> pd.Series:
    """
    Calculate realized volatility from returns
    
    Args:
        returns: Return series
        window: Rolling window size
        annualize: If True, annualize the volatility
    
    Returns:
        Series of realized volatility
    """
    rv = returns.rolling(window=window).std()
    
    if annualize:
        rv = rv * np.sqrt(252)
    
    return rv


def calculate_parkinson_volatility(
    df: pd.DataFrame,
    window: int = 20,
    annualize: bool = True
) -> pd.Series:
    """
    Parkinson volatility estimator (uses high-low range)
    More efficient than close-to-close
    
    Args:
        df: DataFrame with 'high' and 'low' columns
        window: Rolling window
        annualize: If True, annualize the result
    
    Returns:
        Parkinson volatility series
    """
    hl_ratio = np.log(df['high'] / df['low'])
    parkinson_vol = hl_ratio.rolling(window=window).apply(
        lambda x: np.sqrt(np.sum(x**2) / (4 * len(x) * np.log(2)))
    )
    
    if annualize:
        parkinson_vol = parkinson_vol * np.sqrt(252)
    
    return parkinson_vol


def calculate_garman_klass_volatility(
    df: pd.DataFrame,
    window: int = 20,
    annualize: bool = True
) -> pd.Series:
    """
    Garman-Klass volatility estimator (uses OHLC)
    More efficient than Parkinson
    
    Args:
        df: DataFrame with 'open', 'high', 'low', 'close'
        window: Rolling window
        annualize: If True, annualize the result
    
    Returns:
        Garman-Klass volatility series
    """
    log_hl = np.log(df['high'] / df['low'])
    log_co = np.log(df['close'] / df['open'])
    
    gk = 0.5 * (log_hl ** 2) - (2 * np.log(2) - 1) * (log_co ** 2)
    gk_vol = np.sqrt(gk.rolling(window=window).mean())
    
    if annualize:
        gk_vol = gk_vol * np.sqrt(252)
    
    return gk_vol


def fit_gjr_garch(
    returns: pd.Series,
    p: int = 1,
    o: int = 1,
    q: int = 1
) -> Dict[str, any]:
    """
    Fit GJR-GARCH model (asymmetric GARCH for leverage effect)
    
    Args:
        returns: Return series
        p: Symmetric GARCH order
        o: Asymmetric order
        q: ARCH order
    
    Returns:
        Model results dictionary
    """
    returns_pct = returns * 100
    returns_clean = returns_pct.dropna()
    
    model = arch_model(
        returns_clean,
        vol='GARCH',
        p=p,
        o=o,
        q=q,
        dist='normal'
    )
    
    result = model.fit(disp='off', show_warning=False)
    
    return {
        'model': result,
        'params': result.params.to_dict(),
        'conditional_volatility': result.conditional_volatility,
        'leverage_effect': result.params.get('gamma[1]', 0.0) if o > 0 else 0.0
    }
