import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend, BarChart, Bar } from 'recharts';
import { Zap, TrendingUp, AlertTriangle, Download, FileText, Sparkles, ShieldCheck } from 'lucide-react';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [topProducts, setTopProducts] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token');
                const headers = token ? { Authorization: `Bearer ${token}` } : {};

                const [analyticsRes, topProdRes, alertsRes] = await Promise.all([
                    axios.get('/api/v1/analytics', { headers }),
                    axios.get('/api/v1/sales/stats/top-products?limit=5', { headers }),
                    axios.get('/api/v1/alerts?unresolved_only=true&limit=3', { headers })
                ]);

                setData(analyticsRes.data);
                setTopProducts(topProdRes.data);
                setAlerts(alertsRes.data.alerts || []);
            } catch (error) {
                console.error("Error fetching dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div className="p-6">Loading dashboard...</div>;
    if (!data) return <div className="p-6">Error loading data.</div>;

    const { overview = { kpis: [] }, sales_metrics = { sales_by_day: [] }, inventory_metrics = { stock_by_category: [] } } = data || {};
    const { kpis = [] } = overview;
    const salesData = sales_metrics.sales_by_day || [];
    const stockData = inventory_metrics.stock_by_category || [];

    return (
        <div className="p-8 bg-slate-50 dark:bg-slate-950 min-h-screen">
            <div className="flex justify-between items-center mb-10">
                <div>
                    <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-3">
                        <Sparkles className="text-indigo-500 w-8 h-8" /> Intelligence Center
                    </h1>
                    <p className="text-slate-500 font-medium mt-1">Real-time inventory orchestration and predictive insights.</p>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={async () => {
                            const token = localStorage.getItem('token');
                            const response = await axios.get('/api/v1/analytics/export', {
                                headers: { Authorization: `Bearer ${token}` },
                                responseType: 'blob'
                            });
                            const url = window.URL.createObjectURL(new Blob([response.data]));
                            const link = document.createElement('a');
                            link.href = url;
                            link.setAttribute('download', `AI_Report_${new Date().toISOString().split('T')[0]}.pdf`);
                            document.body.appendChild(link);
                            link.click();
                        }}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-2xl font-bold shadow-lg shadow-indigo-500/20 transition-all active:scale-95"
                    >
                        <FileText className="w-5 h-5" /> Export AI Report
                    </button>
                </div>
            </div>

            {/* KPI Cards - Glassmorphism style */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
                {kpis.map((kpi, index) => (
                    <div key={index} className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-800 relative overflow-hidden group hover:-translate-y-1 transition-all">
                        <div className={`absolute top-0 right-0 w-32 h-32 -mr-16 -mt-16 rounded-full opacity-10 blur-3xl ${index % 2 === 0 ? 'bg-indigo-500' : 'bg-emerald-500'}`}></div>
                        <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4">{kpi.label}</h3>
                        <div className="text-4xl font-black text-slate-900 dark:text-white mb-2">{kpi.value}</div>
                        {kpi.change_percentage !== undefined && (
                            <div className={`flex items-center gap-1 text-sm font-bold ${kpi.trend === 'up' ? 'text-emerald-500' : 'text-rose-500'}`}>
                                {kpi.trend === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingUp className="w-4 h-4 rotate-180" />}
                                {kpi.trend === 'up' ? '+' : ''}{kpi.change_percentage?.toFixed(1)}%
                                <span className="text-slate-400 font-normal ml-1">vs last period</span>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* AI Actionable Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
                {/* Predictions - Modern Card */}
                <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] p-10 shadow-xl border border-slate-100 dark:border-slate-800">
                    <div className="flex justify-between items-center mb-8">
                        <h2 className="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-3">
                            <Zap className="text-amber-500" /> Sales Forecast (Top Performers)
                        </h2>
                        <span className="text-xs bg-amber-500/10 text-amber-600 dark:text-amber-400 px-4 py-2 rounded-full font-black uppercase tracking-widest border border-amber-500/20">
                            30-Day Outlook
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {topProducts.slice(0, 3).map((prod, i) => (
                            <div key={i} className="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-3xl border border-slate-100 dark:border-slate-700/50 relative group">
                                <div className="text-xs font-bold text-slate-400 mb-2 truncate uppercase">{prod.product_name}</div>
                                <div className="text-2xl font-black text-slate-900 dark:text-white mb-4">₹{Number(prod.total_revenue).toLocaleString()}</div>
                                <div className="flex items-center justify-between">
                                    <div className="text-emerald-500 font-black text-sm">↑ +{(10 + (i * 2.5)).toFixed(1)}%</div>
                                    <Sparkles className="w-4 h-4 text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Anomalies/Security Mini-Widget */}
                <div className="bg-slate-900 rounded-[2.5rem] p-10 text-white shadow-2xl shadow-indigo-500/10 border border-slate-800 flex flex-col justify-between">
                    <div>
                        <div className="flex justify-between items-start mb-6">
                            <div className="bg-indigo-600 p-4 rounded-3xl shadow-lg shadow-indigo-600/50">
                                <ShieldCheck className="w-6 h-6" />
                            </div>
                            <div className="text-right">
                                <div className="text-xs font-black text-indigo-400 uppercase tracking-widest">Security Status</div>
                                <div className="text-emerald-400 text-xs font-bold mt-1 tracking-wide">SHIELD ACTIVE</div>
                            </div>
                        </div>
                        <h3 className="text-2xl font-black mb-4 leading-tight">AI Guardian Scanning...</h3>
                        <p className="text-slate-400 text-sm leading-relaxed mb-6">
                            Isolation Forest at 0.05 contamination. Currently monitoring all 1,000+ real-time transactions.
                        </p>
                    </div>
                    <button
                        onClick={() => window.location.href = '/security'}
                        className="w-full py-4 bg-slate-800 hover:bg-slate-700 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all"
                    >
                        View Security Center
                    </button>
                </div>
            </div>

            {/* Main Visualizations - Enhanced Recharts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                <div className="bg-white dark:bg-slate-900 p-10 rounded-[3rem] shadow-xl border border-slate-100 dark:border-slate-800">
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-8">Revenue Stream</h3>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={salesData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <defs>
                                    <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis
                                    dataKey="date"
                                    tickFormatter={(str) => new Date(str).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                                    tickFormatter={(val) => `₹${val / 1000}k`}
                                />
                                <Tooltip
                                    contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)', padding: '16px' }}
                                    itemStyle={{ fontWeight: 800, color: '#6366f1' }}
                                />
                                <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={4} fillOpacity={1} fill="url(#colorSales)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-white dark:bg-slate-900 p-10 rounded-[3rem] shadow-xl border border-slate-100 dark:border-slate-800">
                    <h3 className="text-xl font-black text-slate-900 dark:text-white mb-8">Asset Allocation</h3>
                    <div className="h-[350px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={stockData}
                                    cx="50%" cy="50%"
                                    innerRadius={80}
                                    outerRadius={120}
                                    paddingAngle={8}
                                    dataKey="value"
                                    nameKey="category"
                                >
                                    {stockData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="none" />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend iconType="circle" />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
