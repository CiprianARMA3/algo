"""
Pydantic models for data validation and API responses
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime


class OHLCVData(BaseModel):
    """OHLCV candlestick data point"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class SymbolInfo(BaseModel):
    """Symbol information"""
    symbol: str
    name: str
    type: Literal["stock", "forex", "crypto"]
    exchange: Optional[str] = None


class CointegrationResult(BaseModel):
    """Cointegration test results"""
    adf_statistic: float
    adf_pvalue: float
    adf_critical_values: Dict[str, float]
    is_stationary: bool
    kpss_statistic: Optional[float] = None
    kpss_pvalue: Optional[float] = None
    kpss_critical_values: Optional[Dict[str, float]] = None


class PCAResult(BaseModel):
    """Principal Component Analysis results"""
    explained_variance_ratio: List[float]
    cumulative_variance_ratio: List[float]
    n_components: int
    eigenvalues: List[float]
    s_score: Optional[float] = None


class VolatilityForecast(BaseModel):
    """Volatility model forecast"""
    model_type: str  # GARCH, GJR-GARCH, EGARCH
    current_volatility: float
    forecast_horizon: int
    forecasted_volatility: List[float]
    annualized_volatility: float
    parameters: Dict[str, float]


class RegimeDetection(BaseModel):
    """Hidden Markov Model regime detection"""
    current_regime: int
    regime_probabilities: List[float]
    regime_descriptions: Dict[int, str]
    n_states: int


class MicrostructureMetrics(BaseModel):
    """Market microstructure indicators"""
    order_book_imbalance: Optional[float] = None
    order_flow_imbalance: Optional[float] = None
    vpin: Optional[float] = None
    kyle_lambda: Optional[float] = None
    amihud_illiquidity: Optional[float] = None


class SignalProcessingResult(BaseModel):
    """Signal processing outputs"""
    fractional_diff_order: Optional[float] = None
    fractional_diff_series: Optional[List[float]] = None
    wavelet_denoised: Optional[List[float]] = None
    dominant_frequency: Optional[float] = None
    hurst_exponent: Optional[float] = None


class KalmanFilterState(BaseModel):
    """Kalman filter state for pairs trading"""
    hedge_ratio: float
    spread: float
    spread_mean: float
    spread_std: float
    z_score: float


class TradingRecommendation(BaseModel):
    """Trading position recommendation"""
    recommendation: Literal["BUY", "SELL", "HOLD"]
    confidence: float  # 0-100
    signal_strength: float  # -1 to 1
    reasoning: str


class AnalysisResponse(BaseModel):
    """Complete analysis response for a symbol"""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    lookback_days: int
    
    # Price data summary
    current_price: float
    price_change_pct: float
    
    # Statistical tests
    cointegration: Optional[CointegrationResult] = None
    
    # Dimensionality reduction
    pca: Optional[PCAResult] = None
    
    # Volatility
    volatility: Optional[VolatilityForecast] = None
    
    # Regime
    regime: Optional[RegimeDetection] = None
    
    # Microstructure
    microstructure: Optional[MicrostructureMetrics] = None
    
    # Signal processing
    signal_processing: Optional[SignalProcessingResult] = None
    
    # Trading recommendation
    recommendation: Optional[TradingRecommendation] = None
    
    # Additional metrics
    metrics: Dict[str, float] = Field(default_factory=dict)


class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis"""
    symbols: List[str] = Field(..., min_length=1, max_length=50)
    lookback_days: int = Field(default=252, ge=30, le=2520)
    indicators: Optional[List[str]] = None  # Specific indicators to calculate


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
