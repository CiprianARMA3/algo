"""
Trading recommendation system
Generates buy/hold/sell signals based on quantitative indicators
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Literal
from data.models import AnalysisResponse


def calculate_trading_signal(
    analysis: Dict,
    price_series: pd.Series,
    returns: pd.Series
) -> Dict[str, any]:
    """
    Calculate trading recommendation based on multiple quantitative factors
    
    Args:
        analysis: Dictionary with all analysis results
        price_series: Historical prices
        returns: Return series
    
    Returns:
        Dictionary with recommendation and confidence
    """
    
    signals = []
    weights = []
    
    # 1. Hurst Exponent Signal (30% weight)
    hurst = analysis.get('signal_processing', {}).get('hurst_exponent')
    if hurst is not None:
        if hurst < 0.45:
            # Strong mean reversion - sell if overextended, buy if oversold
            recent_return = (price_series.iloc[-1] / price_series.iloc[-20] - 1)
            if recent_return > 0.05:  # Up 5% in 20 days - overbought
                signals.append(-1)
            elif recent_return < -0.05:  # Down 5% - oversold
                signals.append(1)
            else:
                signals.append(0)
        elif hurst > 0.55:
            # Trending - follow momentum
            momentum = (price_series.iloc[-1] / price_series.iloc[-20] - 1)
            if momentum > 0:
                signals.append(1)
            else:
                signals.append(-1)
        else:
            # Random walk
            signals.append(0)
        weights.append(0.30)
    
    # 2. Regime Signal (25% weight)
    regime = analysis.get('regime')
    if regime:
        current_regime = regime.get('current_regime')
        regime_desc = regime.get('regime_descriptions', {}).get(current_regime, '')
        regime_prob = regime.get('regime_probabilities', [0, 0, 0])[current_regime]
        
        if 'Bull' in regime_desc and regime_prob > 0.6:
            signals.append(1)
        elif 'Bear' in regime_desc and regime_prob > 0.6:
            signals.append(-1)
        else:
            signals.append(0)
        weights.append(0.25)
    
    # 3. Volatility Signal (15% weight)
    volatility = analysis.get('volatility')
    if volatility:
        current_vol = volatility.get('annualized_volatility', 0)
        # High volatility = risky, reduce exposure
        if current_vol > 0.40:  # > 40% annual vol
            signals.append(-0.5)  # Reduce position
        elif current_vol < 0.15:  # < 15% annual vol
            signals.append(0.5)  # Safe to add
        else:
            signals.append(0)
        weights.append(0.15)
    
    # 4. Momentum Signal (20% weight)
    price_change = analysis.get('price_change_pct', 0)
    sharpe = analysis.get('metrics', {}).get('sharpe_ratio', 0)
    
    if sharpe > 1.5:  # Strong risk-adjusted returns
        if price_change > 0:
            signals.append(1)
        else:
            signals.append(0.5)
    elif sharpe < 0.5:
        if price_change < 0:
            signals.append(-1)
        else:
            signals.append(-0.5)
    else:
        signals.append(0)
    weights.append(0.20)
    
    # 5. Statistical Signal (10% weight)
    cointegration = analysis.get('cointegration')
    if cointegration:
        is_stationary = cointegration.get('is_stationary', False)
        if not is_stationary:
            # Non-stationary prices often trend
            if price_change > 2:
                signals.append(1)
            elif price_change < -2:
                signals.append(-1)
            else:
                signals.append(0)
        else:
            # Stationary = mean reverting
            if price_change > 3:
                signals.append(-1)  # Sell overbought
            elif price_change < -3:
                signals.append(1)  # Buy oversold
            else:
                signals.append(0)
        weights.append(0.10)
    
    # Calculate weighted signal
    if not signals:
        return {
            'recommendation': 'HOLD',
            'confidence': 0.0,
            'signal_strength': 0.0,
            'reasoning': 'Insufficient data for recommendation'
        }
    
    weights_array = np.array(weights)
    weights_array = weights_array / weights_array.sum()  # Normalize
    
    weighted_signal = np.average(signals, weights=weights_array)
    
    # Convert to recommendation
    if weighted_signal > 0.3:
        recommendation = 'BUY'
        confidence = min(abs(weighted_signal) * 100, 100)
    elif weighted_signal < -0.3:
        recommendation = 'SELL'
        confidence = min(abs(weighted_signal) * 100, 100)
    else:
        recommendation = 'HOLD'
        confidence = 100 - abs(weighted_signal) * 100
    
    # Generate reasoning
    reasoning_parts = []
    
    if hurst is not None:
        if hurst < 0.45:
            reasoning_parts.append(f"Mean reverting (H={hurst:.2f})")
        elif hurst > 0.55:
            reasoning_parts.append(f"Trending (H={hurst:.2f})")
    
    if regime:
        regime_desc = regime.get('regime_descriptions', {}).get(regime.get('current_regime', 0), '')
        reasoning_parts.append(regime_desc)
    
    if volatility:
        vol_pct = volatility.get('annualized_volatility', 0) * 100
        if vol_pct > 40:
            reasoning_parts.append(f"High volatility ({vol_pct:.1f}%)")
        elif vol_pct < 15:
            reasoning_parts.append(f"Low volatility ({vol_pct:.1f}%)")
    
    if sharpe > 1.5:
        reasoning_parts.append(f"Strong Sharpe ({sharpe:.2f})")
    elif sharpe < 0.5:
        reasoning_parts.append(f"Weak Sharpe ({sharpe:.2f})")
    
    reasoning = " | ".join(reasoning_parts) if reasoning_parts else "Based on technical analysis"
    
    return {
        'recommendation': recommendation,
        'confidence': round(confidence, 1),
        'signal_strength': round(weighted_signal, 3),
        'reasoning': reasoning
    }
