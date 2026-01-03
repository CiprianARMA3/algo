"""
Cointegration Analysis for Statistical Arbitrage
Implements ADF, KPSS, and Johansen tests for mean reversion strategies
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss, coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from typing import Tuple, Dict, Optional
from data.models import CointegrationResult


def adf_test(
    series: pd.Series,
    regression: str = 'c',
    autolag: str = 'AIC'
) -> CointegrationResult:
    """
    Augmented Dickey-Fuller test for stationarity
    
    Args:
        series: Time series to test
        regression: Regression type ('c', 'ct', 'ctt', 'n')
        autolag: Method to determine lag order ('AIC', 'BIC', 't-stat')
    
    Returns:
        CointegrationResult with test statistics
    """
    result = adfuller(series.dropna(), regression=regression, autolag=autolag)
    
    adf_statistic = result[0]
    pvalue = result[1]
    critical_values = result[4]
    
    # Stationary if we reject null hypothesis (p < 0.05)
    is_stationary = pvalue < 0.05
    
    return CointegrationResult(
        adf_statistic=float(adf_statistic),
        adf_pvalue=float(pvalue),
        adf_critical_values={k: float(v) for k, v in critical_values.items()},
        is_stationary=is_stationary
    )


def kpss_test(
    series: pd.Series,
    regression: str = 'c',
    nlags: str = 'auto'
) -> Dict[str, float]:
    """
    KPSS test for stationarity (null hypothesis: stationary)
    
    Args:
        series: Time series to test
        regression: 'c' (level) or 'ct' (trend)
        nlags: Number of lags
    
    Returns:
        Dictionary with test results
    """
    result = kpss(series.dropna(), regression=regression, nlags=nlags)
    
    return {
        'statistic': float(result[0]),
        'pvalue': float(result[1]),
        'critical_values': {k: float(v) for k, v in result[3].items()},
        'is_stationary': result[1] > 0.05  # Do not reject null if p > 0.05
    }


def combined_stationarity_test(
    series: pd.Series
) -> CointegrationResult:
    """
    Combined ADF + KPSS test for robust stationarity check
    Signal is stationary only if:
    - ADF rejects unit root (p < 0.05)
    - KPSS fails to reject stationarity (p > 0.05)
    
    Args:
        series: Time series to test
    
    Returns:
        CointegrationResult with both tests
    """
    adf_result = adf_test(series)
    kpss_result = kpss_test(series)
    
    # Robust stationarity requires both tests to agree
    is_stationary = adf_result.is_stationary and kpss_result['is_stationary']
    
    return CointegrationResult(
        adf_statistic=adf_result.adf_statistic,
        adf_pvalue=adf_result.adf_pvalue,
        adf_critical_values=adf_result.adf_critical_values,
        kpss_statistic=kpss_result['statistic'],
        kpss_pvalue=kpss_result['pvalue'],
        kpss_critical_values=kpss_result['critical_values'],
        is_stationary=is_stationary
    )


def calculate_spread(
    y: pd.Series,
    x: pd.Series,
    method: str = 'ols'
) -> Tuple[pd.Series, float]:
    """
    Calculate spread between two price series
    
    Args:
        y: Dependent variable (price series)
        x: Independent variable (price series)
        method: 'ols' for ordinary least squares
    
    Returns:
        Tuple of (spread series, hedge ratio beta)
    """
    # Align series
    df = pd.DataFrame({'y': y, 'x': x}).dropna()
    
    # Calculate hedge ratio (beta) using OLS
    from sklearn.linear_model import LinearRegression
    model = LinearRegression(fit_intercept=True)
    model.fit(df[['x']], df['y'])
    
    beta = model.coef_[0]
    alpha = model.intercept_
    
    # Calculate spread: y - beta*x
    spread = df['y'] - beta * df['x']
    
    return spread, beta


def johansen_cointegration_test(
    data: pd.DataFrame,
    det_order: int = 0,
    k_ar_diff: int = 1
) -> Dict[str, any]:
    """
    Johansen cointegration test for multivariate analysis
    
    Args:
        data: DataFrame with multiple price series
        det_order: Deterministic trend order (-1, 0, 1)
        k_ar_diff: Number of lagged differences
    
    Returns:
        Dictionary with test results
    """
    result = coint_johansen(data.dropna(), det_order=det_order, k_ar_diff=k_ar_diff)
    
    # Trace statistic tests
    trace_stat = result.lr1
    trace_crit = result.cvt
    
    # Maximum eigenvalue tests
    max_eig_stat = result.lr2
    max_eig_crit = result.cvm
    
    # Determine number of cointegrating vectors
    n_cointegrating = 0
    for i in range(len(trace_stat)):
        if trace_stat[i] > trace_crit[i, 1]:  # 95% confidence
            n_cointegrating = i + 1
    
    return {
        'trace_statistic': trace_stat.tolist(),
        'trace_critical_values': trace_crit[:, 1].tolist(),  # 95% level
        'max_eig_statistic': max_eig_stat.tolist(),
        'max_eig_critical_values': max_eig_crit[:, 1].tolist(),
        'n_cointegrating_vectors': n_cointegrating,
        'eigenvectors': result.evec.tolist()
    }


def calculate_half_life(spread: pd.Series) -> float:
    """
    Calculate mean reversion half-life using Ornstein-Uhlenbeck process
    
    Args:
        spread: Spread time series
    
    Returns:
        Half-life in number of periods
    """
    spread_lag = spread.shift(1).dropna()
    spread_diff = spread.diff().dropna()
    
    # Align
    df = pd.DataFrame({
        'diff': spread_diff,
        'lag': spread_lag
    }).dropna()
    
    # Regress diff on lagged level
    from sklearn.linear_model import LinearRegression
    model = LinearRegression(fit_intercept=True)
    model.fit(df[['lag']], df['diff'])
    
    theta = model.coef_[0]
    
    # Half-life = -ln(2) / theta
    if theta < 0:
        half_life = -np.log(2) / theta
        return float(half_life)
    else:
        return float('inf')  # Not mean reverting


def calculate_z_score(spread: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate rolling z-score of spread
    
    Args:
        spread: Spread series
        window: Rolling window size
    
    Returns:
        Z-score series
    """
    mean = spread.rolling(window=window).mean()
    std = spread.rolling(window=window).std()
    
    z_score = (spread - mean) / std
    return z_score
