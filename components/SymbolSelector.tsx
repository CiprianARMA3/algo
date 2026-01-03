'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { Search } from 'lucide-react';

interface SymbolSelectorProps {
    onSelect: (symbol: string) => void;
    selectedSymbol?: string;
}

export default function SymbolSelector({ onSelect, selectedSymbol }: SymbolSelectorProps) {
    const [symbols, setSymbols] = useState<string[]>([]);
    const [filter, setFilter] = useState<'all' | 'stocks' | 'forex'>('stocks');
    const [search, setSearch] = useState('');
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        loadSymbols();
    }, [filter]);

    const loadSymbols = async () => {
        try {
            let data: string[];
            if (filter === 'stocks') {
                data = await api.getStockSymbols();
            } else if (filter === 'forex') {
                data = await api.getForexSymbols();
            } else {
                const allSymbols = await api.getSymbols();
                data = allSymbols.map(s => s.symbol);
            }
            setSymbols(data);
        } catch (error) {
            console.error('Error loading symbols:', error);
        }
    };

    const filteredSymbols = symbols.filter(symbol =>
        symbol.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="glass rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 text-gray-200">Symbol Selection</h3>

            {/* Filter Buttons */}
            <div className="flex gap-2 mb-4">
                <button
                    onClick={() => setFilter('stocks')}
                    className={`px-4 py-2 rounded-lg transition-all ${filter === 'stocks'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                        }`}
                >
                    Stocks
                </button>
                <button
                    onClick={() => setFilter('forex')}
                    className={`px-4 py-2 rounded-lg transition-all ${filter === 'forex'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                        }`}
                >
                    Forex
                </button>
            </div>

            {/* Search Input */}
            <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                    type="text"
                    placeholder="Search symbols..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
            </div>

            {/* Symbol Grid */}
            <div className="max-h-96 overflow-y-auto">
                <div className="grid grid-cols-3 gap-2">
                    {filteredSymbols.slice(0, 50).map((symbol) => (
                        <button
                            key={symbol}
                            onClick={() => onSelect(symbol)}
                            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${selectedSymbol === symbol
                                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                                }`}
                        >
                            {symbol}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
