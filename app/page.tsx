'use client';

import { useState, useEffect } from 'react';
import { api, AnalysisResponse, OHLCVData } from '@/lib/api';
import CandlestickChart from '@/components/CandlestickChart';
import SymbolSelector from '@/components/SymbolSelector';
import StatisticsGrid from '@/components/StatisticsGrid';
import RecommendationCard from '@/components/RecommendationCard';
import { Activity, RefreshCw } from 'lucide-react';

export default function Home() {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');
  const [ohlcvData, setOhlcvData] = useState<OHLCVData[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    if (selectedSymbol) {
      loadData();
    }
  }, [selectedSymbol]);

  const loadData = async () => {
    setLoading(true);
    try {
      // Fetch OHLCV data  
      const ohlcvResponse = await api.getOHLCV(selectedSymbol, '1y');
      setOhlcvData(ohlcvResponse.data);

      // Fetch analysis
      const analysisResponse = await api.analyze(selectedSymbol, 252);
      setAnalysis(analysisResponse);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = ohlcvData.map(d => ({
    time: d.timestamp,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
  }));

  return (
    <main className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              Quantitative Analysis Dashboard
            </h1>
            <p className="text-gray-400">
              Institutional-grade algorithmic trading analyzer
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right text-sm text-gray-400">
              <p>Last Update</p>
              <p className="font-mono">{lastUpdate.toLocaleTimeString()}</p>
            </div>
            <button
              onClick={loadData}
              disabled={loading}
              className="glass px-4 py-2 rounded-lg hover:bg-gray-700 transition-all flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar - Symbol Selector */}
        <div className="lg:col-span-1">
          <SymbolSelector
            selectedSymbol={selectedSymbol}
            onSelect={setSelectedSymbol}
          />
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Trading Recommendation */}
          <RecommendationCard recommendation={analysis?.recommendation} />

          {/* Price Chart */}
          <CandlestickChart data={chartData} symbol={selectedSymbol} />

          {/* Statistics Grid */}
          <StatisticsGrid analysis={analysis} loading={loading} />

          {/* Volatility Forecast Chart */}
          {analysis?.volatility && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-200">
                Volatility Forecast ({analysis.volatility.model_type})
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {analysis.volatility.forecasted_volatility.map((vol, index) => (
                  <div key={index} className="bg-gray-800 rounded-lg p-3 text-center">
                    <p className="text-xs text-gray-500 mb-1">Day {index + 1}</p>
                    <p className="text-lg font-bold text-blue-400">
                      {(vol * 100).toFixed(2)}%
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Regime Probabilities */}
          {analysis?.regime && (
            <div className="glass rounded-xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-gray-200">
                Market Regime Detection (HMM)
              </h3>
              <div className="space-y-3">
                {analysis.regime.regime_probabilities.map((prob, index) => (
                  <div key={index}>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-400">
                        {analysis.regime!.regime_descriptions[index]}
                      </span>
                      <span className="text-sm font-medium text-gray-200">
                        {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-800 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${index === analysis.regime.current_regime
                          ? 'bg-gradient-to-r from-blue-500 to-purple-500'
                          : 'bg-gray-600'
                          }`}
                        style={{ width: `${prob * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-12 text-center text-gray-500 text-sm">
        <p>Powered by advanced econometrics, signal processing, and machine learning</p>
        <p className="mt-1">Data provided by Yahoo Finance</p>
      </footer>
    </main>
  );
}
