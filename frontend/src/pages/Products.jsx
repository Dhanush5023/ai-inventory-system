import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Package, Search, Filter, Plus, Edit, Trash2, X, Save, TrendingUp, Info, ArrowUpRight, Clock } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Products = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentProduct, setCurrentProduct] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        sku: '',
        category: '',
        unit_price: '',
        cost_price: '',
        current_stock: '',
        minimum_stock: '10',
        unit: 'pcs'
    });

    // Forecast State
    const [isForecastModalOpen, setIsForecastModalOpen] = useState(false);
    const [forecastData, setForecastData] = useState([]);
    const [forecastLoading, setForecastLoading] = useState(false);
    const [selectedProductForForecast, setSelectedProductForForecast] = useState(null);
    const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
    const [selectedProductDetail, setSelectedProductDetail] = useState(null);

    const fetchProducts = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.get('/api/v1/products', { headers });
            setProducts(response.data.products || []);
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const openAddModal = () => {
        setCurrentProduct(null);
        setFormData({
            name: '',
            sku: '',
            category: '',
            unit_price: '',
            cost_price: '',
            current_stock: '',
            minimum_stock: '10',
            unit: 'pcs'
        });
        setIsModalOpen(true);
    };

    const openEditModal = (product) => {
        setCurrentProduct(product);
        setFormData({
            name: product.name,
            sku: product.sku,
            category: product.category || '',
            unit_price: product.unit_price,
            cost_price: product.cost_price,
            current_stock: product.current_stock,
            minimum_stock: product.minimum_stock,
            unit: product.unit
        });
        setIsModalOpen(true);
    };

    const handleDelete = async (id) => {
        if (window.confirm('Are you sure you want to delete this product?')) {
            try {
                const token = localStorage.getItem('token');
                const headers = token ? { Authorization: `Bearer ${token}` } : {};
                await axios.delete(`/api/v1/products/${id}`, { headers });
                fetchProducts();
            } catch (error) {
                console.error("Error deleting product:", error);
                alert("Failed to delete product. It might be referenced in sales.");
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const payload = {
                ...formData,
                unit_price: parseFloat(formData.unit_price),
                cost_price: parseFloat(formData.cost_price),
                current_stock: parseInt(formData.current_stock),
                minimum_stock: parseInt(formData.minimum_stock)
            };

            if (currentProduct) {
                await axios.put(`/api/v1/products/${currentProduct.id}`, payload, { headers });
            } else {
                await axios.post('/api/v1/products', payload, { headers });
            }

            setIsModalOpen(false);
            fetchProducts();
        } catch (error) {
            console.error("Error saving product:", error);
            alert("Failed to save product. Check inputs.");
        }
    };

    const openForecastModal = async (product) => {
        setSelectedProductForForecast(product);
        setIsForecastModalOpen(true);
        setForecastLoading(true);
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            // Post to forecast endpoint
            const res = await axios.post('/api/v1/predictions/forecast', {
                product_id: product.id,
                horizon_days: 30
            }, { headers });

            setForecastData(res.data);
        } catch (error) {
            console.error("Error fetching forecast:", error);
            alert("Could not generate forecast. Insufficient data.");
            setIsForecastModalOpen(false);
        } finally {
            setForecastLoading(false);
        }
    };

    const filteredProducts = products.filter(product =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.sku.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) return <div className="p-6">Loading products...</div>;

    return (
        <div className="p-6 relative">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold flex items-center">
                    <Package className="mr-2" /> Products Inventory
                </h1>
                <button
                    onClick={openAddModal}
                    className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center hover:bg-primary/90"
                >
                    <Plus className="mr-2 h-4 w-4" /> Add Product
                </button>
            </div>

            <div className="bg-card text-card-foreground rounded-lg border shadow-sm">
                <div className="p-6 flex flex-col md:flex-row gap-4 border-b">
                    <div className="relative flex-1">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                        <input
                            type="text"
                            placeholder="Search by name or SKU..."
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 pl-8 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>
                <div className="p-0 overflow-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
                            <tr>
                                <th className="px-6 py-3">Name</th>
                                <th className="px-6 py-3">SKU</th>
                                <th className="px-6 py-3">Category</th>
                                <th className="px-6 py-3">Price</th>
                                <th className="px-6 py-3">Stock</th>
                                <th className="px-6 py-3">Status</th>
                                <th className="px-6 py-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredProducts.map((product) => (
                                <tr key={product.id} className="border-b hover:bg-muted/50 transition-colors">
                                    <td className="px-6 py-4 font-medium">{product.name}</td>
                                    <td className="px-6 py-4">{product.sku}</td>
                                    <td className="px-6 py-4">{product.category}</td>
                                    <td className="px-6 py-4">₹{(Number(product.unit_price) || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                                    <td className="px-6 py-4">{product.current_stock}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold
                                            ${product.current_stock === 0 ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                                                product.current_stock < product.minimum_stock ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400' :
                                                    'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                            }`}>
                                            {product.current_stock === 0 ? 'Out of Stock' :
                                                product.current_stock < product.minimum_stock ? 'Low Stock' : 'In Stock'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 flex gap-2">
                                        <button
                                            onClick={() => {
                                                setSelectedProductDetail(product);
                                                setIsDetailModalOpen(true);
                                            }}
                                            className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 mr-1"
                                            title="View Details"
                                        >
                                            <Info className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={() => openForecastModal(product)}
                                            className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300 mr-1"
                                            title="AI Forecast"
                                        >
                                            <TrendingUp className="h-4 w-4" />
                                        </button>
                                        <button onClick={() => openEditModal(product)} className="text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-300">
                                            <Edit className="h-4 w-4" />
                                        </button>
                                        <button onClick={() => handleDelete(product.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {filteredProducts.length === 0 && (
                                <tr>
                                    <td colSpan="7" className="px-6 py-4 text-center text-muted-foreground">
                                        No products found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Edit/Add Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card text-card-foreground rounded-lg shadow-lg w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto border">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-bold">{currentProduct ? 'Edit Product' : 'Add New Product'}</h2>
                            <button onClick={() => setIsModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                                <X className="h-6 w-6" />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Name</label>
                                    <input name="name" required value={formData.name} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">SKU</label>
                                    <input name="sku" required value={formData.sku} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Category</label>
                                    <input name="category" value={formData.category} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Unit</label>
                                    <input name="unit" value={formData.unit} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Cost Price</label>
                                    <input type="number" step="0.01" name="cost_price" required value={formData.cost_price} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Selling Price</label>
                                    <input type="number" step="0.01" name="unit_price" required value={formData.unit_price} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Current Stock</label>
                                    <input type="number" name="current_stock" required value={formData.current_stock} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Min Stock Alert</label>
                                    <input type="number" name="minimum_stock" required value={formData.minimum_stock} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 border rounded-md hover:bg-accent text-muted-foreground">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 flex items-center">
                                    <Save className="mr-2 h-4 w-4" /> Save Product
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Product Detail Modal */}
            {isDetailModalOpen && selectedProductDetail && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card text-card-foreground rounded-xl shadow-2xl w-full max-w-4xl p-8 border max-h-[90vh] overflow-y-auto relative animate-in fade-in zoom-in duration-200">
                        <button
                            onClick={() => setIsDetailModalOpen(false)}
                            className="absolute top-6 right-6 text-muted-foreground hover:text-foreground transition-colors"
                        >
                            <X className="h-7 w-7" />
                        </button>

                        <div className="mb-8">
                            <span className="text-sm font-semibold text-primary uppercase tracking-wider">{selectedProductDetail.category}</span>
                            <h2 className="text-4xl font-extrabold mt-1">{selectedProductDetail.name}</h2>
                            <p className="text-muted-foreground text-lg mt-2">{selectedProductDetail.sku} • {selectedProductDetail.unit}</p>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                            {/* Left Column: Basic Info & AI Insights */}
                            <div className="space-y-8">
                                <div className="bg-muted/30 p-6 rounded-xl border border-border/50">
                                    <h3 className="text-xl font-bold mb-5 flex items-center">
                                        <TrendingUp className="mr-3 h-6 w-6 text-primary" /> AI Optimization Insights
                                    </h3>
                                    {selectedProductDetail.ai_insights ? (
                                        <div className="grid grid-cols-2 gap-6">
                                            <div className="space-y-1">
                                                <div className="text-sm text-muted-foreground flex items-center">
                                                    EOQ <Info className="h-3 w-3 ml-1 cursor-help" title="Economic Order Quantity: Most cost-effective amount to order" />
                                                </div>
                                                <div className="text-2xl font-black text-primary">{selectedProductDetail.ai_insights.eoq}</div>
                                            </div>
                                            <div className="space-y-1">
                                                <div className="text-sm text-muted-foreground">Reorder Point</div>
                                                <div className="text-2xl font-black text-blue-500">{selectedProductDetail.ai_insights.reorder_point}</div>
                                            </div>
                                            <div className="space-y-1">
                                                <div className="text-sm text-muted-foreground">Safety Stock</div>
                                                <div className="text-2xl font-black text-orange-500">{selectedProductDetail.ai_insights.safety_stock}</div>
                                            </div>
                                            <div className="space-y-1">
                                                <div className="text-sm text-muted-foreground">Current Stock</div>
                                                <div className={`text-2xl font-black ${selectedProductDetail.current_stock <= selectedProductDetail.ai_insights.reorder_point ? 'text-red-500' : 'text-green-500'}`}>
                                                    {selectedProductDetail.current_stock}
                                                </div>
                                            </div>
                                            <div className="col-span-2 mt-4 pt-4 border-t border-border/50">
                                                <div className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-2">AI Recommendation</div>
                                                <div className={`text-lg font-bold p-3 rounded-lg text-center ${selectedProductDetail.ai_insights.recommendation === 'Restock Now' ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                                                    {selectedProductDetail.ai_insights.recommendation.toUpperCase()}
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        <p className="text-muted-foreground italic py-4">Generating AI optimization data...</p>
                                    )}
                                </div>

                                <div className="bg-muted/20 p-6 rounded-xl border border-border/30">
                                    <h3 className="text-xl font-bold mb-4 flex items-center">
                                        <Package className="mr-3 h-6 w-6 text-primary" /> Inventory Status
                                    </h3>
                                    <div className="space-y-4">
                                        <div className="flex justify-between items-center bg-background/50 p-3 rounded-lg">
                                            <span className="text-muted-foreground">Current Stock Level</span>
                                            <span className="font-bold text-xl">{selectedProductDetail.current_stock} units</span>
                                        </div>
                                        <div className="flex justify-between items-center bg-background/50 p-3 rounded-lg">
                                            <span className="text-muted-foreground">Average Profit Margin</span>
                                            <span className="font-bold text-xl text-green-600">{selectedProductDetail.profit_margin}%</span>
                                        </div>
                                        <div className="flex justify-between items-center bg-background/50 p-3 rounded-lg">
                                            <span className="text-muted-foreground">Supplier</span>
                                            <span className="font-bold text-lg">{selectedProductDetail.supplier_name || 'Generic'}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Right Column: Pending Orders & Forecast */}
                            <div className="space-y-8">
                                <div className="bg-blue-500/5 p-6 rounded-xl border border-blue-500/20">
                                    <h3 className="text-xl font-bold mb-5 flex items-center">
                                        <Clock className="mr-3 h-6 w-6 text-blue-500" /> Pending Inbound Orders
                                    </h3>
                                    <div className="space-y-3">
                                        {selectedProductDetail.pending_orders && selectedProductDetail.pending_orders.length > 0 ? (
                                            selectedProductDetail.pending_orders.map(order => (
                                                <div key={order.order_id} className="flex justify-between items-center p-4 bg-background rounded-xl border border-border shadow-sm hover:shadow-md transition-shadow">
                                                    <div>
                                                        <div className="font-bold text-blue-600">{order.order_number}</div>
                                                        <div className="text-sm text-muted-foreground">{order.quantity} {selectedProductDetail.unit} ordered</div>
                                                    </div>
                                                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase ${order.status === 'draft' ? 'bg-orange-100 text-orange-800' :
                                                            order.status === 'shipped' ? 'bg-blue-100 text-blue-800' :
                                                                'bg-gray-100 text-gray-800'
                                                        }`}>
                                                        {order.status}
                                                    </span>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="text-center py-10 border-2 border-dashed border-border/50 rounded-xl">
                                                <p className="text-muted-foreground">No pending orders found</p>
                                                <button
                                                    onClick={() => {
                                                        setIsDetailModalOpen(false);
                                                        // Navigate or open restock logic?
                                                    }}
                                                    className="mt-3 text-sm font-bold text-primary hover:underline hover:text-primary/80"
                                                >
                                                    Generate Restock Order →
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-xl font-bold flex items-center">
                                        <TrendingUp className="mr-3 h-6 w-6 text-primary" /> Demand Projection
                                    </h3>
                                    <div className="h-48 w-full bg-muted/10 rounded-xl border border-dashed flex items-center justify-center p-4">
                                        {selectedProductDetail.demand_forecast && selectedProductDetail.demand_forecast.length > 0 ? (
                                            <ResponsiveContainer width="100%" height="100%">
                                                <LineChart data={selectedProductDetail.demand_forecast}>
                                                    <Line type="monotone" dataKey="predicted_demand" stroke="#8884d8" strokeWidth={3} dot={false} />
                                                    <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }} />
                                                </LineChart>
                                            </ResponsiveContainer>
                                        ) : (
                                            <p className="text-muted-foreground">Forecast data visualization</p>
                                        )}
                                    </div>
                                    <button
                                        onClick={() => openForecastModal(selectedProductDetail)}
                                        className="w-full py-4 bg-primary/10 hover:bg-primary/20 text-primary font-bold rounded-xl transition-all flex items-center justify-center group"
                                    >
                                        Open Full AI Analysis <ArrowUpRight className="ml-2 h-5 w-5 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Products;
