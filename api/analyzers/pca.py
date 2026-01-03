"""
Principal Component Analysis for dimensionality reduction
Used for eigenportfolio construction and statistical arbitrage
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, List
from data.models import PCAResult


def compute_pca(
    returns_df: pd.DataFrame,
    n_components: Optional[int] = None,
    variance_threshold: float = 0.95
) -> Tuple[PCA, np.ndarray, StandardScaler]:
    """
    Perform PCA on returns data
    
    Args:
        returns_df: DataFrame with returns for multiple assets
        n_components: Number of components (None for auto based on variance threshold)
        variance_threshold: Cumulative variance to explain
    
    Returns:
        Tuple of (PCA model, transformed data, scaler)
    """
    # Standardize the data
    scaler = StandardScaler()
    returns_scaled = scaler.fit_transform(returns_df.fillna(0))
    
    # Fit PCA
    if n_components is None:
        # Determine components to explain variance_threshold
        pca_full = PCA()
        pca_full.fit(returns_scaled)
        cumsum = np.cumsum(pca_full.explained_variance_ratio_)
        n_components = int(np.argmax(cumsum >= variance_threshold) + 1)
    
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(returns_scaled)
    
    return pca, principal_components, scaler


def calculate_eigenportfolios(
    returns_df: pd.DataFrame,
    n_components: int = 5
) -> PCAResult:
    """
    Calculate eigenportfolios from return data
    
    Args:
        returns_df: DataFrame with asset returns (columns = assets)
        n_components: Number of principal components
    
    Returns:
        PCAResult object
    """
    pca, components, scaler = compute_pca(returns_df, n_components=n_components)
    
    explained_var = pca.explained_variance_ratio_.tolist()
    cumulative_var = np.cumsum(pca.explained_variance_ratio_).tolist()
    eigenvalues = pca.explained_variance_.tolist()
    
    return PCAResult(
        explained_variance_ratio=explained_var,
        cumulative_variance_ratio=cumulative_var,
        n_components=n_components,
        eigenvalues=eigenvalues
    )


def calculate_factor_loadings(
    returns_df: pd.DataFrame,
    n_components: int = 5
) -> pd.DataFrame:
    """
    Calculate factor loadings (correlation between assets and factors)
    
    Args:
        returns_df: DataFrame with asset returns
        n_components: Number of factors
    
    Returns:
        DataFrame of factor loadings (assets x factors)
    """
    pca, components, scaler = compute_pca(returns_df, n_components=n_components)
    
    # Loadings = eigenvectors * sqrt(eigenvalues)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    
    loadings_df = pd.DataFrame(
        loadings,
        index=returns_df.columns,
        columns=[f'PC{i+1}' for i in range(n_components)]
    )
    
    return loadings_df


def calculate_s_score(
    asset_returns: pd.Series,
    factor_returns: pd.DataFrame,
    window: int = 60
) -> pd.Series:
    """
    Calculate S-Score (standardized residual) for statistical arbitrage
    
    Args:
        asset_returns: Returns of the target asset
        factor_returns: Returns of the factors/eigenportfolios
        window: Rolling window for standardization
    
    Returns:
        S-Score series
    """
    from sklearn.linear_model import LinearRegression
    
    # Align data
    df = pd.concat([asset_returns, factor_returns], axis=1).dropna()
    y = df[asset_returns.name].values.reshape(-1, 1)
    X = df[factor_returns.columns].values
    
    # Fit regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate residuals
    predictions = model.predict(X)
    residuals = y.flatten() - predictions.flatten()
    
    residual_series = pd.Series(residuals, index=df.index)
    
    # Standardize residuals (S-Score)
    rolling_mean = residual_series.rolling(window=window).mean()
    rolling_std = residual_series.rolling(window=window).std()
    
    s_score = (residual_series - rolling_mean) / rolling_std
    
    return s_score


def analyze_pca_portfolio(
    returns_df: pd.DataFrame,
    target_asset: str,
    n_factors: int = 3
) -> Dict[str, any]:
    """
    Complete PCA-based statistical arbitrage analysis
    
    Args:
        returns_df: DataFrame with returns for asset universe
        target_asset: Asset to analyze
        n_factors: Number of factors to use
    
    Returns:
        Dictionary with analysis results
    """
    # Calculate eigenportfolios
    pca_result = calculate_eigenportfolios(returns_df, n_components=n_factors)
    
    # Get factor loadings
    loadings = calculate_factor_loadings(returns_df, n_components=n_factors)
    
    # Extract target asset's returns
    asset_returns = returns_df[target_asset]
    
    # Reconstruct factor returns
    pca, components, scaler = compute_pca(returns_df, n_components=n_factors)
    factor_returns_array = components
    factor_returns = pd.DataFrame(
        factor_returns_array,
        index=returns_df.index[: len(factor_returns_array)],
        columns=[f'Factor{i+1}' for i in range(n_factors)]
    )
    
    # Calculate S-Score
    s_score = calculate_s_score(asset_returns, factor_returns, window=60)
    
    return {
        'pca_result': pca_result,
        'factor_loadings': loadings.loc[target_asset].to_dict(),
        's_score_current': float(s_score.iloc[-1]) if len(s_score) > 0 else None,
        's_score_series': s_score
    }


from typing import Optional
