"""
Signal processing techniques for financial time series
Implements fractional differentiation, wavelet transforms, and FFT
"""
import numpy as np
import pandas as pd
import pywt
from scipy import signal as scipy_signal
from typing import Tuple, List, Optional, Dict
from data.models import SignalProcessingResult


def fractional_diff(
    series: pd.Series,
    d: float = 0.5,
    threshold: float = 1e-5
) -> pd.Series:
    """
    Fractional differentiation to achieve stationarity while preserving memory
    
    Based on Marcos Lopez de Prado's methodology
    
    Args:
        series: Price series to differentiate
        d: Differencing order (0 < d < 1 for fractional)
        threshold: Threshold for weight truncation
    
    Returns:
        Fractionally differentiated series
    """
    # Compute weights
    weights = [1.0]
    k = 1
    while abs(weights[-1]) > threshold:
        weight = -weights[-1] * (d - k + 1) / k
        weights.append(weight)
        k += 1
    
    weights = np.array(weights[::-1]).reshape(-1, 1)
    
    # Apply weights
    width = len(weights)
    result = pd.Series(index=series.index, dtype=float)
    
    for iloc in range(width, len(series)):
        result.iloc[iloc] = np.dot(
            weights.T,
            series.iloc[iloc-width:iloc].values.reshape(-1, 1)
        )[0, 0]
    
    return result.dropna()


def find_min_ffd(
    series: pd.Series,
    max_d: float = 1.0,
    threshold: float = 1e-5
) -> float:
    """
    Find minimum d for fractional differentiation that achieves stationarity
    
    Args:
        series: Price series
        max_d: Maximum d to test
        threshold: Weight threshold
    
    Returns:
        Minimum d value that passes ADF test
    """
    from statsmodels.tsa.stattools import adfuller
    
    for d in np.arange(0.0, max_d, 0.1):
        ffd_series = fractional_diff(series, d=d, threshold=threshold)
        
        if len(ffd_series) < 10:
            continue
        
        adf_result = adfuller(ffd_series.dropna(), regression='c', autolag='AIC')
        if adf_result[1] < 0.05:  # Stationary
            return float(d)
    
    return float(max_d)


def wavelet_denoise(
    series: pd.Series,
    wavelet: str = 'db4',
    level: Optional[int] = None,
    mode: str = 'soft'
) -> pd.Series:
    """
    Denoise time series using wavelet transform
    
    Args:
        series: Time series to denoise
        wavelet: Wavelet family ('db4', 'sym4', 'coif4')
        level: Decomposition level (None for auto)
        mode: Thresholding mode ('soft', 'hard')
    
    Returns:
        Denoised series
    """
    data = series.dropna().values
    
    # Determine decomposition level if not specified
    if level is None:
        level = pywt.dwt_max_level(len(data), wavelet)
        level = min(level, 6)  # Cap at 6 levels
    
    # Perform wavelet decomposition
    coeffs = pywt.wavedec(data, wavelet, level=level)
    
    # Calculate threshold using Donoho-Johnstone method
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    threshold = sigma * np.sqrt(2 * np.log(len(data)))
    
    # Apply thresholding to detail coefficients
    denoised_coeffs = [coeffs[0]]  # Keep approximation
    for detail in coeffs[1:]:
        if mode == 'soft':
            denoised = pywt.threshold(detail, threshold, mode='soft')
        else:
            denoised = pywt.threshold(detail, threshold, mode='hard')
        denoised_coeffs.append(denoised)
    
    # Reconstruct signal
    denoised_data = pywt.waverec(denoised_coeffs, wavelet)
    
    # Handle length mismatch
    if len(denoised_data) > len(data):
        denoised_data = denoised_data[:len(data)]
    
    return pd.Series(denoised_data, index=series.dropna().index)


def fft_analysis(
    series: pd.Series,
    sample_rate: float = 1.0
) -> Dict[str, np.ndarray]:
    """
    Fast Fourier Transform for frequency analysis
    
    Args:
        series: Time series
        sample_rate: Sampling rate (1.0 for daily data)
    
    Returns:
        Dictionary with frequencies and power spectrum
    """
    data = series.dropna().values
    n = len(data)
    
    # Perform FFT
    fft_values = np.fft.fft(data)
    frequencies = np.fft.fftfreq(n, d=1/sample_rate)
    
    # Power spectrum
    power = np.abs(fft_values) ** 2
    
    # Keep only positive frequencies
    positive_freq_idx = frequencies > 0
    
    return {
        'frequencies': frequencies[positive_freq_idx],
        'power_spectrum': power[positive_freq_idx],
        'dominant_frequency': float(frequencies[positive_freq_idx][np.argmax(power[positive_freq_idx])]),
        'period': float(1 / frequencies[positive_freq_idx][np.argmax(power[positive_freq_idx])])
    }


def calculate_hurst_exponent(series: pd.Series, max_lag: int = 20) -> float:
    """
    Calculate Hurst exponent for mean reversion / trending behavior
    
    H < 0.5: Mean reverting
    H = 0.5: Random walk
    H > 0.5: Trending
    
    Args:
        series: Price series
        max_lag: Maximum lag for R/S calculation
    
    Returns:
        Hurst exponent
    """
    lags = range(2, max_lag)
    tau = []
    
    for lag in lags:
        # Calculate standard deviation
        std = series.rolling(window=lag).std().dropna().values
        
        if len(std) == 0:
            continue
        
        # Calculate range
        rolling_mean = series.rolling(window=lag).mean().dropna()
        deviations = series[lag-1:len(rolling_mean)+lag-1] - rolling_mean.values
        cumulative_dev = deviations.cumsum()
        
        R = cumulative_dev.max() - cumulative_dev.min()
        
        # R/S ratio
        RS = R / std.mean() if std.mean() > 0 else 0
        tau.append(RS)
    
    # Fit log(R/S) vs log(lag)
    if len(tau) == 0:
        return 0.5
    
    log_lags = np.log(list(lags[:len(tau)]))
    log_tau = np.log(tau)
    
    # Linear regression
    coeffs = np.polyfit(log_lags, log_tau, 1)
    hurst = coeffs[0]
    
    return float(hurst)


def bandpass_filter(
    series: pd.Series,
    low_freq: float,
    high_freq: float,
    sample_rate: float = 1.0,
    order: int = 5
) -> pd.Series:
    """
    Apply bandpass filter to isolate specific frequency range
    
    Args:
        series: Time series
        low_freq: Low cutoff frequency
        high_freq: High cutoff frequency
        sample_rate: Sampling rate
        order: Filter order
    
    Returns:
        Filtered series
    """
    data = series.dropna().values
    
    # Nyquist frequency
    nyquist = 0.5 * sample_rate
    low = low_freq / nyquist
    high = high_freq / nyquist
    
    # Design filter
    b, a = scipy_signal.butter(order, [low, high], btype='band')
    
    # Apply filter
    filtered = scipy_signal.filtfilt(b, a, data)
    
    return pd.Series(filtered, index=series.dropna().index)
