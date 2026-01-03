'use client';

import { useEffect, useRef } from 'react';
import { createChart, IChartApi, ISeriesApi } from 'lightweight-charts';

interface CandlestickChartProps {
    data: Array<{
        time: string;
        open: number;
        high: number;
        low: number;
        close: number;
    }>;
    symbol: string;
}

export default function CandlestickChart({ data, symbol }: CandlestickChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Create chart
        const chart = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 500,
            layout: {
                background: { color: '#111827' },
                textColor: '#d1d5db',
            },
            grid: {
                vertLines: { color: '#1f2937' },
                horzLines: { color: '#1f2937' },
            },
            timeScale: {
                borderColor: '#374151',
                timeVisible: true,
            },
            rightPriceScale: {
                borderColor: '#374151',
            },
        });

        chartRef.current = chart;

        // Add candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderUpColor: '#10b981',
            borderDownColor: '#ef4444',
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        });

        seriesRef.current = candlestickSeries;

        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, []);

    // Update data when it changes
    useEffect(() => {
        if (seriesRef.current && data.length > 0) {
            const formattedData = data.map(d => ({
                time: d.time.split('T')[0],
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close,
            }));

            seriesRef.current.setData(formattedData);
            chartRef.current?.timeScale().fitContent();
        }
    }, [data]);

    return (
        <div className="glass rounded-xl p-4">
            <h2 className="text-xl font-semibold mb-4 text-gray-200">
                {symbol} - Price Chart
            </h2>
            <div ref={chartContainerRef} className="w-full" />
        </div>
    );
}
