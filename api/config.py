"""
Configuration management for the Quantitative Analysis API
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Quantitative Analysis API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Institutional-grade algorithmic trading analyzer"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",
    ]
    
    # Redis Cache
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour
    
    # Data Provider Settings
    DATA_PROVIDER: str = "yfinance"  # yfinance, alphavantage, polygon
    ALPHAVANTAGE_API_KEY: str | None = None
    POLYGON_API_KEY: str | None = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Analysis Settings
    DEFAULT_LOOKBACK_DAYS: int = 252  # 1 trading year
    MIN_LOOKBACK_DAYS: int = 30
    MAX_LOOKBACK_DAYS: int = 2520  # 10 years
    
    # Statistical Parameters
    ADF_SIGNIFICANCE_LEVEL: float = 0.05
    KPSS_SIGNIFICANCE_LEVEL: float = 0.05
    GARCH_P: int = 1
    GARCH_Q: int = 1
    HMM_N_STATES: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
