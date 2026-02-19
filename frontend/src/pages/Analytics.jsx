import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { TrendingUp, DollarSign, Activity } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Analytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get('/api/v1/analytics/prediction');
                setData(response.data);
            } catch (error) {
                console.error("Error fetching analytics:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div className="p-6">Loading analytics...</div>;
    if (!data) return <div className="p-6">Error loading data.</div>;

    const { financial_metrics } = data;
    const { total_revenue, total_cost, gross_profit, profit_margin, revenue_by_month } = financial_metrics;

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6 flex items-center">
                <TrendingUp className="mr-2" /> Financial Analytics
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                <div className="bg-card text-card-foreground p-6 rounded-lg shadow border">
                    <h3 className="text-sm font-medium text-muted-foreground">Total Revenue</h3>
                    <div className="text-2xl font-bold mt-2 text-green-600">₹{(Number(total_revenue) || 0).toLocaleString()}</div>
                </div>
                <div className="bg-card text-card-foreground p-6 rounded-lg shadow border">
                    <h3 className="text-sm font-medium text-muted-foreground">Total Cost</h3>
                    <div className="text-2xl font-bold mt-2 text-red-600">₹{(Number(total_cost) || 0).toLocaleString()}</div>
                </div>
                <div className="bg-card text-card-foreground p-6 rounded-lg shadow border">
                    <h3 className="text-sm font-medium text-muted-foreground">Gross Profit</h3>
                    <div className="text-2xl font-bold mt-2 text-blue-600">₹{(Number(gross_profit) || 0).toLocaleString()}</div>
                </div>
                <div className="bg-card text-card-foreground p-6 rounded-lg shadow border">
                    <h3 className="text-sm font-medium text-muted-foreground">Profit Margin</h3>
                    <div className="text-2xl font-bold mt-2 text-purple-600">{profit_margin}%</div>
                </div>
            </div>

            <div className="bg-card p-6 rounded-lg shadow border h-[400px]">
                <h3 className="text-lg font-semibold mb-4">Revenue Trends (Last 6 Months)</h3>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={revenue_by_month}>
                        <defs>
                            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="date"
                            tickFormatter={(str) => new Date(str).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
                        />
                        <YAxis />
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <Tooltip
                            labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}
                            formatter={(value) => [`₹${(Number(value) || 0).toLocaleString()}`, 'Revenue']}
                        />
                        <Area type="monotone" dataKey="value" stroke="#82ca9d" fillOpacity={1} fill="url(#colorRevenue)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default Analytics;
