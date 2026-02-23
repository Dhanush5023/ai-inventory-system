import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Sales from './pages/Sales';
import Suppliers from './pages/Suppliers';
import Alerts from './pages/Alerts';
import Analytics from './pages/Analytics';
import Optimization from './pages/Optimization';
import Orders from './pages/Orders';
import Security from './pages/Security';
import Storefront from './pages/Storefront';
import CustomerOrders from './pages/CustomerOrders';
import Profile from './pages/Profile';
import TrackOrder from './pages/TrackOrder';
import Layout from './components/Layout';
import AIAssistant from './components/AIAssistant';

const ProtectedRoute = ({ children, roles = [] }) => {
    const { isAuthenticated, user, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
                <div className="text-xl font-medium text-foreground">Loading application...</div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    if (roles.length > 0 && !roles.includes(user?.role)) {
        // Redirect to their respective "home" if they try to access unauthorized route
        const homePath = user?.role === 'customer' ? '/store' : '/';
        return <Navigate to={homePath} />;
    }

    return children;
};

// Home component to redirect based on role
const RoleBasedHome = () => {
    const { user } = useAuth();
    if (user?.role === 'customer') {
        return <Navigate to="/store" replace />;
    }
    return <Dashboard />;
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />

                    <Route
                        path="/*"
                        element={
                            <ProtectedRoute>
                                <Layout>
                                    <Routes>
                                        <Route path="/" element={<RoleBasedHome />} />
                                        <Route path="/store" element={<ProtectedRoute roles={['customer', 'admin']}><Storefront /></ProtectedRoute>} />
                                        <Route path="/my-orders" element={<ProtectedRoute roles={['customer', 'admin']}><CustomerOrders /></ProtectedRoute>} />
                                        <Route path="/profile" element={<ProtectedRoute roles={['customer', 'admin']}><Profile /></ProtectedRoute>} />
                                        <Route path="/track-order" element={<ProtectedRoute roles={['customer', 'admin']}><TrackOrder /></ProtectedRoute>} />

                                        <Route path="/products" element={<ProtectedRoute roles={['admin', 'manager']}><Products /></ProtectedRoute>} />
                                        <Route path="/sales" element={<ProtectedRoute roles={['admin', 'manager']}><Sales /></ProtectedRoute>} />
                                        <Route path="/suppliers" element={<ProtectedRoute roles={['admin', 'manager']}><Suppliers /></ProtectedRoute>} />
                                        <Route path="/alerts" element={<ProtectedRoute roles={['admin', 'manager']}><Alerts /></ProtectedRoute>} />
                                        <Route path="/analytics" element={<ProtectedRoute roles={['admin', 'manager']}><Analytics /></ProtectedRoute>} />
                                        <Route path="/optimization" element={<ProtectedRoute roles={['admin', 'manager']}><Optimization /></ProtectedRoute>} />
                                        <Route path="/orders" element={<ProtectedRoute roles={['admin', 'manager']}><Orders /></ProtectedRoute>} />
                                        <Route path="/security" element={<ProtectedRoute roles={['admin', 'manager']}><Security /></ProtectedRoute>} />

                                        {/* Catch all for authenticated users */}
                                        <Route path="*" element={<Navigate to="/" replace />} />
                                    </Routes>
                                </Layout>
                            </ProtectedRoute>
                        }
                    />
                </Routes>
                <AIAssistant />
            </Router>
        </AuthProvider>
    );
}

export default App;
