/**
 * API client for quantitative analysis backend
 */
import axios from 'axios';

const API_BASE_URL = '';

export interface OHLCVData {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

export interface TradingRecommendation {
    recommendation: 'BUY' | 'SELL' | 'HOLD';
    confidence: number;
    signal_strength: number;
    reasoning: string;
}

export interface AnalysisResponse {
    symbol: string;
    timestamp: string;
    lookback_days: number;
    current_price: number;
    price_change_pct: number;
    cointegration?: {
        adf_statistic: number;
        adf_pvalue: number;
        is_stationary: boolean;
        kpss_statistic?: number;
        kpss_pvalue?: number;
    };
    volatility?: {
        model_type: string;
        current_volatility: number;
        annualized_volatility: number;
        forecasted_volatility: number[];
        parameters: Record<string, number>;
    };
    regime?: {
        current_regime: number;
        regime_probabilities: number[];
        regime_descriptions: Record<number, string>;
        n_states: number;
    };
    signal_processing?: {
        fractional_diff_order: number;
        hurst_exponent: number;
        dominant_frequency: number;
    };
    recommendation?: TradingRecommendation;
    metrics: Record<string, number>;
}

export interface SymbolInfo {
    symbol: string;
    name: string;
    type: 'stock' | 'forex' | 'crypto';
    exchange?: string;
}

export const api = {
    // Get all available symbols
    async getSymbols(): Promise<SymbolInfo[]> {
        const response = await axios.get(`${API_BASE_URL}/api/data/symbols`);
        return response.data;
    },

    // Get stock symbols
    async getStockSymbols(): Promise<string[]> {
        const response = await axios.get(`${API_BASE_URL}/api/data/symbols/stocks`);
        return response.data;
    },

    // Get forex symbols
    async getForexSymbols(): Promise<string[]> {
        const response = await axios.get(`${API_BASE_URL}/api/data/symbols/forex`);
        return response.data;
    },

    // Get OHLCV data
    async getOHLCV(symbol: string, period: string = '1y'): Promise<{ symbol: string; data: OHLCVData[] }> {
        const response = await axios.get(`${API_BASE_URL}/api/data/ohlcv/${symbol}`, {
            params: { period }
        });
        return response.data;
    },

    // Get comprehensive analysis
    async analyze(symbol: string, lookbackDays: number = 252): Promise<AnalysisResponse> {
        const response = await axios.get(`${API_BASE_URL}/api/analyze/${symbol}`, {
            params: { lookback_days: lookbackDays }
        });
        return response.data;
    },

    // Get current price
    async getCurrentPrice(symbol: string): Promise<{ symbol: string; price: number }> {
        const response = await axios.get(`${API_BASE_URL}/api/data/price/${symbol}`);
        return response.data;
    },
};
