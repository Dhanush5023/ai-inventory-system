import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    MessageSquare, X, Send, Bot, User,
    Loader2, Sparkles, TrendingUp,
    Zap, ShieldCheck, Activity, Target
} from 'lucide-react';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';

const AIAssistant = () => {
    const { user } = useAuth();
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'proactive'
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'QUANTUM NEXUS Intel initialized. Matrix active. How can I facilitate your business orchestration today?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [marketInt, setMarketInt] = useState(null);
    const [hasProactiveNotice, setHasProactiveNotice] = useState(false);
    const messagesEndRef = useRef(null);

    const isAdmin = user?.role === 'admin' || user?.role === 'manager';

    useEffect(() => {
        if (isAdmin) {
            fetchMarketIntelligence();
        }
    }, [isAdmin]);

    const fetchMarketIntelligence = async () => {
        try {
            const res = await api.get('/api/v1/analytics/market-intelligence');
            setMarketInt(res.data);
            setHasProactiveNotice(true);
        } catch (error) {
            console.error("AI Assistant could not fetch intelligence:", error);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await api.post('/api/v1/ai/chatbot/query', { question: input });
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.answer }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Neural link interrupted. Re-synchronizing brain...' }]);
        } finally {
            setIsLoading(false);
        }
    };

    if (!isAdmin) return null;

    return (
        <div className="fixed bottom-8 right-8 z-[100]">
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="glass-card w-[400px] h-[600px] rounded-[2.5rem] border border-primary/20 shadow-2xl overflow-hidden flex flex-col mb-6"
                    >
                        {/* Header */}
                        <div className="bg-gradient-to-br from-primary to-indigo-600 p-6 text-white shrink-0">
                            <div className="flex justify-between items-center mb-4">
                                <div className="flex items-center gap-3">
                                    <div className="h-8 w-8 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-md">
                                        <Sparkles className="h-4 w-4" />
                                    </div>
                                    <span className="font-black text-sm uppercase tracking-widest text-white/90">QUANTUM NEXUS INTELLIGENCE</span>
                                </div>
                                <button onClick={() => setIsOpen(false)} className="hover:rotate-90 transition-transform duration-300">
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="flex gap-2">
                                <button
                                    onClick={() => setActiveTab('chat')}
                                    className={`px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase transition-all ${activeTab === 'chat' ? 'bg-white text-primary' : 'bg-white/10 hover:bg-white/20'
                                        }`}
                                >
                                    NEURAL INTERFACE
                                </button>
                                {isAdmin && (
                                    <button
                                        onClick={() => { setActiveTab('proactive'); setHasProactiveNotice(false); }}
                                        className={`px-4 py-1.5 rounded-full text-[10px] font-black tracking-widest uppercase transition-all relative ${activeTab === 'proactive' ? 'bg-white text-primary' : 'bg-white/10 hover:bg-white/20'
                                            }`}
                                    >
                                        PROACTIVE INSIGHTS
                                        {hasProactiveNotice && (
                                            <span className="absolute -top-1 -right-1 h-2 w-2 bg-red-400 rounded-full animate-ping" />
                                        )}
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-6 scrollbar-none space-y-4">
                            {activeTab === 'chat' ? (
                                <div className="space-y-4">
                                    {messages.map((msg, i) => (
                                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`max-w-[85%] p-4 rounded-3xl text-sm font-medium leading-relaxed ${msg.role === 'user'
                                                ? 'bg-primary text-white rounded-tr-none'
                                                : 'bg-accent/50 text-foreground rounded-tl-none border'
                                                }`}>
                                                {msg.content}
                                            </div>
                                        </div>
                                    ))}
                                    {isLoading && (
                                        <div className="flex justify-start">
                                            <div className="bg-accent/50 p-4 rounded-3xl rounded-tl-none border flex items-center gap-3">
                                                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                                                <span className="text-xs font-black uppercase tracking-widest text-muted-foreground">Neural Processing...</span>
                                            </div>
                                        </div>
                                    )}
                                    <div ref={messagesEndRef} />
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {(marketInt?.optimizations || []).map((opt, i) => (
                                        <motion.div
                                            key={i}
                                            initial={{ x: -20, opacity: 0 }}
                                            animate={{ x: 0, opacity: 1 }}
                                            transition={{ delay: i * 0.1 }}
                                            className="p-5 rounded-[2rem] bg-accent/30 border border-primary/10 space-y-3"
                                        >
                                            <div className="flex justify-between items-center">
                                                <div className="flex items-center gap-2 text-[10px] font-black text-primary uppercase tracking-widest">
                                                    <Zap className="h-3 w-3" /> Strategy Suggestion
                                                </div>
                                                <span className="font-black text-xs text-green-500">₹{opt.potential_savings.toLocaleString()} ROI</span>
                                            </div>
                                            <p className="text-sm font-bold leading-relaxed">{opt.action}</p>
                                            <button className="w-full py-3 bg-white dark:bg-slate-900 border rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-primary hover:text-white transition-all">
                                                Execute Optimization
                                            </button>
                                        </motion.div>
                                    ))}

                                    <div className="p-6 rounded-[2rem] bg-slate-950 text-white space-y-4 relative overflow-hidden">
                                        <div className="absolute top-0 right-0 p-4 opacity-10"><Activity className="h-12 w-12" /></div>
                                        <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Headline Brief</span>
                                        <p className="text-xs font-bold leading-relaxed relative z-10">{marketInt?.brief?.summary}</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input Area */}
                        {activeTab === 'chat' && (
                            <form onSubmit={handleSend} className="p-6 border-t border-border/50 shrink-0">
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        placeholder="Interface with Matrix..."
                                        className="w-full bg-accent/40 border-none rounded-2xl py-4 pl-6 pr-14 outline-none focus:ring-2 focus:ring-primary/20 font-bold text-sm"
                                    />
                                    <button
                                        type="submit"
                                        disabled={isLoading}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 bg-primary text-white rounded-xl flex items-center justify-center shadow-lg shadow-primary/20 hover:scale-105 transition-all disabled:opacity-50"
                                    >
                                        <Send className="h-4 w-4" />
                                    </button>
                                </div>
                            </form>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Toggle Button */}
            <motion.button
                onClick={() => setIsOpen(!isOpen)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className={`h-16 w-16 rounded-[1.5rem] shadow-2xl flex items-center justify-center transition-all duration-500 relative ${isOpen ? 'bg-slate-950 text-white rotate-90' : 'bg-primary text-white'
                    }`}
            >
                {isOpen ? <X className="h-6 w-6" /> : <Bot className="h-7 w-7" />}
                {!isOpen && hasProactiveNotice && (
                    <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full border-2 border-white flex items-center justify-center text-[8px] font-black">1</span>
                )}
            </motion.button>
        </div>
    );
};

export default AIAssistant;
