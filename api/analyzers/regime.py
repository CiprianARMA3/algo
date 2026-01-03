"""
Hidden Markov Model for regime detection
Identifies market regimes (bull, bear, sideways)
"""
import numpy as np
import pandas as pd
from hmmlearn import hmm
from typing import Dict, List
from data.models import RegimeDetection


def fit_hmm(
    returns: pd.Series,
    n_states: int = 3,
    n_iter: int = 100,
    random_state: int = 42
) -> hmm.GaussianHMM:
    """
    Fit Hidden Markov Model to returns
    
    Args:
        returns: Return series
        n_states: Number of hidden states (regimes)
        n_iter: Maximum iterations for EM algorithm
        random_state: Random seed
    
    Returns:
        Fitted GaussianHMM model
    """
    # Prepare data
    X = returns.dropna().values.reshape(-1, 1)
    
    # Initialize model
    model = hmm.GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=n_iter,
        random_state=random_state
    )
    
    # Fit model
    model.fit(X)
    
    return model


def detect_regime(
    returns: pd.Series,
    n_states: int = 3,
    regime_names: Dict[int, str] = None
) -> RegimeDetection:
    """
    Detect current market regime using HMM
    
    Args:
        returns: Historical returns
        n_states: Number of regimes
        regime_names: Optional custom regime names
    
    Returns:
        RegimeDetection object
    """
    # Fit model
    model = fit_hmm(returns, n_states=n_states)
    
    # Predict regimes
    X = returns.dropna().values.reshape(-1, 1)
    hidden_states = model.predict(X)
    
    # Get current regime (last state)
    current_regime = int(hidden_states[-1])
    
    # Calculate regime probabilities for current observation
    posteriors = model.predict_proba(X)
    current_probabilities = posteriors[-1, :].tolist()
    
    # Characterize regimes by mean and variance
    means = model.means_.flatten()
    variances = model.covars_.flatten()
    
    # Auto-generate regime descriptions if not provided
    if regime_names is None:
        regime_descriptions = {}
        sorted_indices = np.argsort(means)
        
        if n_states == 2:
            regime_descriptions[sorted_indices[0]] = "Bear Market (Low Mean)"
            regime_descriptions[sorted_indices[1]] = "Bull Market (High Mean)"
        elif n_states == 3:
            regime_descriptions[sorted_indices[0]] = "Bear Market (Negative Mean)"
            regime_descriptions[sorted_indices[1]] = "Sideways (Low Volatility)"
            regime_descriptions[sorted_indices[2]] = "Bull Market (Positive Mean)"
        else:
            for i, idx in enumerate(sorted_indices):
                regime_descriptions[idx] = f"Regime {i+1} (μ={means[idx]:.4f}, σ²={variances[idx]:.4f})"
    else:
        regime_descriptions = regime_names
    
    return RegimeDetection(
        current_regime=current_regime,
        regime_probabilities=current_probabilities,
        regime_descriptions=regime_descriptions,
        n_states=n_states
    )


def get_regime_history(
    returns: pd.Series,
    n_states: int = 3
) -> pd.Series:
    """
    Get historical regime classifications
    
    Args:
        returns: Return series
        n_states: Number of regimes
    
    Returns:
        Series of regime labels
    """
    model = fit_hmm(returns, n_states=n_states)
    X = returns.dropna().values.reshape(-1, 1)
    hidden_states = model.predict(X)
    
    return pd.Series(hidden_states, index=returns.dropna().index)


def calculate_regime_statistics(
    returns: pd.Series,
    regimes: pd.Series
) -> Dict[int, Dict[str, float]]:
    """
    Calculate statistics for each regime
    
    Args:
        returns: Return series
        regimes: Regime labels
    
    Returns:
        Dictionary mapping regime to statistics
    """
    stats = {}
    
    for regime in regimes.unique():
        regime_returns = returns[regimes == regime]
        
        stats[int(regime)] = {
            'mean_return': float(regime_returns.mean()),
            'volatility': float(regime_returns.std()),
            'sharpe_ratio': float(regime_returns.mean() / regime_returns.std()) if regime_returns.std() > 0 else 0.0,
            'frequency': float(len(regime_returns) / len(returns)),
            'max_return': float(regime_returns.max()),
            'min_return': float(regime_returns.min())
        }
    
    return stats
