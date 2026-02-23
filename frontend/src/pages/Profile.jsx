import React from 'react';
import { User, Mail, MapPin, Phone, Shield, Bell, LogOut, ChevronRight, Package, CreditCard } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
    const { user, logout } = useAuth();

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <div className="bg-card rounded-3xl border shadow-xl overflow-hidden">
                {/* Header/Banner */}
                <div className="h-32 bg-gradient-to-r from-primary/20 to-indigo-500/20 relative">
                    <div className="absolute -bottom-12 left-8 h-24 w-24 rounded-2xl bg-primary flex items-center justify-center text-primary-foreground text-4xl font-bold shadow-lg border-4 border-card">
                        {user?.full_name?.charAt(0) || 'U'}
                    </div>
                </div>

                <div className="pt-16 p-8">
                    <div className="flex justify-between items-start mb-8">
                        <div>
                            <h1 className="text-3xl font-black text-foreground">{user?.full_name}</h1>
                            <p className="text-muted-foreground flex items-center mt-1">
                                <Shield className="h-4 w-4 mr-1 text-primary" />
                                {user?.role?.toUpperCase()} ACCOUNT
                            </p>
                        </div>
                        <button
                            onClick={logout}
                            className="px-4 py-2 rounded-xl bg-red-50 text-red-600 font-bold text-sm hover:bg-red-100 transition-colors flex items-center"
                        >
                            <LogOut className="h-4 w-4 mr-2" /> Log Out
                        </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            <h2 className="text-lg font-bold border-b pb-2">Personal Information</h2>
                            <div className="space-y-4">
                                <div className="flex items-center p-3 rounded-xl bg-accent/50 space-x-4">
                                    <div className="h-10 w-10 rounded-lg bg-card flex items-center justify-center shadow-sm">
                                        <Mail className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <span className="text-xs text-muted-foreground block">Email Address</span>
                                        <span className="font-semibold">{user?.email}</span>
                                    </div>
                                </div>
                                <div className="flex items-center p-3 rounded-xl bg-accent/50 space-x-4">
                                    <div className="h-10 w-10 rounded-lg bg-card flex items-center justify-center shadow-sm">
                                        <Phone className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <span className="text-xs text-muted-foreground block">Phone Number</span>
                                        <span className="font-semibold">+91 98765 43210</span>
                                    </div>
                                </div>
                                <div className="flex items-center p-3 rounded-xl bg-accent/50 space-x-4">
                                    <div className="h-10 w-10 rounded-lg bg-card flex items-center justify-center shadow-sm">
                                        <MapPin className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <span className="text-xs text-muted-foreground block">Shipping Address</span>
                                        <span className="font-semibold">M.G. Road, Bangalore, KA</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <h2 className="text-lg font-bold border-b pb-2">Quick Actions</h2>
                            <div className="space-y-3">
                                <button className="w-full flex items-center justify-between p-4 rounded-xl border hover:bg-accent transition-all group">
                                    <div className="flex items-center">
                                        <Package className="h-5 w-5 mr-3 text-muted-foreground group-hover:text-primary" />
                                        <span className="font-medium">My Orders</span>
                                    </div>
                                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                                </button>
                                <button className="w-full flex items-center justify-between p-4 rounded-xl border hover:bg-accent transition-all group">
                                    <div className="flex items-center">
                                        <CreditCard className="h-5 w-5 mr-3 text-muted-foreground group-hover:text-primary" />
                                        <span className="font-medium">Payment Methods</span>
                                    </div>
                                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                                </button>
                                <button className="w-full flex items-center justify-between p-4 rounded-xl border hover:bg-accent transition-all group">
                                    <div className="flex items-center">
                                        <Bell className="h-5 w-5 mr-3 text-muted-foreground group-hover:text-primary" />
                                        <span className="font-medium">Notifications</span>
                                    </div>
                                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Profile;
