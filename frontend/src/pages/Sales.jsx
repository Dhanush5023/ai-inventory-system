import React, { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';
import { ShoppingCart, Search, Plus, X, Trash2, CreditCard, RefreshCw, AlertCircle } from 'lucide-react';

const Sales = () => {
    // Data State
    const [sales, setSales] = useState([]);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // POS State
    const [cart, setCart] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [processing, setProcessing] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [recommendations, setRecommendations] = useState([]);
    const [loadingRecs, setLoadingRecs] = useState(false);

    const fetchProducts = useCallback(async (search = '') => {
        try {
            const safeSearch = encodeURIComponent(search);
            const response = await api.get(`/api/v1/products?limit=100&query=${safeSearch}`);
            const productsList = response.data?.products;
            setProducts(Array.isArray(productsList) ? productsList : []);
        } catch (error) {
            console.error("Error fetching products:", error);
            setProducts([]);
        }
    }, []);

    const fetchSales = useCallback(async () => {
        setRefreshing(true);
        try {
            const response = await api.get('/api/v1/sales');
            const salesList = response.data?.sales;
            setSales(Array.isArray(salesList) ? salesList : []);
            setError(null);
        } catch (error) {
            console.error("Error fetching sales:", error);
            setError("Failed to load sales history.");
        } finally {
            setRefreshing(false);
        }
    }, []);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            await Promise.all([fetchSales(), fetchProducts('')]);
            setLoading(false);
        };
        loadData();
        const pollTimer = setInterval(fetchSales, 30000);
        return () => clearInterval(pollTimer);
    }, [fetchSales, fetchProducts]);

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchProducts(searchTerm);
        }, 300);
        return () => clearTimeout(timer);
    }, [searchTerm, fetchProducts]);

    useEffect(() => {
        const fetchRecs = async () => {
            if (processing) return;
            setLoadingRecs(true);
            try {
                const cartIds = cart.map(item => item.product_id);
                const response = await api.post('/api/v1/analytics/recommendations', { cart_product_ids: cartIds });
                setRecommendations(response.data || []);
            } catch (error) {
                console.error("Error fetching recommendations:", error);
            } finally {
                setLoadingRecs(false);
            }
        };

        const timer = setTimeout(fetchRecs, 1000);
        return () => clearTimeout(timer);
    }, [cart, processing]);

    const addToCart = (product) => {
        if (!product || product.current_stock <= 0) {
            alert("Out of stock!");
            return;
        }

        setCart(prev => {
            const existing = prev.find(item => item.product_id === product.id);
            if (existing) {
                if (existing.quantity >= product.current_stock) {
                    alert("Cannot add more than available stock!");
                    return prev;
                }
                return prev.map(item =>
                    item.product_id === product.id
                        ? { ...item, quantity: item.quantity + 1, total: (item.quantity + 1) * item.unit_price }
                        : item
                );
            }
            return [...prev, {
                product_id: product.id,
                name: product.name,
                unit_price: Number(product.unit_price) || 0,
                quantity: 1,
                total: Number(product.unit_price) || 0
            }];
        });
    };

    const removeFromCart = (productId) => {
        setCart(prev => prev.filter(item => item.product_id !== productId));
    };

    const updateQuantity = (productId, newQty) => {
        if (newQty < 1) return;
        const product = products.find(p => p.id === productId);
        if (!product) return;
        if (newQty > product.current_stock) {
            alert(`Only ${product.current_stock} available!`);
            return;
        }
        setCart(prev => prev.map(item =>
            item.product_id === productId
                ? { ...item, quantity: newQty, total: newQty * item.unit_price }
                : item
        ));
    };

    const clearCart = () => setCart([]);
    const cartTotal = cart.reduce((sum, item) => sum + (item.total || 0), 0);

    const handleCheckout = async () => {
        if (cart.length === 0) return;
        setProcessing(true);
        try {
            const payload = {
                items: cart.map(item => ({
                    product_id: item.product_id,
                    quantity: item.quantity,
                    unit_price: item.unit_price,
                    notes: "POS Transaction"
                }))
            };
            await api.post('/api/v1/sales/bulk', payload);
            setTimeout(async () => {
                await Promise.all([fetchSales(), fetchProducts(searchTerm)]);
            }, 500);
            alert("Transaction Complete!");
            setCart([]);
        } catch (error) {
            console.error("Checkout failed:", error);
            alert("Transaction failed: " + (error.response?.data?.detail || error.message));
        } finally {
            setProcessing(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
            <RefreshCw className="h-8 w-8 animate-spin text-indigo-600 mr-2" />
            <span className="font-semibold text-slate-600">Loading AI POS System...</span>
        </div>
    );

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden">
            <div className="w-2/3 p-6 flex flex-col border-r bg-gray-50/50 dark:bg-gray-900/50">
                <div className="mb-6 flex justify-between items-center">
                    <h1 className="text-2xl font-bold flex items-center">
                        <ShoppingCart className="mr-2" /> Products
                    </h1>
                    <div className="relative w-64">
                        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search products..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-9 pr-4 py-2 rounded-md border text-sm"
                        />
                    </div>
                </div>

                {recommendations.length > 0 && (
                    <div className="mb-4 bg-indigo-50 dark:bg-indigo-900/10 p-4 rounded-xl border border-indigo-100 dark:border-indigo-500/20">
                        <h3 className="text-sm font-bold text-indigo-800 dark:text-indigo-300 mb-3 flex items-center">
                            <span className="bg-indigo-600 text-white p-1 rounded-md mr-2"><AlertCircle className="w-3 h-3" /></span>
                            AI Suggested Add-ons
                        </h3>
                        <div className="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
                            {recommendations.map(product => (
                                <button
                                    key={product.id}
                                    onClick={() => addToCart(product)}
                                    className="flex-shrink-0 w-48 bg-white dark:bg-slate-800 p-3 rounded-lg border border-indigo-200 dark:border-indigo-500/30 hover:shadow-md transition-all text-left group"
                                >
                                    <div className="font-semibold text-sm truncate text-slate-800 dark:text-slate-200 group-hover:text-indigo-600">{product.name}</div>
                                    <div className="flex justify-between items-center mt-2">
                                        <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                                            ₹{Number(product.unit_price).toLocaleString()}
                                        </span>
                                        <span className="text-[10px] bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300 px-1.5 py-0.5 rounded-full">
                                            Add +
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-3 gap-4 overflow-y-auto content-start pr-2 pb-4 flex-1 min-h-0">
                    {products.map(product => (
                        <button
                            key={product.id}
                            onClick={() => addToCart(product)}
                            disabled={!product.current_stock}
                            className={`p-4 rounded-lg border text-left transition-all hover:shadow-md flex flex-col justify-between h-32 ${!product.current_stock
                                ? 'opacity-50 cursor-not-allowed bg-gray-100 dark:bg-gray-800'
                                : 'bg-card hover:bg-accent/50 cursor-pointer'
                                }`}
                        >
                            <div className="flex justify-between w-full">
                                <span className="font-semibold truncate pr-2" title={product.name}>{product.name}</span>
                                <span className="text-primary font-bold">
                                    ₹{Number(product.unit_price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                </span>
                            </div>
                            <div className="text-xs text-muted-foreground mt-1">SKU: {product.sku}</div>
                            <div className={`text-sm mt-auto ${(product.current_stock || 0) < 10 ? 'text-red-500 font-medium' : 'text-green-600'
                                }`}>
                                {(!product.current_stock) ? 'Out of Stock' : `${product.current_stock} in stock`}
                            </div>
                        </button>
                    ))}
                    {products.length === 0 && !loading && (
                        <div className="col-span-3 text-center text-muted-foreground py-10">
                            No products found.
                        </div>
                    )}
                </div>

                <div className="mt-6 flex-none h-64 flex flex-col min-h-0 border-t pt-4">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold flex items-center">
                            <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Recent Transactions
                        </h2>
                        <div className="flex items-center gap-4">
                            {error && <span className="text-sm text-red-500 flex items-center"><AlertCircle className="w-4 h-4 mr-1" /> {error}</span>}
                            <button
                                onClick={fetchSales}
                                disabled={refreshing}
                                className="p-1.5 hover:bg-muted rounded-full transition-colors text-muted-foreground disabled:opacity-50 border shadow-sm"
                                title="Refresh History"
                            >
                                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                            </button>
                        </div>
                    </div>
                    <div className="bg-card rounded-lg border shadow-sm flex-1 overflow-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-muted-foreground uppercase bg-muted/50 sticky top-0">
                                <tr>
                                    <th className="px-4 py-3">Time</th>
                                    <th className="px-4 py-3">Product</th>
                                    <th className="px-4 py-3">Qty</th>
                                    <th className="px-4 py-3">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {sales.slice(0, 20).map((sale) => (
                                    <tr key={sale.id} className="border-b hover:bg-muted/50 transition-colors">
                                        <td className="px-4 py-2">
                                            {sale.sale_date ? new Date(sale.sale_date).toLocaleTimeString() : '-'}
                                        </td>
                                        <td className="px-4 py-2 font-medium">{sale.product_name || 'Unknown'}</td>
                                        <td className="px-4 py-2">{sale.quantity}</td>
                                        <td className="px-4 py-2 text-green-600 font-bold">
                                            ₹{(Number(sale.total_amount) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                        </td>
                                    </tr>
                                ))}
                                {sales.length === 0 && (
                                    <tr>
                                        <td colSpan="4" className="px-4 py-8 text-center text-muted-foreground">
                                            No recent sales.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div className="w-1/3 bg-card border-l flex flex-col p-6 shadow-xl z-10">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold flex items-center">
                        <ShoppingCart className="mr-2 h-5 w-5" /> Current Sale
                    </h2>
                    {cart.length > 0 && (
                        <button onClick={clearCart} className="text-sm text-red-500 hover:text-red-700">Clear Cart</button>
                    )}
                </div>

                <div className="flex-1 overflow-y-auto space-y-4 pr-1">
                    {cart.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-muted-foreground pb-20">
                            <ShoppingCart className="h-16 w-16 mb-4 opacity-20" />
                            <p>Cart is empty</p>
                            <p className="text-sm">Select products to start sale</p>
                        </div>
                    ) : (
                        cart.map((item) => (
                            <div key={item.product_id} className="flex justify-between items-center p-3 rounded-lg border bg-background/50">
                                <div className="flex-1">
                                    <div className="font-medium">{item.name}</div>
                                    <div className="text-xs text-muted-foreground">₹{Number(item.unit_price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} / unit</div>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="flex items-center border rounded-md">
                                        <button
                                            onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                                            className="px-2 py-1 hover:bg-accent"
                                        >-</button>
                                        <span className="w-8 text-center text-sm">{item.quantity}</span>
                                        <button
                                            onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                                            className="px-2 py-1 hover:bg-accent"
                                        >+</button>
                                    </div>
                                    <div className="font-bold w-16 text-right">₹{Number(item.total).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
                                    <button
                                        onClick={() => removeFromCart(item.product_id)}
                                        className="text-muted-foreground hover:text-red-500"
                                    >
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                <div className="border-t pt-4 mt-4 space-y-4">
                    <div className="flex justify-between items-end">
                        <span className="text-muted-foreground">Total Amount</span>
                        <span className="text-3xl font-bold text-primary">₹{(Number(cartTotal) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                    </div>

                    <button
                        onClick={handleCheckout}
                        disabled={cart.length === 0 || processing}
                        className="w-full py-4 bg-primary text-primary-foreground text-lg font-bold rounded-lg shadow hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex justify-center items-center transition-all"
                    >
                        {processing ? <RefreshCw className="h-5 w-5 animate-spin mr-2" /> : <CreditCard className="h-5 w-5 mr-2" />}
                        {processing ? 'Processing...' : 'Complete Transaction'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Sales;
