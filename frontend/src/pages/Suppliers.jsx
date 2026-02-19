import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { Truck, Star, MapPin, Phone, Mail, Plus, Edit, X, Save, Activity } from 'lucide-react';

const Suppliers = () => {
    const [suppliers, setSuppliers] = useState([]);
    const [riskData, setRiskData] = useState({});
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [currentSupplier, setCurrentSupplier] = useState(null);
    const [formData, setFormData] = useState({
        name: '',
        contact_person: '',
        email: '',
        phone: '',
        address: '',
        city: '',
        country: '',
        rating: '5.0'
    });

    const fetchRisks = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.get('/api/v1/ai/autonomous/risk/suppliers', { headers });

            // Transform array to map for easy lookup
            const riskMap = {};
            if (response.data.risks) {
                response.data.risks.forEach(r => {
                    riskMap[r.supplier_id] = r;
                });
            }
            setRiskData(riskMap);
        } catch (error) {
            console.error("Error fetching risks:", error);
        }
    };

    const fetchSuppliers = async () => {
        try {
            const response = await api.get('/api/v1/suppliers');
            setSuppliers(response.data.suppliers || []);
            // Fetch risks after suppliers are loaded
            fetchRisks();
        } catch (error) {
            console.error("Error fetching suppliers:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSuppliers();
    }, []);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const openAddModal = () => {
        setCurrentSupplier(null);
        setFormData({
            name: '',
            contact_person: '',
            email: '',
            phone: '',
            address: '',
            city: '',
            country: '',
            rating: '5.0'
        });
        setIsModalOpen(true);
    };

    const openEditModal = (supplier) => {
        setCurrentSupplier(supplier);
        setFormData({
            name: supplier.name,
            contact_person: supplier.contact_person || '',
            email: supplier.email || '',
            phone: supplier.phone || '',
            address: supplier.address || '',
            city: supplier.city || '',
            country: supplier.country || '',
            rating: supplier.rating.toString()
        });
        setIsModalOpen(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};

            const payload = {
                ...formData,
                rating: parseFloat(formData.rating)
            };

            if (currentSupplier) {
                await axios.put(`/api/v1/suppliers/${currentSupplier.id}`, payload, { headers });
            } else {
                await axios.post('/api/v1/suppliers', payload, { headers });
            }

            setIsModalOpen(false);
            fetchSuppliers();
        } catch (error) {
            console.error("Error saving supplier:", error);
            alert("Failed to save supplier.");
        }
    };

    if (loading) return <div className="p-6">Loading suppliers...</div>;

    return (
        <div className="p-6 relative">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold flex items-center">
                    <Truck className="mr-2" /> Supplier Management
                </h1>
                <button
                    onClick={openAddModal}
                    className="bg-primary text-primary-foreground px-4 py-2 rounded-md flex items-center hover:bg-primary/90"
                >
                    <Plus className="mr-2 h-4 w-4" /> Add Supplier
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {suppliers.map((supplier) => (
                    <div key={supplier.id} className="bg-card text-card-foreground rounded-lg border shadow-sm p-6 relative group">
                        <button
                            onClick={() => openEditModal(supplier)}
                            className="absolute top-4 right-4 text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            <Edit className="h-4 w-4" />
                        </button>

                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-semibold">{supplier.name}</h3>
                                <p className="text-sm text-muted-foreground">{supplier.contact_person}</p>
                            </div>
                            <div className="flex items-center bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 px-2 py-1 rounded-md text-xs font-bold">
                                <Star className="w-3 h-3 mr-1 fill-current" />
                                {supplier.rating}
                            </div>
                        </div>

                        <div className="space-y-2 text-sm">
                            <div className="flex items-center text-muted-foreground">
                                <Mail className="w-4 h-4 mr-2" />
                                <a href={`mailto:${supplier.email}`} className="hover:text-primary transition-colors">{supplier.email}</a>
                            </div>
                            <div className="flex items-center text-muted-foreground">
                                <Phone className="w-4 h-4 mr-2" />
                                <span>{supplier.phone}</span>
                            </div>
                            <div className="flex items-center text-muted-foreground">
                                <MapPin className="w-4 h-4 mr-2" />
                                <span>{supplier.city}, {supplier.country}</span>
                            </div>
                        </div>

                        <div className="mt-4 pt-4 border-t flex justify-between text-xs text-muted-foreground">
                            <span>Products: {supplier.product_count || 0}</span>
                            <span>Orders: {supplier.total_orders || 0}</span>
                        </div>

                        {/* AI Risk Section */}
                        <div className="mt-4 bg-slate-100 dark:bg-slate-800 p-3 rounded-lg border border-slate-200 dark:border-slate-700">
                            <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1">
                                <Activity className="w-3 h-3" /> AI Risk Profile
                            </div>
                            {riskData[supplier.id] ? (
                                <div className="flex justify-between items-center">
                                    <div className="flex flex-col">
                                        <span className={`text-sm font-bold ${riskData[supplier.id].risk_level === 'High' ? 'text-red-500' :
                                            riskData[supplier.id].risk_level === 'Medium' ? 'text-amber-500' :
                                                'text-emerald-500'
                                            }`}>
                                            {riskData[supplier.id].risk_level} Risk
                                        </span>
                                        <span className="text-[10px] text-slate-400">Score: {riskData[supplier.id].risk_score}</span>
                                    </div>
                                    <div className="h-1.5 w-16 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${riskData[supplier.id].risk_level === 'High' ? 'bg-red-500' :
                                                riskData[supplier.id].risk_level === 'Medium' ? 'bg-amber-500' :
                                                    'bg-emerald-500'
                                                }`}
                                            style={{ width: `${riskData[supplier.id].risk_score * 100}%` }}
                                        />
                                    </div>
                                </div>
                            ) : (
                                <div className="flex justify-between items-center text-xs text-slate-400 italic">
                                    <span>Analyzing...</span>
                                    <div className="h-4 w-4 rounded-full border-2 border-slate-300 border-t-slate-500 animate-spin" />
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {suppliers.length === 0 && (
                    <div className="col-span-full text-center py-12 text-muted-foreground">
                        No suppliers found.
                    </div>
                )}
            </div>

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card text-card-foreground rounded-lg shadow-lg w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto border">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-xl font-bold">{currentSupplier ? 'Edit Supplier' : 'Add New Supplier'}</h2>
                            <button onClick={() => setIsModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                                <X className="h-6 w-6" />
                            </button>
                        </div>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Company Name</label>
                                    <input name="name" required value={formData.name} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Contact Person</label>
                                    <input name="contact_person" value={formData.contact_person} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Email</label>
                                    <input type="email" name="email" value={formData.email} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Phone</label>
                                    <input name="phone" value={formData.phone} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium">Address</label>
                                <input name="address" value={formData.address} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                            </div>
                            <div className="grid grid-cols-3 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">City</label>
                                    <input name="city" value={formData.city} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Country</label>
                                    <input name="country" value={formData.country} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium">Rating</label>
                                    <input type="number" step="0.1" max="5" min="0" name="rating" value={formData.rating} onChange={handleInputChange} className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm" />
                                </div>
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button type="button" onClick={() => setIsModalOpen(false)} className="px-4 py-2 border rounded-md hover:bg-accent text-muted-foreground">Cancel</button>
                                <button type="submit" className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 flex items-center">
                                    <Save className="mr-2 h-4 w-4" /> Save Supplier
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Suppliers;
