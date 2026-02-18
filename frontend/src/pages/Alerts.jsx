import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const Alerts = () => {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAlerts = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            const response = await axios.get('/api/v1/alerts', { headers });
            setAlerts(response.data.alerts || []);
        } catch (error) {
            console.error("Error fetching alerts:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();
    }, []);

    const handleResolve = async (id) => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { Authorization: `Bearer ${token}` } : {};
            await axios.put(`/api/v1/alerts/${id}`, { is_resolved: true }, { headers });
            fetchAlerts();
        } catch (error) {
            console.error("Error resolving alert:", error);
            alert("Failed to update alert status.");
        }
    };

    if (loading) return <div className="p-6">Loading alerts...</div>;

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6 flex items-center">
                <AlertTriangle className="mr-2" /> Alert Center
            </h1>

            <div className="bg-card text-card-foreground rounded-lg border shadow-sm">
                <div className="p-0 overflow-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-muted-foreground uppercase bg-muted/50">
                            <tr>
                                <th className="px-6 py-3">Severity</th>
                                <th className="px-6 py-3">Product</th>
                                <th className="px-6 py-3">Message</th>
                                <th className="px-6 py-3">Date</th>
                                <th className="px-6 py-3">Status</th>
                                <th className="px-6 py-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {alerts.map((alert) => (
                                <tr key={alert.id} className="border-b hover:bg-muted/50 transition-colors">
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded-full text-xs font-semibold
                                            ${alert.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' :
                                                alert.severity === 'high' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' :
                                                    'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                                            }`}>
                                            {alert.severity.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-medium">{alert.product_name}</td>
                                    <td className="px-6 py-4">{alert.message}</td>
                                    <td className="px-6 py-4">{new Date(alert.created_at).toLocaleDateString()}</td>
                                    <td className="px-6 py-4">
                                        {alert.is_resolved ? (
                                            <span className="flex items-center text-green-600">
                                                <CheckCircle className="w-4 h-4 mr-1" /> Resolved
                                            </span>
                                        ) : (
                                            <span className="flex items-center text-red-600">
                                                <XCircle className="w-4 h-4 mr-1" /> Open
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        {!alert.is_resolved && (
                                            <button
                                                onClick={() => handleResolve(alert.id)}
                                                className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded hover:bg-primary/90"
                                            >
                                                Mark Resolved
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                            {alerts.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="px-6 py-4 text-center text-muted-foreground">
                                        No active alerts.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Alerts;
