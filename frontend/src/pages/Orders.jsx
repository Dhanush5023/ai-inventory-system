import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
    ClipboardList, Search, CheckCircle, Truck, PackageCheck,
    XCircle, Trash2, RefreshCw, AlertCircle, Calendar, User,
    ChevronRight, ArrowLeftRight, Box, Clock, ArrowUpRight, Download, ExternalLink
} from 'lucide-react';

const Orders = () => {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const [statusFilter, setStatusFilter] = useState('');
    const [searchTerm, setSearchTerm] = useState('');

    // Detail Modal State
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [transitioning, setTransitioning] = useState(false);

    const fetchOrders = useCallback(async () => {
        setRefreshing(true);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`/api/v1/orders?limit=100${statusFilter ? `&status=${statusFilter}` : ''}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setOrders(response.data.orders);
            setError(null);
        } catch (err) {
            console.error("Error fetching orders:", err);
            setError("Failed to load purchase orders.");
        } finally {
            setRefreshing(false);
            setLoading(false);
        }
    }, [statusFilter]);

    useEffect(() => {
        fetchOrders();
    }, [fetchOrders]);

    const handleUpdateStatus = async (orderId, newStatus) => {
        setTransitioning(true);
        try {
            const token = localStorage.getItem('token');
            await axios.patch(`/api/v1/orders/${orderId}/status`,
                { status: newStatus },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            fetchOrders();
            if (selectedOrder && selectedOrder.id === orderId) {
                setIsModalOpen(false);
                setSelectedOrder(null);
            }
        } catch (err) {
            alert("Status update failed: " + (err.response?.data?.detail || err.message));
        } finally {
            setTransitioning(false);
        }
    };

    const handleReceiveOrder = async (orderId, items) => {
        setTransitioning(true);
        try {
            const token = localStorage.getItem('token');
            const receiveData = {
                items: items.map(item => ({
                    order_item_id: item.id,
                    received_quantity: item.quantity
                })),
                notes: "Received via High-Performance UI"
            };
            await axios.post(`/api/v1/orders/${orderId}/receive`, receiveData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchOrders();
            setIsModalOpen(false);
            setSelectedOrder(null);
            alert("Inventory updated successfully!");
        } catch (err) {
            alert("Receiving failed: " + (err.response?.data?.detail || err.message));
        } finally {
            setTransitioning(false);
        }
    };

    const handleDeleteOrder = async (orderId) => {
        if (!window.confirm("Are you sure you want to delete this order?")) return;
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`/api/v1/orders/${orderId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchOrders();
        } catch (err) {
            alert("Deletion failed: " + (err.response?.data?.detail || err.message));
        }
    };

    const filteredOrders = orders.filter(order =>
        order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (order.supplier_name && order.supplier_name.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const getStatusStyles = (status) => {
        switch (status) {
            case 'draft': return 'bg-slate-800 text-slate-400 border-slate-700';
            case 'pending': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
            case 'approved': return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
            case 'shipped': return 'bg-violet-500/10 text-violet-400 border-violet-500/20';
            case 'received': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
            case 'cancelled': return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
            default: return 'bg-slate-800 text-slate-400 border-slate-700';
        }
    };

    if (loading) return (
        <div className="flex flex-col items-center justify-center h-[calc(100vh-64px)] bg-slate-950">
            <RefreshCw className="h-10 w-10 animate-spin text-indigo-500" />
            <p className="mt-4 text-slate-500 text-xs font-bold uppercase tracking-widest">Optimizing Data Stream</p>
        </div>
    );

    return (
        <div className="min-h-[calc(100vh-64px)] bg-slate-950 p-4 md:p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Simplified Header for Speed */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                    <div className="space-y-1">
                        <div className="inline-flex items-center gap-2 px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[9px] font-bold uppercase tracking-widest">
                            Procurement Dashboard
                        </div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">
                            Purchase <span className="text-indigo-400">Orders</span>
                        </h1>
                        <p className="text-slate-500 text-xs">High-performance supply chain management.</p>
                    </div>

                    <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-xl border border-white/5">
                        <div className="relative">
                            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search hash..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:ring-1 focus:ring-indigo-500 outline-none w-48"
                            />
                        </div>
                        <select
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-[10px] text-white outline-none h-[34px]"
                        >
                            <option value="">All Nodes</option>
                            <option value="draft">Drafts</option>
                            <option value="pending">Queue</option>
                            <option value="approved">Approved</option>
                            <option value="shipped">In Transit</option>
                            <option value="received">Settled</option>
                        </select>
                        <button
                            onClick={fetchOrders}
                            disabled={refreshing}
                            className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors disabled:opacity-50"
                        >
                            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>

                {/* Aggressively Optimized Table */}
                <div className="bg-slate-900 border border-white/5 rounded-2xl overflow-hidden shadow-2xl overflow-x-auto ring-1 ring-white/5">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-slate-800/50 border-b border-white/5">
                                <th className="px-6 py-4 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Entity</th>
                                <th className="px-6 py-4 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Temporal</th>
                                <th className="px-6 py-4 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Volume</th>
                                <th className="px-6 py-4 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Valuation</th>
                                <th className="px-6 py-4 text-[9px] font-bold text-slate-500 uppercase tracking-widest">Status</th>
                                <th className="px-6 py-4 text-[9px] font-bold text-slate-500 uppercase tracking-widest text-right">Ops</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/[0.03]">
                            {filteredOrders.length > 0 ? filteredOrders.map((order) => (
                                <tr key={order.id} className="hover:bg-indigo-500/[0.04] transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="h-8 w-8 rounded-lg bg-slate-800 border border-white/5 flex items-center justify-center text-indigo-400">
                                                <ClipboardList className="h-4 w-4" />
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="text-xs text-white font-bold font-mono">{order.order_number}</span>
                                                <span className="text-[10px] text-slate-500 truncate max-w-[150px]">{order.supplier_name}</span>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-col">
                                            <span className="text-xs text-slate-300">{new Date(order.order_date).toLocaleDateString()}</span>
                                            <span className="text-[9px] text-slate-600 font-mono uppercase tracking-tighter">Registered</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-xs font-bold text-white">
                                        {order.items?.length || 0}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-sm font-black text-white italic tracking-tight">₹{order.total_amount.toLocaleString()}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider border ${getStatusStyles(order.status)}`}>
                                            {order.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex items-center justify-end gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => { setSelectedOrder(order); setIsModalOpen(true); }}
                                                className="p-1.5 bg-slate-800 hover:bg-indigo-600 text-white rounded border border-white/5 transition-colors"
                                            >
                                                <ArrowUpRight className="h-4 w-4" />
                                            </button>
                                            {(order.status === 'draft' || order.status === 'pending') && (
                                                <button
                                                    onClick={() => handleDeleteOrder(order.id)}
                                                    className="p-1.5 bg-slate-800 hover:bg-rose-600 text-white rounded border border-white/5 transition-colors"
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </button>
                                            )}
                                        </div>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan="6" className="px-6 py-12 text-center text-slate-600 text-[10px] uppercase font-bold tracking-widest italic">
                                        No active nodes detected
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Optimized Modal - Using solid backgrounds instead of blur for speed */}
            {isModalOpen && selectedOrder && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-950/90">
                    <div className="bg-slate-900 border border-white/10 w-full max-w-4xl max-h-[90vh] rounded-3xl overflow-hidden shadow-2xl flex flex-col relative animate-in zoom-in-95 duration-200">
                        <div className="p-6 border-b border-white/5 flex justify-between items-start bg-slate-800/20">
                            <div>
                                <h2 className="text-2xl font-black text-white tracking-tighter flex items-center gap-3">
                                    {selectedOrder.order_number}
                                    <span className={`text-[9px] font-bold uppercase px-3 py-1 rounded border ${getStatusStyles(selectedOrder.status)}`}>
                                        {selectedOrder.status}
                                    </span>
                                </h2>
                                <p className="text-xs text-slate-500 mt-1 uppercase font-bold tracking-widest">{selectedOrder.supplier_name}</p>
                            </div>
                            <button onClick={() => setIsModalOpen(false)} className="p-2 hover:bg-white/5 rounded-full transition-colors">
                                <XCircle className="h-6 w-6 text-slate-400" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6 space-y-6">
                            <div className="grid grid-cols-3 gap-4">
                                <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                                    <p className="text-[9px] font-bold text-slate-500 uppercase">Valuation</p>
                                    <p className="text-xl font-black text-indigo-400 italic">₹{selectedOrder.total_amount.toLocaleString()}</p>
                                </div>
                                <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                                    <p className="text-[9px] font-bold text-slate-500 uppercase">Items</p>
                                    <p className="text-xl font-black text-white">{selectedOrder.items?.length || 0}</p>
                                </div>
                                <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
                                    <p className="text-[9px] font-bold text-slate-500 uppercase">Created By</p>
                                    <p className="text-xl font-black text-white truncate">{selectedOrder.username || 'System'}</p>
                                </div>
                            </div>

                            <div className="bg-slate-950/50 rounded-2xl border border-white/5 overflow-hidden">
                                <table className="w-full text-left text-[11px]">
                                    <thead className="bg-slate-800/50 border-b border-white/5">
                                        <tr>
                                            <th className="px-6 py-3 text-slate-500 font-bold uppercase">Product</th>
                                            <th className="px-6 py-3 text-slate-500 font-bold uppercase text-center">Qty</th>
                                            <th className="px-6 py-3 text-slate-500 font-bold uppercase text-right">Price</th>
                                            <th className="px-6 py-3 text-slate-500 font-bold uppercase text-right">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/[0.02]">
                                        {selectedOrder.items?.map((item, idx) => (
                                            <tr key={idx} className="hover:bg-white/5">
                                                <td className="px-6 py-3 text-white font-bold">{item.product_name}</td>
                                                <td className="px-6 py-3 text-center text-slate-300">{item.quantity}</td>
                                                <td className="px-6 py-3 text-right text-slate-500 font-mono">₹{item.unit_price.toLocaleString()}</td>
                                                <td className="px-6 py-3 text-right text-indigo-400 font-black italic">₹{item.total_price.toLocaleString()}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Action Pipeline</h3>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    {selectedOrder.status === 'draft' && (
                                        <button onClick={() => handleUpdateStatus(selectedOrder.id, 'pending')} disabled={transitioning} className="p-4 bg-amber-500/10 hover:bg-amber-500/20 text-amber-500 border border-amber-500/20 rounded-2xl text-[10px] font-black uppercase transition-all">
                                            Queue Entry
                                        </button>
                                    )}
                                    {(selectedOrder.status === 'draft' || selectedOrder.status === 'pending') && (
                                        <button onClick={() => handleUpdateStatus(selectedOrder.id, 'approved')} disabled={transitioning} className="p-4 bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 border border-blue-500/20 rounded-2xl text-[10px] font-black uppercase transition-all">
                                            Authorize
                                        </button>
                                    )}
                                    {selectedOrder.status === 'approved' && (
                                        <button onClick={() => handleUpdateStatus(selectedOrder.id, 'shipped')} disabled={transitioning} className="p-4 bg-violet-500/10 hover:bg-violet-500/20 text-violet-400 border border-violet-500/20 rounded-2xl text-[10px] font-black uppercase transition-all">
                                            Log Ship
                                        </button>
                                    )}
                                    {selectedOrder.status === 'shipped' && (
                                        <button onClick={() => handleReceiveOrder(selectedOrder.id, selectedOrder.items)} disabled={transitioning} className="p-4 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 rounded-2xl text-[10px] font-black uppercase transition-all">
                                            Finalize Settle
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="p-6 border-t border-white/5 bg-slate-800/20 flex justify-between items-center">
                            <span className="text-[10px] text-slate-500 font-bold uppercase">{selectedOrder.order_date}</span>
                            <button onClick={() => setIsModalOpen(false)} className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[10px] font-black uppercase tracking-widest shadow-lg shadow-indigo-500/20 transition-all">
                                Return
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Orders;
