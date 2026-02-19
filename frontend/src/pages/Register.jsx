import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, User, Loader2, AlertCircle } from 'lucide-react';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        full_name: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useAuth();
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(formData);
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 font-sans">
            <div className="max-w-md w-full space-y-8 bg-card p-8 rounded-xl shadow-lg border">
                <div className="text-center">
                    <h2 className="mt-6 text-3xl font-bold text-foreground tracking-tight">Create Account</h2>
                    <p className="mt-2 text-sm text-muted-foreground">Join the AI-powered inventory system</p>
                </div>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative flex items-center" role="alert">
                        <AlertCircle className="w-5 h-5 mr-2" />
                        <span className="block sm:inline">{error}</span>
                    </div>
                )}

                <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div className="relative">
                            <User className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                            <input
                                name="full_name"
                                type="text"
                                required
                                value={formData.full_name}
                                onChange={handleChange}
                                className="appearance-none rounded-md relative block w-full px-10 py-3 border border-input placeholder-muted-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary sm:text-sm"
                                placeholder="Full Name"
                            />
                        </div>
                        <div className="relative">
                            <User className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                            <input
                                name="username"
                                type="text"
                                required
                                value={formData.username}
                                onChange={handleChange}
                                className="appearance-none rounded-md relative block w-full px-10 py-3 border border-input placeholder-muted-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary sm:text-sm"
                                placeholder="Username"
                            />
                        </div>
                        <div className="relative">
                            <Mail className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                            <input
                                name="email"
                                type="email"
                                required
                                value={formData.email}
                                onChange={handleChange}
                                className="appearance-none rounded-md relative block w-full px-10 py-3 border border-input placeholder-muted-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary sm:text-sm"
                                placeholder="Email address"
                            />
                        </div>
                        <div className="relative">
                            <Lock className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                            <input
                                name="password"
                                type="password"
                                required
                                value={formData.password}
                                onChange={handleChange}
                                className="appearance-none rounded-md relative block w-full px-10 py-3 border border-input placeholder-muted-foreground text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary sm:text-sm"
                                placeholder="Password"
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-primary-foreground bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-70 disabled:cursor-not-allowed transition-all"
                        >
                            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Sign up'}
                        </button>
                    </div>
                </form>

                <div className="text-center text-sm">
                    <span className="text-muted-foreground">Already have an account? </span>
                    <Link to="/login" className="font-medium text-primary hover:text-primary/80 transition-colors">
                        Login here
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Register;
