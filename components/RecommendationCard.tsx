'use client';

import { TradingRecommendation } from '@/lib/api';
import { TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react';

interface RecommendationCardProps {
    recommendation: TradingRecommendation | null | undefined;
}

export default function RecommendationCard({ recommendation }: RecommendationCardProps) {
    if (!recommendation) {
        return (
            <div className="glass rounded-xl p-6">
                <div className="flex items-center gap-3 mb-3">
                    <AlertCircle className="w-6 h-6 text-gray-400" />
                    <h3 className="text-lg font-semibold text-gray-300">Trading Recommendation</h3>
                </div>
                <p className="text-gray-500">Analyzing market conditions...</p>
            </div>
        );
    }

    const getRecommendationColor = (rec: string) => {
        switch (rec) {
            case 'BUY':
                return {
                    bg: 'from-green-900/50 to-green-800/30',
                    border: 'border-green-500/50',
                    text: 'text-green-400',
                    icon: TrendingUp,
                    glow: 'shadow-green-500/20',
                };
            case 'SELL':
                return {
                    bg: 'from-red-900/50 to-red-800/30',
                    border: 'border-red-500/50',
                    text: 'text-red-400',
                    icon: TrendingDown,
                    glow: 'shadow-red-500/20',
                };
            case 'HOLD':
                return {
                    bg: 'from-yellow-900/50 to-yellow-800/30',
                    border: 'border-yellow-500/50',
                    text: 'text-yellow-400',
                    icon: Minus,
                    glow: 'shadow-yellow-500/20',
                };
            default:
                return {
                    bg: 'from-gray-900/50 to-gray-800/30',
                    border: 'border-gray-500/50',
                    text: 'text-gray-400',
                    icon: Minus,
                    glow: 'shadow-gray-500/20',
                };
        }
    };

    const colors = getRecommendationColor(recommendation.recommendation);
    const Icon = colors.icon;

    return (
        <div className={`glass rounded-xl p-6 border-2 ${colors.border} shadow-xl ${colors.glow}`}>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-200">Trading Recommendation</h3>
                <Icon className={`w-6 h-6 ${colors.text}`} />
            </div>

            {/* Main Recommendation */}
            <div className={`bg-gradient-to-br ${colors.bg} rounded-lg p-6 mb-4`}>
                <div className="text-center">
                    <p className="text-sm text-gray-400 mb-2">Position</p>
                    <p className={`text-5xl font-bold ${colors.text} mb-3`}>
                        {recommendation.recommendation}
                    </p>
                    <div className="flex items-center justify-center gap-2">
                        <div className="flex-1 bg-gray-800 rounded-full h-3 overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${recommendation.recommendation === 'BUY'
                                        ? 'from-green-600 to-green-400'
                                        : recommendation.recommendation === 'SELL'
                                            ? 'from-red-600 to-red-400'
                                            : 'from-yellow-600 to-yellow-400'
                                    }`}
                                style={{ width: `${recommendation.confidence}%` }}
                            />
                        </div>
                        <span className={`text-2xl font-bold ${colors.text} min-w-[60px]`}>
                            {recommendation.confidence.toFixed(0)}%
                        </span>
                    </div>
                </div>
            </div>

            {/* Signal Strength Indicator */}
            <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-400">Signal Strength</span>
                    <span className="text-sm font-mono text-gray-300">
                        {recommendation.signal_strength.toFixed(3)}
                    </span>
                </div>
                <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
                    {/* Center line */}
                    <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-gray-600 z-10"></div>
                    {/* Signal bar */}
                    <div
                        className={`absolute top-0 bottom-0 ${recommendation.signal_strength >= 0
                                ? 'bg-gradient-to-r from-green-600 to-green-400'
                                : 'bg-gradient-to-l from-red-600 to-red-400'
                            }`}
                        style={{
                            left: recommendation.signal_strength >= 0 ? '50%' : `${50 + recommendation.signal_strength * 50}%`,
                            right: recommendation.signal_strength >= 0 ? `${50 - recommendation.signal_strength * 50}%` : '50%',
                        }}
                    />
                </div>
                <div className="flex justify-between mt-1 text-xs text-gray-500">
                    <span>Strong Sell</span>
                    <span>Neutral</span>
                    <span>Strong Buy</span>
                </div>
            </div>

            {/* Reasoning */}
            <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-xs text-gray-500 mb-1">Analysis Reasoning:</p>
                <p className="text-sm text-gray-300">{recommendation.reasoning}</p>
            </div>

            {/* Disclaimer */}
            <div className="mt-4 pt-4 border-t border-gray-700">
                <p className="text-xs text-gray-500 italic">
                    ⚠️ This is not financial advice. Algorithmic recommendations should be used alongside your own research.
                </p>
            </div>
        </div>
    );
}
