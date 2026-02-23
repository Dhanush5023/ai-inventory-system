import React, { useState } from 'react';
import { Package, Truck, CheckCircle, Clock, MapPin, Search, ChevronRight, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const TrackOrder = () => {
    const [orderId, setOrderId] = useState('');
    const [trackingData, setTrackingData] = useState(null);

    const handleTrack = (e) => {
        e.preventDefault();
        // Simulate tracking data
        setTrackingData({
            id: orderId || "ORD-99234",
            status: 'In Transit',
            estimate: 'Tomorrow, by 8:00 PM',
            currentLocation: 'Hub - Bangalore South',
            steps: [
                { title: 'Order Placed', time: 'Yesterday, 10:30 AM', completed: True },
                { title: 'Processing', time: 'Yesterday, 02:45 PM', completed: True },
                { title: 'Shipped', time: 'Today, 08:00 AM', completed: True },
                { title: 'In Transit', time: 'Today, 11:30 AM', current: True },
                { title: 'Delivered', time: 'Expected Tomorrow', pending: True },
            ]
        });
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-foreground">Track Your Order</h1>
                <p className="text-muted-foreground mt-1">Enter your order ID to see real-time updates</p>
            </div>

            <div className="bg-card rounded-2xl border p-6 shadow-sm mb-8">
                <form onSubmit={handleTrack} className="flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Enter Order ID (e.g., ORD-12345)"
                            className="w-full pl-10 pr-4 py-3 rounded-xl border bg-background focus:ring-2 focus:ring-primary outline-none transition-all"
                            value={orderId}
                            onChange={(e) => setOrderId(e.target.value)}
                        />
                    </div>
                    <button
                        type="submit"
                        className="px-6 py-3 bg-primary text-primary-foreground font-bold rounded-xl hover:translate-y-[-2px] hover:shadow-lg transition-all"
                    >
                        Track Order
                    </button>
                </form>
            </div>

            {trackingData ? (
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="bg-primary/5 rounded-3xl border border-primary/20 p-8 flex flex-col md:flex-row justify-between gap-6">
                        <div className="flex items-center gap-4">
                            <div className="h-16 w-16 bg-primary/20 rounded-2xl flex items-center justify-center">
                                <Truck className="h-8 w-8 text-primary" />
                            </div>
                            <div>
                                <span className="text-xs font-bold text-primary uppercase tracking-widest">{trackingData.status}</span>
                                <h2 className="text-2xl font-black text-foreground">Estimate: {trackingData.estimate}</h2>
                                <p className="text-sm text-muted-foreground flex items-center mt-1">
                                    <MapPin className="h-4 w-4 mr-1" />
                                    {trackingData.currentLocation}
                                </p>
                            </div>
                        </div>
                        <div className="text-right flex flex-col justify-center">
                            <span className="text-xs text-muted-foreground">Order ID</span>
                            <span className="font-mono font-bold text-lg">{trackingData.id}</span>
                        </div>
                    </div>

                    <div className="bg-card rounded-3xl border p-8 shadow-sm">
                        <h3 className="font-bold text-lg mb-8">Order Journey</h3>
                        <div className="relative space-y-8 before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-0.5 before:bg-muted">
                            {trackingData.steps.map((step, idx) => (
                                <div key={idx} className="relative pl-10">
                                    <div className={`absolute left-0 top-1.5 h-6 w-6 rounded-full border-4 border-card flex items-center justify-center z-10 ${step.completed ? 'bg-green-500' : step.current ? 'bg-primary animate-pulse' : 'bg-muted'
                                        }`}>
                                        {step.completed && <CheckCircle className="h-3 w-3 text-white" />}
                                    </div>
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className={`font-bold ${step.pending ? 'text-muted-foreground' : 'text-foreground'}`}>{step.title}</h4>
                                            <p className="text-sm text-muted-foreground">{step.time}</p>
                                        </div>
                                        {step.current && (
                                            <span className="text-[10px] font-black bg-primary/10 text-primary px-2 py-0.5 rounded-full uppercase tracking-tighter">Live Update</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div className="text-center py-20 bg-card rounded-3xl border border-dashed">
                    <Clock className="h-16 w-16 text-muted-foreground/20 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-muted-foreground">Recent Orders</h2>
                    <p className="text-muted-foreground mb-6">Select an order from your history to track</p>
                    <Link to="/my-orders" className="text-primary font-bold hover:underline">View Purchase History</Link>
                </div>
            )}
        </div>
    );
};

export default TrackOrder;
