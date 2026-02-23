import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    LayoutDashboard, Package, ShoppingCart, Users, Truck,
    TrendingUp, AlertTriangle, ShieldCheck, Settings, LogOut, Zap,
    ChevronDown, Menu, X, Bell, Search, ClipboardList, User
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const navItems = {
        admin: [
            { to: '/', label: 'Dashboard', icon: LayoutDashboard },
            { to: '/products', label: 'Inventory', icon: Package },
            { to: '/sales', label: 'Sales Intelligence', icon: TrendingUp },
            { to: '/suppliers', label: 'Global Suppliers', icon: Truck },
            { to: '/analytics', label: 'Market Insights', icon: Zap },
            { to: '/security', label: 'AI Security', icon: ShieldCheck },
            { to: '/alerts', label: 'System Alerts', icon: AlertTriangle },
        ],
        customer: [
            { to: '/store', label: 'Marketplace', icon: Package },
            { to: '/my-orders', label: 'My Purchases', icon: ShoppingCart },
            { to: '/track-order', label: 'Track Shipment', icon: Truck },
            { to: '/profile', label: 'Account Profile', icon: User },
        ]
    };

    const currentNav = navItems[user?.role] || [];

    return (
        <div className="flex h-screen bg-background text-foreground overflow-hidden">
            {/* Sidebar */}
            <aside className="w-72 border-r bg-card/40 backdrop-blur-xl hidden md:flex flex-col z-20 shadow-[1px_0_0_0_rgba(0,0,0,0.1)]">
                <div className="h-20 flex items-center px-8">
                    <motion.div
                        animate={{
                            rotate: [0, 5, -5, 0],
                            scale: [1, 1.1, 1]
                        }}
                        transition={{
                            duration: 4,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                        className="h-10 w-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 mr-3 relative overflow-hidden"
                    >
                        <motion.div
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="absolute inset-0 bg-white/20"
                        />
                        <Zap className="h-6 w-6 text-primary-foreground font-black z-10" />
                    </motion.div>
                    <motion.span
                        animate={{ opacity: [0.8, 1, 0.8] }}
                        transition={{ duration: 3, repeat: Infinity }}
                        className="font-black text-xl tracking-tighter premium-gradient-text uppercase"
                    >
                        QUANTUM NEXUS
                    </motion.span>
                </div>

                <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto custom-scrollbar">
                    {currentNav.map((item) => {
                        const isActive = location.pathname === item.to;
                        return (
                            <Link
                                key={item.to}
                                to={item.to}
                                className={`group flex items-center px-4 py-3 text-sm font-bold rounded-2xl transition-all duration-300 ${isActive
                                    ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/25 translate-x-1'
                                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground hover:translate-x-1'
                                    }`}
                            >
                                <item.icon className={`h-5 w-5 mr-3 transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div className="p-6 border-t border-border/50">
                    <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-3 text-sm font-bold text-red-500 rounded-2xl hover:bg-red-50 dark:hover:bg-red-950/20 transition-all active:scale-95"
                    >
                        <LogOut className="h-5 w-5 mr-3" />
                        Terminate Session
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <div className="flex-1 flex flex-col relative overflow-hidden">
                {/* Header */}
                <header className="h-20 border-b bg-background/60 backdrop-blur-lg flex items-center justify-between px-8 z-10">
                    <div className="flex flex-col">
                        <span className="text-[10px] uppercase tracking-[0.2em] font-black text-primary/60">Operational Matrix</span>
                        <h2 className="text-xl font-black tracking-tight">{user?.full_name || 'Anonymous Operating System'}</h2>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex flex-col text-right mr-2">
                            <span className="text-[10px] font-black uppercase text-muted-foreground tracking-widest">{user?.role} Access</span>
                            <span className="text-xs font-bold text-green-500 flex items-center justify-end">
                                <div className="h-1.5 w-1.5 rounded-full bg-green-500 mr-2 animate-pulse" />
                                System Online
                            </span>
                        </div>
                        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-primary to-indigo-600 p-[1px] shadow-lg shadow-primary/20">
                            <div className="h-full w-full rounded-[15px] bg-card flex items-center justify-center text-primary font-black text-lg">
                                {user?.username?.charAt(0).toUpperCase()}
                            </div>
                        </div>
                    </div>
                </header>

                <main className="flex-1 overflow-y-auto p-8 relative">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={location.pathname}
                            initial={{ opacity: 0, y: 15, scale: 0.98 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: -15, scale: 0.98 }}
                            transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                            className="min-h-full"
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </main>
            </div>
        </div>
    );
};

export default Layout;
