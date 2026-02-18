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
import Layout from './components/Layout';
import AIAssistant from './components/AIAssistant';

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="flex h-screen items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
                <div className="text-xl font-medium text-foreground">Loading application...</div>
            </div>
        );
    }
    return isAuthenticated ? children : <Navigate to="/login" />;
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
                                        <Route path="/" element={<Dashboard />} />
                                        <Route path="/products" element={<Products />} />
                                        <Route path="/sales" element={<Sales />} />
                                        <Route path="/suppliers" element={<Suppliers />} />
                                        <Route path="/alerts" element={<Alerts />} />
                                        <Route path="/analytics" element={<Analytics />} />
                                        <Route path="/optimization" element={<Optimization />} />
                                        <Route path="/orders" element={<Orders />} />
                                        <Route path="/security" element={<Security />} />
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
