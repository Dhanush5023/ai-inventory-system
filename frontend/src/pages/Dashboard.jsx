import React, { useState, useEffect } from 'react';
import api from '../utils/api';
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
                const [analyticsRes, topProdRes, alertsRes] = await Promise.all([
                    api.get('/api/v1/analytics'),
                    api.get('/api/v1/sales/stats/top-products?limit=5'),
                    api.get('/api/v1/alerts?unresolved_only=true&limit=3')
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
        <div className="p-8 bg-slate-50 dark:bg-slate-950 min-h-screen font-sans">
            <div className="flex justify-between items-center mb-10">
                <div>
                    <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-3">
                        <Sparkles className="text-indigo-500 w-8 h-8" /> Intelligence Center
                    </h1>
                    <p className="text-slate-500 font-medium mt-1">Real-time inventory orchestration and predictive insights.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-10">
                {kpis.map((kpi, index) => (
                    <div key={index} className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] shadow-xl border border-slate-100 dark:border-slate-800 relative overflow-hidden transition-all">
                        <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-4">{kpi.label}</h3>
                        <div className="text-4xl font-black text-slate-900 dark:text-white mb-2">{kpi.value}</div>
                        {kpi.change_percentage !== undefined && (
                            <div className={`flex items-center gap-1 text-sm font-bold ${kpi.trend === 'up' ? 'text-emerald-500' : 'text-rose-500'}`}>
                                {kpi.trend === 'up' ? '+' : ''}{kpi.change_percentage?.toFixed(1)}%
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] p-10 shadow-xl border border-slate-100 dark:border-slate-800">
                    <h2 className="text-2xl font-black text-slate-900 dark:text-white mb-8">Sales Forecast</h2>
                    <div className="h-[350px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={salesData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Area type="monotone" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.1} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-slate-900 rounded-[2.5rem] p-10 text-white shadow-2xl border border-slate-800">
                    <h3 className="text-2xl font-black mb-4">Stock Highlights</h3>
                    <div className="space-y-4">
                        {topProducts.map((prod, i) => (
                            <div key={i} className="flex justify-between items-center bg-slate-800 p-4 rounded-2xl">
                                <span className="text-sm font-bold">{prod.product_name}</span>
                                <span className="text-indigo-400 font-black">₹{Number(prod.total_revenue).toLocaleString()}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
