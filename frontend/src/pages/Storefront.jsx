import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Package, Search, ShoppingCart, Tag,
    AlertCircle, CheckCircle2, ChevronRight,
    X, CreditCard, ShieldCheck, Zap
} from 'lucide-react';
import api from '../utils/api';

const CATEGORY_STYLES = {
    'Consumer Electronics': { gradient: 'from-blue-500/10 to-indigo-500/10', iconColor: 'text-blue-500', spotColor: 'bg-blue-500/20' },
    'FMCG & Groceries': { gradient: 'from-emerald-500/10 to-teal-500/10', iconColor: 'text-emerald-500', spotColor: 'bg-emerald-500/20' },
    'Textiles & Apparel': { gradient: 'from-rose-500/10 to-pink-500/10', iconColor: 'text-rose-500', spotColor: 'bg-rose-500/20' },
    'Home & Kitchen': { gradient: 'from-amber-500/10 to-orange-500/10', iconColor: 'text-amber-500', spotColor: 'bg-amber-500/20' },
    'default': { gradient: 'from-slate-500/10 to-slate-600/10', iconColor: 'text-slate-500', spotColor: 'bg-slate-500/20' }
};

const Storefront = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('');
    const [categories, setCategories] = useState([]);
    const [checkoutItem, setCheckoutItem] = useState(null);
    const [notification, setNotification] = useState(null);

    useEffect(() => {
        fetchProducts();
        fetchCategories();
    }, [category, search]);

    const fetchProducts = async () => {
        setLoading(true);
        try {
            const params = { limit: 50, query: search || undefined, category: category || undefined };
            const response = await api.get('/api/v1/products', { params });
            setProducts(response.data.products || []);
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await api.get('/api/v1/products/categories');
            setCategories(response.data);
        } catch (error) {
            console.error("Error fetching categories:", error);
        }
    };

    const handlePurchase = async (product) => {
        try {
            await api.post('/api/v1/sales', {
                product_id: product.id,
                quantity: 1,
                unit_price: product.unit_price,
                notes: "Premium Checkout Flow"
            });

            setNotification({ type: 'success', message: `Order Confirmed: ${product.name} is on its way.` });
            setCheckoutItem(null);
            setTimeout(() => setNotification(null), 5000);
            fetchProducts();
        } catch (error) {
            setNotification({ type: 'error', message: "Financial transaction failed. Please retry." });
            setTimeout(() => setNotification(null), 5000);
        }
    };

    const container = {
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.05 } }
    };

    const cardAnim = {
        hidden: { opacity: 0, scale: 0.95, y: 20 },
        show: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } }
    };

    return (
        <div className="space-y-12 pb-20">
            {/* Market Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center gap-2 text-primary font-black text-xs uppercase tracking-[0.3em] mb-3">
                        <Zap className="h-3 w-3" /> Global Marketplace
                    </div>
                    <h1 className="text-6xl font-black tracking-tighter leading-none mb-4">Select Items.</h1>
                    <p className="text-xl text-muted-foreground font-medium max-w-lg">Premium inventory sourced from verified vendors across the Bangalore circuit.</p>
                </div>
            </div>

            {/* Search and Filters */}
            <div className="flex flex-col md:flex-row gap-4 items-center sticky top-0 z-10 py-4 -mt-4 bg-background/80 backdrop-blur-xl">
                <div className="relative group flex-1 w-full">
                    <Search className="absolute left-6 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    <input
                        type="text"
                        placeholder="Scan inventory for specific units..."
                        className="w-full pl-16 pr-8 py-5 rounded-[2rem] border bg-card/60 focus:ring-4 focus:ring-primary/10 focus:border-primary outline-none text-lg font-bold transition-all"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none w-full md:w-auto">
                    <button
                        onClick={() => setCategory('')}
                        className={`px-8 py-5 rounded-[2rem] border text-sm font-black whitespace-nowrap transition-all ${category === '' ? 'bg-primary text-primary-foreground border-primary' : 'bg-card/60 hover:bg-accent text-muted-foreground'
                            }`}
                    >
                        ALL UNITS
                    </button>
                    {categories.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setCategory(cat)}
                            className={`px-8 py-5 rounded-[2rem] border text-sm font-black whitespace-nowrap transition-all ${category === cat ? 'bg-primary text-primary-foreground border-primary' : 'bg-card/60 hover:bg-accent text-muted-foreground'
                                }`}
                        >
                            {cat.toUpperCase()}
                        </button>
                    ))}
                </div>
            </div>

            {/* Product Grid */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                    {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                        <div key={i} className="h-96 rounded-[2.5rem] bg-card/40 border animate-pulse" />
                    ))}
                </div>
            ) : (
                <motion.div
                    variants={container}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8"
                >
                    {products.map((product) => {
                        const style = CATEGORY_STYLES[product.category] || CATEGORY_STYLES.default;
                        return (
                            <motion.div
                                key={product.id}
                                variants={cardAnim}
                                className="group glass-card rounded-[2.5rem] overflow-hidden flex flex-col h-full border hover:border-primary/50 transition-all duration-500"
                            >
                                <div className={`h-64 bg-gradient-to-br ${style.gradient} flex items-center justify-center p-12 relative overflow-hidden`}>
                                    <div className={`absolute inset-0 opacity-20 transition-transform duration-700 group-hover:scale-110 ${style.spotColor}`} />
                                    <Package className={`h-24 w-24 ${style.iconColor} relative z-10 transition-all duration-700 group-hover:scale-110`} />
                                    <div className="absolute bottom-4 left-6 bg-white/80 dark:bg-black/80 backdrop-blur-md px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border border-white/20">
                                        {product.sku}
                                    </div>
                                </div>
                                <div className="p-8 flex-1 flex flex-col">
                                    <div className="flex justify-between items-start mb-4">
                                        <span className={`text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest border ${style.iconColor} bg-white/50 dark:bg-black/50`}>
                                            {product.category}
                                        </span>
                                        <span className={`text-[10px] font-black flex items-center gap-1.5 ${product.current_stock > 10 ? 'text-green-500' : 'text-orange-500'
                                            }`}>
                                            <div className={`h-1.5 w-1.5 rounded-full ${product.current_stock > 10 ? 'bg-green-500' : 'bg-orange-500 animate-pulse'}`} />
                                            {product.current_stock} UNS.
                                        </span>
                                    </div>
                                    <h3 className="font-black text-2xl mb-2 tracking-tight line-clamp-1">{product.name}</h3>
                                    <p className="text-sm text-muted-foreground font-medium leading-relaxed mb-8 flex-1 line-clamp-2">
                                        {product.description || "Premium operational equipment for industrial and consumer deployment."}
                                    </p>

                                    <div className="flex items-center justify-between gap-4">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] font-black text-muted-foreground uppercase tracking-widest mb-0.5">Mkt. Val</span>
                                            <span className="text-2xl font-black tracking-tight">₹{product.unit_price.toLocaleString()}</span>
                                        </div>
                                        <button
                                            onClick={() => setCheckoutItem(product)}
                                            className="h-14 w-14 premium-button rounded-2xl flex items-center justify-center text-white"
                                        >
                                            <ChevronRight className="h-6 w-6" />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        );
                    })}
                </motion.div>
            )}

            {/* Checkout Modal */}
            <AnimatePresence>
                {checkoutItem && (
                    <div className="fixed inset-0 z-50 flex items-center justify-end p-6 md:p-12">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setCheckoutItem(null)}
                            className="absolute inset-0 bg-background/60 backdrop-blur-xl"
                        />
                        <motion.div
                            initial={{ x: '100%', opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            exit={{ x: '100%', opacity: 0 }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="relative w-full max-w-md h-full bg-card shadow-2xl rounded-[3rem] border border-border/50 flex flex-col overflow-hidden"
                        >
                            <div className="p-8 border-b flex justify-between items-center">
                                <span className="text-xs font-black uppercase tracking-[0.3em] text-primary">Transaction Protocol</span>
                                <button onClick={() => setCheckoutItem(null)} className="p-3 hover:bg-accent rounded-2xl transition-all">
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="flex-1 p-10 space-y-10 overflow-y-auto">
                                <div>
                                    <h2 className="text-4xl font-black tracking-tighter mb-4">{checkoutItem.name}</h2>
                                    <div className="flex items-center gap-3">
                                        <div className="px-3 py-1 bg-accent rounded-lg text-xs font-black tracking-widest">{checkoutItem.sku}</div>
                                        <div className="px-3 py-1 bg-green-50 text-green-600 rounded-lg text-xs font-black tracking-widest uppercase">Secured Unit</div>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex justify-between items-center text-sm font-bold border-b pb-4 border-dashed">
                                        <span className="text-muted-foreground uppercase tracking-widest text-[10px]">Stock Status</span>
                                        <span>AVAILABLE ({checkoutItem.current_stock})</span>
                                    </div>
                                    <div className="flex justify-between items-center text-sm font-bold border-b pb-4 border-dashed">
                                        <span className="text-muted-foreground uppercase tracking-widest text-[10px]">Shipping Logic</span>
                                        <span>EXPRESS INTEL DELIVERY</span>
                                    </div>
                                </div>

                                <div className="p-8 rounded-[2rem] bg-slate-950 text-white space-y-6 shadow-2xl shadow-indigo-500/10">
                                    <div className="flex justify-between items-center">
                                        <span className="text-[10px] font-black uppercase tracking-widest text-white/40">Total Acquisition Cost</span>
                                        <CreditCard className="h-5 w-5 text-indigo-400" />
                                    </div>
                                    <div className="text-4xl font-black tracking-tighter">₹{checkoutItem.unit_price.toLocaleString()}</div>
                                </div>

                                <div className="flex items-center gap-3 text-xs font-bold text-muted-foreground bg-accent/50 p-4 rounded-2xl border border-dashed">
                                    <ShieldCheck className="h-5 w-5 text-green-500" />
                                    Ensured by Secure Matrix Protocol. Your transaction is encrypted.
                                </div>
                            </div>

                            <div className="p-8 bg-background">
                                <button
                                    onClick={() => handlePurchase(checkoutItem)}
                                    className="w-full premium-button text-white py-6 rounded-[2rem] font-black text-lg uppercase tracking-widest shadow-2xl"
                                >
                                    CONFIRM ACQUISITION
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Notifications */}
            <AnimatePresence>
                {notification && (
                    <motion.div
                        initial={{ y: 50, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        exit={{ y: 50, opacity: 0 }}
                        className="fixed bottom-10 left-1/2 -translate-x-1/2 z-[60] px-8 py-5 rounded-3xl glass-card flex items-center gap-4 border-primary/20 shadow-2xl border min-w-[320px]"
                    >
                        {notification.type === 'success' ? <CheckCircle2 className="h-6 w-6 text-green-500" /> : <AlertCircle className="h-6 w-6 text-rose-500" />}
                        <span className="font-black text-sm uppercase tracking-widest">{notification.message}</span>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Storefront;
