import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Package, ShoppingCart, Truck, AlertTriangle, TrendingUp, LogOut, Zap, ClipboardList, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <aside className="w-64 border-r bg-card hidden md:block">
                <div className="h-16 flex items-center px-6 border-b">
                    <TrendingUp className="h-6 w-6 text-primary mr-2" />
                    <span className="font-bold text-lg">AI Inventory</span>
                </div>
                <nav className="p-4 space-y-2">
                    <Link to="/" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <LayoutDashboard className="h-5 w-5 mr-3" />
                        Dashboard
                    </Link>
                    <Link to="/products" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <Package className="h-5 w-5 mr-3" />
                        Products
                    </Link>
                    <Link to="/sales" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <ShoppingCart className="h-5 w-5 mr-3" />
                        Sales
                    </Link>
                    <Link to="/suppliers" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <Truck className="h-5 w-5 mr-3" />
                        Suppliers
                    </Link>
                    <Link to="/orders" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <ClipboardList className="h-5 w-5 mr-3 text-indigo-400" />
                        Orders
                    </Link>
                    <Link to="/analytics" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <TrendingUp className="h-5 w-5 mr-3" />
                        Analytics
                    </Link>
                    <Link to="/optimization" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <Zap className="h-5 w-5 mr-3 text-indigo-500" />
                        AI Optimization
                    </Link>
                    <Link to="/security" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <ShieldCheck className="h-5 w-5 mr-3 text-rose-500" />
                        AI Security
                    </Link>
                    <Link to="/alerts" className="flex items-center px-4 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                        <AlertTriangle className="h-5 w-5 mr-3" />
                        Alerts
                    </Link>
                </nav>
                <div className="absolute bottom-4 left-0 w-64 px-4">
                    <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm font-medium text-red-500 rounded-md hover:bg-red-50 dark:hover:bg-red-900/10"
                    >
                        <LogOut className="h-5 w-5 mr-3" />
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                <header className="h-16 border-b bg-card flex items-center justify-between px-6">
                    <div className="text-sm text-muted-foreground">
                        Welcome back, <strong>{user?.full_name || user?.username || 'User'}</strong>
                        <span className="ml-2 text-xs bg-primary/10 text-primary px-2 py-0.5 rounded capitalize">{user?.role}</span>
                    </div>
                    <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                        {user?.username?.charAt(0).toUpperCase()}
                    </div>
                </header>
                {children}
            </main>
        </div>
    );
};

export default Layout;
