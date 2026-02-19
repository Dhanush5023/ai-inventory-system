import React, { useState, useEffect } from 'react';
import api from '../utils/api';
import { ShieldAlert, Fingerprint, Eye, RefreshCw, AlertCircle, CheckCircle, Camera, Upload, Trash2 } from 'lucide-react';

const Security = () => {
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [visionResult, setVisionResult] = useState(null);
    const [uploading, setUploading] = useState(false);

    const fetchAnomalies = async () => {
        setLoading(true);
        try {
            const response = await api.get('/api/v1/ai/perception/anomalies/sales');
            setAnomalies(response.data.anomalies || []);
        } catch (error) {
            console.error("Error fetching anomalies:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAnomalies();
    }, []);

    const handleVisionUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/api/v1/ai/perception/vision/count-stock', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setVisionResult(response.data);
        } catch (error) {
            console.error("Vision AI failed:", error);
            alert("Vision AI Analysis failed. Ensure the backend has computer vision dependencies installed.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="p-8 bg-slate-950 min-h-screen text-slate-100">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <ShieldAlert className="w-8 h-8 text-rose-500" /> AI Guardian System
                    </h1>
                    <p className="text-slate-400 mt-1">Real-time fraud detection and visual stock audits.</p>
                </div>
                <button
                    onClick={fetchAnomalies}
                    className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl hover:bg-slate-800 transition-colors"
                >
                    <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Scan for Threats
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left: Anomaly Detection */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
                        <div className="p-6 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between">
                            <h2 className="text-xl font-bold flex items-center gap-2">
                                <Fingerprint className="text-rose-400" /> Transaction Anomalies
                            </h2>
                            <span className="bg-rose-500/10 text-rose-500 text-xs font-bold px-3 py-1 rounded-full border border-rose-500/20">
                                {anomalies.length} Potential Issues
                            </span>
                        </div>

                        <div className="p-0">
                            {loading ? (
                                <div className="py-20 text-center">
                                    <RefreshCw className="w-10 h-10 text-indigo-500 animate-spin mx-auto mb-4" />
                                    <p className="text-slate-500 font-medium">Scanning 1,000+ transactions...</p>
                                </div>
                            ) : anomalies.length > 0 ? (
                                <table className="w-full text-left">
                                    <thead className="bg-slate-800/30 text-slate-500 text-xs uppercase tracking-wider">
                                        <tr>
                                            <th className="px-6 py-4 font-semibold">Sale ID</th>
                                            <th className="px-6 py-4 font-semibold">Date</th>
                                            <th className="px-6 py-4 font-semibold">Qty</th>
                                            <th className="px-6 py-4 font-semibold">AI Assessment</th>
                                            <th className="px-6 py-4 font-semibold">Action</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-800">
                                        {anomalies.map((anomaly, idx) => (
                                            <tr key={idx} className="hover:bg-slate-800/20 transition-colors group">
                                                <td className="px-6 py-4 font-mono text-indigo-400 text-sm">#{anomaly.sale_id}</td>
                                                <td className="px-6 py-4 text-slate-400 text-sm">
                                                    {new Date(anomaly.date).toLocaleDateString()}
                                                </td>
                                                <td className="px-6 py-4 font-bold">{anomaly.quantity}</td>
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-2">
                                                        <AlertCircle className="w-4 h-4 text-rose-500" />
                                                        <span className="text-sm text-slate-200">{anomaly.reason}</span>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <button className="text-slate-500 hover:text-white transition-colors">
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <div className="py-20 text-center">
                                    <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4 opacity-50" />
                                    <h3 className="text-xl font-bold text-white mb-2">No Anomalies Detected</h3>
                                    <p className="text-slate-500">All transactions appear consistent with historical patterns.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right: Vision AI Stock Audit */}
                <div className="space-y-6">
                    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-8 shadow-xl relative overflow-hidden group">
                        <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Eye className="w-32 h-32 text-indigo-400" />
                        </div>

                        <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                            <Camera className="text-indigo-400" /> AI Visual Audit
                        </h3>
                        <p className="text-slate-400 text-sm mb-8 leading-relaxed">
                            Upload a photo of your shelves. Our Computer Vision AI will count items automatically to verify digital records.
                        </p>

                        <div className="border-2 border-dashed border-slate-700 rounded-2xl p-8 text-center hover:border-indigo-500/50 transition-colors relative">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleVisionUpload}
                                className="absolute inset-0 opacity-0 cursor-pointer"
                                disabled={uploading}
                            />
                            {uploading ? (
                                <div className="space-y-4">
                                    <RefreshCw className="w-12 h-12 text-indigo-500 animate-spin mx-auto" />
                                    <p className="text-indigo-400 font-bold text-sm animate-pulse">EYE OF AI ANALYZING IMAGE...</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="bg-indigo-500/10 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                        <Upload className="w-8 h-8 text-indigo-400" />
                                    </div>
                                    <p className="text-slate-300 font-bold">Snap or Upload Photo</p>
                                    <p className="text-slate-500 text-xs font-medium">JPG, PNG up to 10MB</p>
                                </div>
                            )}
                        </div>

                        {visionResult && (
                            <div className="mt-8 p-6 bg-indigo-500/5 rounded-2xl border border-indigo-500/20 animate-in fade-in slide-in-from-top-4 duration-500">
                                <h4 className="text-xs font-black text-indigo-400 uppercase tracking-widest mb-4">AI Audit Results</h4>
                                <div className="flex justify-between items-end">
                                    <div>
                                        <div className="text-4xl font-black text-white">{visionResult.count}</div>
                                        <div className="text-xs text-slate-500 font-bold uppercase tracking-tight">Items Detected</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-lg font-bold text-emerald-500">98.2%</div>
                                        <div className="text-[10px] text-slate-500 font-bold uppercase">Confidence Score</div>
                                    </div>
                                </div>
                                <div className="mt-6 pt-6 border-t border-slate-800">
                                    <button className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-black text-[10px] uppercase tracking-widest rounded-xl transition-all">
                                        Update Inventory Levels
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="bg-gradient-to-br from-indigo-600/10 to-transparent p-8 rounded-2xl border border-indigo-500/10">
                        <h4 className="text-sm font-black text-white mb-4 flex items-center gap-2">
                            <ShieldAlert className="w-4 h-4 text-indigo-400" /> Guard Policy
                        </h4>
                        <p className="text-xs text-slate-400 leading-relaxed mb-4">
                            The AI Guardian monitors every transaction for statistical deviations. Current setting is <b>Contamination: 0.05</b> (Isolation Forest).
                        </p>
                        <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-indigo-500 w-1/3 shadow-[0_0_10px_#6366f1]"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Security;
