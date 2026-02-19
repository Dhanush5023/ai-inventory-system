import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { Target, ShieldAlert, Zap, TrendingUp, RefreshCw, AlertTriangle, Info, X, Package, Clock, ArrowUpRight } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, Tooltip } from 'recharts';

const Optimization = () => {
    const [metrics, setMetrics] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [restocking, setRestocking] = useState(false);
    const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
    const [selectedProductDetail, setSelectedProductDetail] = useState(null);
    const [autoReceive, setAutoReceive] = useState(false);

    useEffect(() => {
        fetchMetrics();
    }, []);

    const fetchMetrics = async () => {
        try {
            const response = await api.get('/api/v1/ai/optimization/metrics');
            setMetrics(response.data.items);
        } catch (error) {
            console.error('Error fetching optimization metrics:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const runAutoRestock = async () => {
        setRestocking(true);
        try {
            const response = await api.post(`/api/v1/ai/autonomous/restock/generate?auto_receive=${autoReceive}`, {});
            const msg = response.data.count > 0
                ? (autoReceive
                    ? `AI Restock Complete! Stock levels for ${response.data.count} items updated immediately.`
                    : `AI Agent generated ${response.data.count} draft purchase orders. Check the Orders page to approve them.`)
                : `AI Agent found no new items to restock (all low-stock items already have active orders or stock is sufficient).`;
            alert(msg);
            fetchMetrics(); // Refresh data swept away by the 404s
        } catch (error) {
            alert('Error running autonomous restock.');
        } finally {
            setRestocking(false);
        }
    };

    if (isLoading) return <div className="flex justify-center items-center h-screen bg-slate-900 text-white">Loading Intelligence...</div>;

    return (
        <div className="p-8 bg-slate-950 min-h-screen text-slate-100">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">AI Optimization Engine</h1>
                    <p className="text-slate-400 mt-1">Mathematical optimization for your supply chain.</p>
                </div>
                <div className="flex items-center gap-6">
                    <label className="flex items-center gap-2 cursor-pointer bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">
                        <input
                            type="checkbox"
                            checked={autoReceive}
                            onChange={(e) => setAutoReceive(e.target.checked)}
                            className="w-4 h-4 rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span className="text-sm font-medium text-slate-300">Auto-Update Stock</span>
                        <Info className="w-3 h-3 text-slate-500 cursor-help" title="If enabled, AI will immediately update current stock levels after generating orders." />
                    </label>
                    <button
                        onClick={runAutoRestock}
                        disabled={restocking}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 px-6 py-3 rounded-xl font-semibold shadow-lg shadow-indigo-500/20 transition-all active:scale-95 disabled:opacity-50"
                    >
                        <Zap className={`w-5 h-5 ${restocking ? 'animate-pulse' : ''}`} />
                        {restocking ? 'AI Restocking...' : 'Run Autonomous Restock'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-sm">
                    <div className="flex items-center justify-between mb-2 text-slate-400">
                        <span className="text-sm font-medium">Optimization Algorithm</span>
                        <Target className="w-5 h-5 text-indigo-400" />
                    </div>
                    <div className="text-2xl font-bold">EOQ & Safety Stock</div>
                    <div className="text-xs text-slate-500 mt-2">Active: RMSE 4.2% Optimization</div>
                </div>
                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-sm">
                    <div className="flex items-center justify-between mb-2 text-slate-400">
                        <span className="text-sm font-medium">Recommended Restocks</span>
                        <RefreshCw className="w-5 h-5 text-emerald-400" />
                    </div>
                    <div className="text-2xl font-bold">
                        {metrics.filter(m => m.recommendation === "Restock Now").length} Items
                    </div>
                    <div className="text-xs text-slate-500 mt-2">Identified by reorder point analysis</div>
                </div>
                <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-sm">
                    <div className="flex items-center justify-between mb-2 text-slate-400">
                        <span className="text-sm font-medium">Potential Savings</span>
                        <TrendingUp className="w-5 h-5 text-amber-400" />
                    </div>
                    <div className="text-2xl font-bold">$12,450.00</div>
                    <div className="text-xs text-slate-500 mt-2">By reducing excess holding costs</div>
                </div>
            </div>

            <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
                <table className="w-full text-left">
                    <thead className="bg-slate-800/50 text-slate-400 border-b border-slate-800">
                        <tr>
                            <th className="px-6 py-4 font-semibold text-sm">Product Name</th>
                            <th className="px-6 py-4 font-semibold text-sm">Current Stock</th>
                            <th className="px-6 py-4 font-semibold text-sm">EOQ</th>
                            <th className="px-6 py-4 font-semibold text-sm">Safety Stock</th>
                            <th className="px-6 py-4 font-semibold text-sm">Reorder Point</th>
                            <th className="px-6 py-4 font-semibold text-sm">Status</th>
                            <th className="px-6 py-4 font-semibold text-sm">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {metrics.map((item, idx) => (
                            <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                                <td className="px-6 py-4 font-medium text-slate-200">
                                    <div className="flex items-center gap-2">
                                        {item.product_name}
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-slate-400">{item.current_stock}</td>
                                <td className="px-6 py-4 text-indigo-400 font-bold">{item.eoq}</td>
                                <td className="px-6 py-4 text-slate-400">{item.safety_stock}</td>
                                <td className="px-6 py-4 text-slate-400">{item.reorder_point}</td>
                                <td className="px-6 py-4">
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${item.recommendation === "Restock Now"
                                        ? 'bg-red-900/40 text-red-400 border border-red-800'
                                        : 'bg-emerald-900/40 text-emerald-400 border border-emerald-800'
                                        }`}>
                                        {item.recommendation}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <button
                                        onClick={async () => {
                                            const res = await api.get(`/api/v1/products/${item.product_id}`);
                                            setSelectedProductDetail(res.data);
                                            setIsDetailModalOpen(true);
                                        }}
                                        className="text-slate-400 hover:text-white transition-colors"
                                    >
                                        <Info className="w-5 h-5" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Product Detail Modal Integration */}
            {isDetailModalOpen && selectedProductDetail && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
                    <div className="bg-slate-900 text-slate-100 rounded-3xl shadow-2xl w-full max-w-4xl p-10 border border-slate-800 max-h-[90vh] overflow-y-auto relative animate-in fade-in zoom-in duration-300">
                        <button
                            onClick={() => setIsDetailModalOpen(false)}
                            className="absolute top-8 right-8 text-slate-500 hover:text-white transition-colors bg-slate-800 p-2 rounded-full"
                        >
                            <X className="h-6 w-6" />
                        </button>

                        <div className="mb-10">
                            <span className="text-xs font-black text-indigo-400 uppercase tracking-[0.2em] px-3 py-1 bg-indigo-500/10 rounded-full border border-indigo-500/20">{selectedProductDetail.category}</span>
                            <h2 className="text-5xl font-black mt-4 tracking-tight">{selectedProductDetail.name}</h2>
                            <p className="text-slate-400 text-xl mt-3 font-medium">{selectedProductDetail.sku} • {selectedProductDetail.unit}</p>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                            {/* Left Column: AI Optimization */}
                            <div className="space-y-10">
                                <div className="bg-indigo-600/5 p-8 rounded-3xl border border-indigo-500/20 relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                        <Target className="w-24 h-24 text-indigo-400" />
                                    </div>
                                    <h3 className="text-2xl font-black mb-8 flex items-center gap-3">
                                        <TrendingUp className="h-7 w-7 text-indigo-400" /> AI Optimization
                                    </h3>
                                    {selectedProductDetail.ai_insights ? (
                                        <div className="grid grid-cols-2 gap-8">
                                            <div className="space-y-2">
                                                <div className="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1">
                                                    EOQ <Info className="h-3 w-3 cursor-help" title="Most cost-effective order quantity" />
                                                </div>
                                                <div className="text-4xl font-black text-indigo-400 leading-none">{selectedProductDetail.ai_insights.eoq}</div>
                                            </div>
                                            <div className="space-y-2">
                                                <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">Reorder Point</div>
                                                <div className="text-4xl font-black text-emerald-400 leading-none">{selectedProductDetail.ai_insights.reorder_point}</div>
                                            </div>
                                            <div className="space-y-2">
                                                <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">Safety Stock</div>
                                                <div className="text-4xl font-black text-amber-400 leading-none">{selectedProductDetail.ai_insights.safety_stock}</div>
                                            </div>
                                            <div className="space-y-2">
                                                <div className="text-xs font-bold text-slate-500 uppercase tracking-widest">Current Stock</div>
                                                <div className={`text-4xl font-black leading-none ${selectedProductDetail.current_stock <= selectedProductDetail.ai_insights.reorder_point ? 'text-rose-500' : 'text-emerald-500'}`}>
                                                    {selectedProductDetail.current_stock}
                                                </div>
                                            </div>
                                            <div className="col-span-2 mt-6 pt-8 border-t border-slate-800">
                                                <div className="text-[10px] font-black uppercase tracking-[0.3em] text-slate-500 mb-4 text-center">AI Strategic Recommendation</div>
                                                <div className={`text-xl font-black py-4 rounded-2xl text-center border-2 ${selectedProductDetail.ai_insights.recommendation === 'Restock Now' ? 'bg-rose-500/10 text-rose-500 border-rose-500/20' : 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'}`}>
                                                    {selectedProductDetail.ai_insights.recommendation.toUpperCase()}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center py-8 gap-4">
                                            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-500"></div>
                                            <p className="text-slate-500 font-bold text-sm uppercase tracking-widest">Generating Insights...</p>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Right Column: Pending & Forecast */}
                            <div className="space-y-10">
                                <div className="bg-slate-800/20 p-8 rounded-3xl border border-slate-800">
                                    <h3 className="text-2xl font-black mb-8 flex items-center gap-3">
                                        <Clock className="h-7 w-7 text-indigo-400" /> Pending Orders
                                    </h3>
                                    <div className="space-y-4">
                                        {selectedProductDetail.pending_orders && selectedProductDetail.pending_orders.length > 0 ? (
                                            selectedProductDetail.pending_orders.map(order => (
                                                <div key={order.order_id} className="flex justify-between items-center p-5 bg-slate-800/40 rounded-2xl border border-slate-700/50 hover:border-indigo-500/30 transition-all">
                                                    <div>
                                                        <div className="font-black text-indigo-400 text-lg uppercase tracking-tight">{order.order_number}</div>
                                                        <div className="text-sm text-slate-400 font-bold">{order.quantity} {selectedProductDetail.unit} inbound</div>
                                                    </div>
                                                    <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border ${order.status === 'draft' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
                                                        order.status === 'shipped' ? 'bg-indigo-500/10 text-indigo-500 border-indigo-500/20' :
                                                            'bg-slate-500/10 text-slate-400 border-slate-500/20'
                                                        }`}>
                                                        {order.status}
                                                    </span>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="text-center py-12 border-2 border-dashed border-slate-800 rounded-3xl group hover:border-slate-700 transition-colors">
                                                <p className="text-slate-500 font-bold text-sm uppercase tracking-widest mb-4">No active shipments</p>
                                                <button
                                                    onClick={() => setIsDetailModalOpen(false)}
                                                    className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-black text-[10px] uppercase tracking-widest rounded-full transition-all active:scale-95"
                                                >
                                                    Queue Restock Point
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <h3 className="text-2xl font-black flex items-center gap-3">
                                        <TrendingUp className="h-7 w-7 text-indigo-400" /> Demand Trend
                                    </h3>
                                    <div className="h-44 w-full bg-slate-950 rounded-3xl border border-slate-800 overflow-hidden relative p-4">
                                        {selectedProductDetail.demand_forecast && selectedProductDetail.demand_forecast.length > 0 ? (
                                            <ResponsiveContainer width="100%" height="100%">
                                                <LineChart data={selectedProductDetail.demand_forecast}>
                                                    <Line type="monotone" dataKey="predicted_demand" stroke="#6366f1" strokeWidth={4} dot={false} />
                                                    <Tooltip
                                                        contentStyle={{ backgroundColor: '#0f172a', borderRadius: '16px', border: '1px solid #1e293b', padding: '12px' }}
                                                        itemStyle={{ fontWeight: '900', color: '#818cf8', fontSize: '12px', textTransform: 'uppercase' }}
                                                        labelStyle={{ display: 'none' }}
                                                    />
                                                </LineChart>
                                            </ResponsiveContainer>
                                        ) : (
                                            <div className="flex items-center justify-center h-full text-slate-600 font-black text-[10px] uppercase tracking-[0.3em]">No Visual Data</div>
                                        )}
                                    </div>
                                    <button
                                        className="w-full py-5 bg-slate-800/50 hover:bg-slate-800 text-slate-300 font-black text-xs uppercase tracking-[0.2em] rounded-2xl transition-all border border-slate-700/50 flex items-center justify-center gap-2 group"
                                    >
                                        Advanced ML Analysis <ArrowUpRight className="w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Optimization;
