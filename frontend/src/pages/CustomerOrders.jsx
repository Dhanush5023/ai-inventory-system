import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBag, Calendar, CreditCard, ChevronRight, Package, Search } from 'lucide-react';
import api from '../utils/api';

const CustomerOrders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        fetchMyOrders();
    }, []);

    const fetchMyOrders = async () => {
        setLoading(true);
        try {
            // In a real app, we'd have a specific endpoint for user's own sales/orders.
            // For now, we fetch sales and filter or just show recent sales as "orders".
            const response = await api.get('/api/v1/sales', { params: { limit: 50 } });
            setOrders(response.data.sales || []);
        } catch (error) {
            console.error("Error fetching orders:", error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-IN', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const filteredOrders = orders.filter(order =>
        order.product_name?.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="p-6 max-w-5xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-foreground">My Purchase History</h1>
                    <p className="text-muted-foreground mt-1">Track and manage your past orders</p>
                </div>
                <div className="relative w-full md:w-64">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search orders..."
                        className="w-full pl-9 pr-4 py-2 rounded-lg border bg-card focus:ring-2 focus:ring-primary outline-none text-sm transition-all"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-32 bg-card rounded-2xl border animate-pulse"></div>
                    ))}
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredOrders.map((order) => (
                        <div key={order.id} className="group bg-card rounded-2xl border p-5 hover:shadow-md transition-all">
                            <div className="flex flex-col md:flex-row gap-6">
                                <div className="h-20 w-20 bg-muted rounded-xl flex items-center justify-center shrink-0">
                                    <Package className="h-10 w-10 text-muted-foreground/40" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                                        <h3 className="font-bold text-lg group-hover:text-primary transition-colors">{order.product_name}</h3>
                                        <span className="text-xs font-bold px-2 py-1 bg-green-100 text-green-700 rounded-full uppercase tracking-tighter">Delivered</span>
                                    </div>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                        <div className="flex items-center text-muted-foreground">
                                            <Calendar className="h-4 w-4 mr-2 opacity-70" />
                                            {formatDate(order.sale_date)}
                                        </div>
                                        <div className="flex items-center text-muted-foreground">
                                            <ShoppingBag className="h-4 w-4 mr-2 opacity-70" />
                                            Qty: {order.quantity}
                                        </div>
                                        <div className="flex items-center text-muted-foreground">
                                            <CreditCard className="h-4 w-4 mr-2 opacity-70" />
                                            ₹{order.unit_price.toLocaleString()} / unit
                                        </div>
                                        <div className="text-right font-black text-foreground md:ml-auto">
                                            Total: ₹{order.total_amount.toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center justify-end md:border-l md:pl-6">
                                    <button className="flex items-center text-sm font-bold text-primary hover:underline">
                                        View Details <ChevronRight className="h-4 w-4 ml-1" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {!loading && filteredOrders.length === 0 && (
                <div className="text-center py-24 bg-card rounded-3xl border border-dashed">
                    <ShoppingBag className="h-16 w-16 text-muted-foreground/20 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-muted-foreground">No orders found</h2>
                    <Link to="/store" className="text-primary hover:underline mt-2 inline-block">Start shopping now</Link>
                </div>
            )}
        </div>
    );
};

export default CustomerOrders;
