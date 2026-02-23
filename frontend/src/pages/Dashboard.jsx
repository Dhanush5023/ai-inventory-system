import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import {
    Zap, TrendingUp, AlertTriangle, Sparkles,
    ShieldCheck, ArrowUpRight, ArrowDownRight,
    Activity, Target, Package, RefreshCw
} from 'lucide-react';

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [marketInt, setMarketInt] = useState(null);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchAllData = useCallback(async (isRefresh = false) => {
        if (isRefresh) setRefreshing(true);
        try {
            const fetchAnalytics = api.get('/api/v1/analytics').then(res => setData(res.data));
            const fetchMarket = api.get('/api/v1/analytics/market-intelligence').then(res => setMarketInt(res.data));

            await Promise.allSettled([fetchAnalytics, fetchMarket]);
            setLastUpdated(new Date());
        } catch (error) {
            console.error("Error fetching dashboard data:", error);
            // Don't let a failed marketInt block the whole dashboard
            if (error.config?.url?.includes('market-intelligence')) {
                console.warn("Market Intelligence failed, but dashboard will still render.");
            }
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchAllData();
        // Auto-refresh every 60 seconds for live feel
        const interval = setInterval(() => fetchAllData(true), 60000);
        return () => clearInterval(interval);
    }, [fetchAllData]);

    if (loading) return (
        <div className="h-full w-full flex items-center justify-center bg-background">
            <div className="flex flex-col items-center">
                <div className="h-16 w-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin mb-4" />
                <p className="text-sm font-black uppercase tracking-[0.3em] text-muted-foreground animate-pulse">Loading Live Data</p>
            </div>
        </div>
    );

    // -- Real data extraction --
    const overview = data?.overview || { kpis: [], low_stock_count: 0, critical_alerts: 0, pending_orders: 0, recent_sales_count: 0 };
    const salesData = data?.sales_metrics?.sales_by_day || [];
    const financials = data?.financial_metrics || {};

    // KPIs by label index
    const kpiMap = {};
    (overview.kpis || []).forEach(k => { kpiMap[k.label] = k; });

    const totalRevenue30d = kpiMap['Total Revenue (30d)']?.value ?? '₹0.00';
    const totalProducts = kpiMap['Total Products']?.value ?? 0;
    const lowStockItems = kpiMap['Low Stock Items']?.value ?? overview.low_stock_count ?? 0;
    const stockValue = kpiMap['Stock Value']?.value ?? '₹0.00';
    const revenueGrowth = kpiMap['Total Revenue (30d)']?.change_percentage ?? 0;
    const revenueTrend = kpiMap['Total Revenue (30d)']?.trend ?? 'up';

    const brief = marketInt?.brief || {};
    const insights = marketInt?.insights || [];

    const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
    const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

    return (
        <motion.div variants={container} initial="hidden" animate="show" className="space-y-10">

            {/* Live Business Telemetry Header */}
            <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-5 gap-4 bg-primary/5 p-6 md:p-8 rounded-[2.5rem] border border-primary/10 relative overflow-hidden">
                <div className="col-span-2 lg:col-span-1 border-b lg:border-b-0 lg:border-r border-primary/10 pb-4 lg:pb-0 lg:pr-6">
                    <h1 className="text-3xl font-black tracking-tighter premium-gradient-text mb-1">INTELLIGENCE</h1>
                    <div className="flex items-center text-xs font-black text-primary/60 uppercase tracking-widest">
                        <Activity className="h-3 w-3 mr-2 animate-pulse" /> Live System Telemetry
                    </div>
                    {lastUpdated && (
                        <div className="text-[10px] text-muted-foreground mt-1">
                            Updated {lastUpdated.toLocaleTimeString()}
                        </div>
                    )}
                </div>

                {/* ROI Score */}
                <div className="flex flex-col justify-center">
                    <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-1">Global Health</span>
                    <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black tracking-tight">{(brief.roi_score ?? 0).toFixed(1)}</span>
                        <span className="text-xs font-bold text-green-500 flex items-center">
                            <ArrowUpRight className="h-3 w-3 mr-0.5" /> / 10
                        </span>
                    </div>
                </div>

                {/* Revenue */}
                <div className="flex flex-col justify-center">
                    <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-1">Revenue (30d)</span>
                    <div className="flex items-baseline gap-1">
                        <span className="text-xl font-black tracking-tight truncate">{totalRevenue30d}</span>
                    </div>
                    <span className={`text-[10px] font-bold flex items-center mt-1 ${revenueGrowth >= 0 ? 'text-green-500' : 'text-rose-500'}`}>
                        {revenueGrowth >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                        {Math.abs(revenueGrowth).toFixed(1)}% vs prev period
                    </span>
                </div>

                {/* Primary Driver */}
                <div className="flex flex-col justify-center">
                    <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-1">Key Driver</span>
                    <span className="text-base font-bold tracking-tight">{brief.top_efficiency_gain ?? '—'}</span>
                </div>

                {/* Refresh */}
                <div className="flex items-center justify-end">
                    <button
                        onClick={() => fetchAllData(true)}
                        className="h-12 w-12 bg-card rounded-2xl flex items-center justify-center border shadow-xl hover:scale-110 transition-transform cursor-pointer"
                        title="Refresh data"
                    >
                        <RefreshCw className={`h-5 w-5 text-primary ${refreshing ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </motion.div>

            {/* KPI Cards Row */}
            <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: 'Total Products', value: totalProducts, icon: Package, color: 'text-blue-500', bg: 'bg-blue-50 dark:bg-blue-950' },
                    { label: 'Low Stock Items', value: lowStockItems, icon: AlertTriangle, color: 'text-amber-500', bg: 'bg-amber-50 dark:bg-amber-950' },
                    { label: 'Pending Orders', value: overview.pending_orders, icon: Zap, color: 'text-purple-500', bg: 'bg-purple-50 dark:bg-purple-950' },
                    { label: 'Sales (7d)', value: overview.recent_sales_count, icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-50 dark:bg-green-950' },
                ].map((kpi, idx) => (
                    <div key={idx} className="bg-card border rounded-2xl p-6 hover:shadow-lg transition-all">
                        <div className={`w-10 h-10 ${kpi.bg} rounded-xl flex items-center justify-center mb-3`}>
                            <kpi.icon className={`h-5 w-5 ${kpi.color}`} />
                        </div>
                        <div className="text-3xl font-black tracking-tight mb-1">{kpi.value ?? 0}</div>
                        <div className="text-xs font-bold text-muted-foreground uppercase tracking-widest">{kpi.label}</div>
                    </div>
                ))}
            </motion.div>

            {/* Morning Brief Card + Revenue Card */}
            <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 glass-card p-8 md:p-10 rounded-[3rem] border border-border/50 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-10 opacity-5 group-hover:opacity-10 transition-opacity">
                        <Sparkles className="h-32 w-32 text-primary" />
                    </div>
                    <div className="flex items-center gap-2 mb-6 text-primary">
                        <Sparkles className="h-5 w-5" />
                        <span className="text-sm font-black uppercase tracking-widest">Executive AI Briefing</span>
                    </div>
                    <h2 className="text-2xl font-black mb-4 tracking-tight leading-snug">
                        {brief.headline_insight || 'Fetching live market intelligence...'}
                    </h2>
                    <p className="text-base text-muted-foreground leading-relaxed max-w-2xl">
                        {brief.summary || 'Analyzing your inventory and sales data...'}
                    </p>
                </div>

                <div className="bg-slate-950 p-8 md:p-10 rounded-[3rem] text-white flex flex-col justify-between relative overflow-hidden shadow-2xl">
                    <div className="absolute bottom-0 right-0 p-10 opacity-10">
                        <TrendingUp className="h-40 w-40 text-indigo-500" />
                    </div>
                    <div>
                        <span className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400 mb-4 block">Profitability Matrix</span>
                        <div className="text-4xl xl:text-5xl font-black mb-2 tracking-tighter break-all">{totalRevenue30d}</div>
                        <p className="text-indigo-300 font-bold text-sm">Total Gross Revenue (30 Days)</p>

                        <div className="mt-4 space-y-1 text-sm">
                            <div className="flex justify-between">
                                <span className="text-white/40">Stock Value</span>
                                <span className="font-bold">{stockValue}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-white/40">Growth vs Prior Period</span>
                                <span className={`font-bold ${revenueGrowth >= 0 ? 'text-green-400' : 'text-rose-400'}`}>
                                    {revenueGrowth >= 0 ? '+' : ''}{revenueGrowth.toFixed(1)}%
                                </span>
                            </div>
                        </div>
                    </div>
                    <div className="mt-6 pt-6 border-t border-white/10 flex justify-between items-center text-sm font-bold">
                        <span className="text-white/40 uppercase tracking-widest text-[10px]">Real-time Status</span>
                        <span className="text-green-400 flex items-center">
                            <div className="h-2 w-2 rounded-full bg-green-400 mr-2 animate-pulse" />
                            Live
                        </span>
                    </div>
                </div>
            </motion.div>

            {/* Revenue Chart + Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <motion.div variants={item} className="lg:col-span-2 glass-card p-8 md:p-10 rounded-[3rem]">
                    <div className="flex justify-between items-center mb-8">
                        <h3 className="text-xl font-black tracking-tight">Revenue Dynamics</h3>
                        <div className="px-3 py-1 bg-primary/10 rounded-lg text-[10px] font-black text-primary uppercase tracking-widest">
                            {salesData.length > 0 ? `${salesData.length} days` : 'No data'}
                        </div>
                    </div>
                    {salesData.length > 0 ? (
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={salesData}>
                                    <defs>
                                        <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0,0,0,0.05)" />
                                    <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                                    <YAxis hide />
                                    <Tooltip
                                        contentStyle={{ borderRadius: '20px', border: 'none', boxShadow: '0 20px 40px -10px rgba(0,0,0,0.1)' }}
                                        formatter={(v) => [`₹${Number(v).toLocaleString()}`, 'Revenue']}
                                    />
                                    <Area type="monotone" dataKey="value" stroke="hsl(var(--primary))" strokeWidth={3} fillOpacity={1} fill="url(#colorSales)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="h-[300px] flex items-center justify-center text-muted-foreground text-center">
                            <div>
                                <TrendingUp className="h-16 w-16 mx-auto mb-4 opacity-20" />
                                <p className="font-bold">No sales data yet</p>
                                <p className="text-sm">Revenue chart will appear once sales are recorded</p>
                            </div>
                        </div>
                    )}
                </motion.div>

                <motion.div variants={item} className="space-y-4">
                    {insights.length > 0 ? insights.map((insight, idx) => (
                        <div key={idx} className="bg-card p-6 rounded-[2rem] border hover:shadow-xl transition-all group">
                            <div className="flex items-center justify-between mb-3">
                                <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${insight.category === 'Revenue' ? 'bg-green-50 dark:bg-green-950 text-green-600' :
                                    insight.category === 'Risk' ? 'bg-rose-50 dark:bg-rose-950 text-rose-600' :
                                        'bg-blue-50 dark:bg-blue-950 text-blue-600'
                                    }`}>
                                    {insight.category === 'Revenue' ? <TrendingUp className="h-5 w-5" /> :
                                        insight.category === 'Risk' ? <ShieldCheck className="h-5 w-5" /> :
                                            <Activity className="h-5 w-5" />}
                                </div>
                                <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${insight.impact_level === 'High' ? 'text-rose-500' :
                                    insight.impact_level === 'Medium' ? 'text-amber-500' : 'text-muted-foreground'
                                    }`}>{insight.impact_level} Impact</span>
                            </div>
                            <h4 className="font-black text-base mb-1">{insight.title}</h4>
                            <p className="text-sm text-muted-foreground font-medium leading-relaxed group-hover:text-foreground transition-colors">
                                {insight.description}
                            </p>
                        </div>
                    )) : (
                        <div className="bg-card p-6 rounded-[2rem] border text-center text-muted-foreground">
                            <p className="font-bold">Loading insights...</p>
                        </div>
                    )}
                </motion.div>
            </div>
        </motion.div>
    );
};

export default Dashboard;
