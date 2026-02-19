import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
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

    const [selectedOrder, setSelectedOrder] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [transitioning, setTransitioning] = useState(false);

    const fetchOrders = useCallback(async () => {
        setRefreshing(true);
        try {
            const response = await api.get(`/api/v1/orders?limit=100${statusFilter ? `&status=${statusFilter}` : ''}`);
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
            await api.patch(`/api/v1/orders/${orderId}/status`, { status: newStatus });
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
            const receiveData = {
                items: items.map(item => ({
                    order_item_id: item.id,
                    received_quantity: item.quantity
                })),
                notes: "Received via High-Performance UI"
            };
            await api.post(`/api/v1/orders/${orderId}/receive`, receiveData);
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
            await api.delete(`/api/v1/orders/${orderId}`);
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

    if (loading) return <div>Loading orders...</div>;

    return (
        <div className="min-h-[calc(100vh-64px)] bg-slate-950 p-4 md:p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                    <div className="space-y-1">
                        <h1 className="text-3xl font-bold text-white tracking-tight">Purchase Orders</h1>
                    </div>
                    <div className="flex items-center gap-2">
                        <input
                            type="text"
                            placeholder="Search orders..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-xs text-white"
                        />
                        <button onClick={fetchOrders} className="p-2 bg-indigo-600 text-white rounded-lg">
                            <RefreshCw className={refreshing ? 'animate-spin' : ''} />
                        </button>
                    </div>
                </div>

                <div className="bg-slate-900 border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-800 border-b border-white/5">
                                <th className="px-6 py-4 text-xs font-bold text-slate-500">Order #</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500">Supplier</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500">Date</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500">Status</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredOrders.map((order) => (
                                <tr key={order.id} className="hover:bg-indigo-500/5 transition-colors border-b border-white/5">
                                    <td className="px-6 py-4 text-white font-mono">{order.order_number}</td>
                                    <td className="px-6 py-4 text-slate-400">{order.supplier_name}</td>
                                    <td className="px-6 py-4 text-slate-400">{new Date(order.order_date).toLocaleDateString()}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${getStatusStyles(order.status)}`}>
                                            {order.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button onClick={() => handleDeleteOrder(order.id)} className="text-rose-500 hover:text-rose-400">
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Orders;
