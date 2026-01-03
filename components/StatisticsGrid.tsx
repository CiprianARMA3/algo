'use client';

import { AnalysisResponse } from '@/lib/api';
import { TrendingUp, TrendingDown, Activity, BarChart3, Zap } from 'lucide-react';

interface StatisticsGridProps {
    analysis: AnalysisResponse | null;
    loading: boolean;
}

export default function StatisticsGrid({ analysis, loading }: StatisticsGridProps) {
    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                    <div key={i} className="glass rounded-xl p-6 animate-pulse">
                        <div className="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
                        <div className="h-10 bg-gray-700 rounded w-1/2"></div>
                    </div>
                ))}
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="glass rounded-xl p-12 text-center">
                <p className="text-gray-400 text-lg">Select a symbol to view analysis</p>
            </div>
        );
    }

    const statCards = [
        {
            title: 'Current Price',
            value: `$${analysis.current_price.toFixed(2)}`,
            change: analysis.price_change_pct,
            icon: Activity,
            color: analysis.price_change_pct >= 0 ? 'green' : 'red',
        },
        {
            title: 'Volatility (Annual)',
            value: analysis.volatility ? `${(analysis.volatility.annualized_volatility * 100).toFixed(2)}%` : 'N/A',
            subtitle: analysis.volatility?.model_type || '',
            icon: BarChart3,
            color: 'blue',
        },
        {
            title: 'Sharpe Ratio',
            value: analysis.metrics.sharpe_ratio?.toFixed(3) || 'N/A',
            icon: TrendingUp,
            color: 'purple',
        },
        {
            title: 'Hurst Exponent',
            value: analysis.signal_processing?.hurst_exponent?.toFixed(3) || 'N/A',
            subtitle: getHurstInterpretation(analysis.signal_processing?.hurst_exponent),
            icon: Zap,
            color: 'yellow',
        },
        {
            title: 'Max Drawdown',
            value: analysis.metrics.max_drawdown ? `${(analysis.metrics.max_drawdown * 100).toFixed(2)}%` : 'N/A',
            icon: TrendingDown,
            color: 'red',
        },
        {
            title: 'Current Regime',
            value: analysis.regime ? analysis.regime.regime_descriptions[analysis.regime.current_regime] : 'N/A',
            subtitle: analysis.regime ? `Confidence: ${(analysis.regime.regime_probabilities[analysis.regime.current_regime] * 100).toFixed(1)}%` : '',
            icon: Activity,
            color: 'green',
        },
    ];

    return (
        <div className="space-y-6">
            {/* Main Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {statCards.map((card, index) => {
                    const Icon = card.icon;
                    return (
                        <div key={index} className="glass rounded-xl p-6 hover:scale-105 transition-transform">
                            <div className="flex items-start justify-between mb-3">
                                <h3 className="text-sm font-medium text-gray-400">{card.title}</h3>
                                <Icon className={`w-5 h-5 text-${card.color}-500`} />
                            </div>
                            <div className="flex items-baseline gap-2">
                                <p className={`text-2xl font-bold text-${card.color}-400`}>
                                    {card.value}
                                </p>
                                {card.change !== undefined && (
                                    <span className={`text-sm ${card.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {card.change >= 0 ? '+' : ''}{card.change.toFixed(2)}%
                                    </span>
                                )}
                            </div>
                            {card.subtitle && (
                                <p className="text-xs text-gray-500 mt-2">{card.subtitle}</p>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Detailed Statistical Tests */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Stationarity Tests */}
                {analysis.cointegration && (
                    <div className="glass rounded-xl p-6">
                        <h3 className="text-lg font-semibold mb-4 text-gray-200">Stationarity Tests</h3>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-gray-400">ADF Test</span>
                                <span className={`px-3 py-1 rounded-full text-sm ${analysis.cointegration.is_stationary
                                        ? 'bg-green-900 text-green-300'
                                        : 'bg-red-900 text-red-300'
                                    }`}>
                                    {analysis.cointegration.is_stationary ? 'Stationary' : 'Non-Stationary'}
                                </span>
                            </div>
                            <div className="text-sm text-gray-500">
                                <p>Statistic: {analysis.cointegration.adf_statistic.toFixed(4)}</p>
                                <p>P-value: {analysis.cointegration.adf_pvalue.toFixed(4)}</p>
                            </div>
                            {analysis.cointegration.kpss_statistic && (
                                <div className="text-sm text-gray-500 pt-2 border-t border-gray-700">
                                    <p>KPSS Statistic: {analysis.cointegration.kpss_statistic.toFixed(4)}</p>
                                    <p>KPSS P-value: {analysis.cointegration.kpss_pvalue?.toFixed(4) || 'N/A'}</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Additional Metrics */}
                <div className="glass rounded-xl p-6">
                    <h3 className="text-lg font-semibold mb-4 text-gray-200">Distribution Metrics</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Skewness</span>
                            <span className="text-gray-200 font-mono">{analysis.metrics.skewness?.toFixed(4) || 'N/A'}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Kurtosis</span>
                            <span className="text-gray-200 font-mono">{analysis.metrics.kurtosis?.toFixed(4) || 'N/A'}</span>
                        </div>
                        {analysis.signal_processing?.dominant_frequency && (
                            <>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Dominant Period</span>
                                    <span className="text-gray-200 font-mono">
                                        {analysis.metrics.dominant_period_days?.toFixed(1) || 'N/A'} days
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Fractional Diff Order</span>
                                    <span className="text-gray-200 font-mono">
                                        {analysis.signal_processing.fractional_diff_order?.toFixed(2) || 'N/A'}
                                    </span>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

function getHurstInterpretation(hurst?: number): string {
    if (!hurst) return '';
    if (hurst < 0.5) return 'Mean Reverting';
    if (hurst > 0.5) return 'Trending';
    return 'Random Walk';
}
