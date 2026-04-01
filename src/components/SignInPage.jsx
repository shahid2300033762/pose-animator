import React, { useState } from 'react';
import API_BASE from '../config.js';

const SignInPage = ({ onHome, onLogin, onSignUp }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_BASE}/api/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                console.log('Login successful:', data);
                onLogin(data.user); // Pass user data back to App state
            } else {
                setError(data.message + (data.error ? ` - ${data.error}` : ''));
            }
        } catch (err) {
            console.error('Connection Error:', err);
            setError('Could not connect to the server. Please ensure the backend is running.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-surface font-body text-on-surface selection:bg-primary-container selection:text-on-primary-container min-h-screen w-full flex flex-col">
            {/* Nav */}
            <nav className="fixed top-0 w-full z-50 bg-slate-50/40 backdrop-blur-xl border-b border-slate-100 flex justify-between items-center px-6 md:px-12 py-4">
                <div className="flex items-center gap-4">
                    <div 
                        className="text-2xl font-black text-slate-900 italic font-headline tracking-tight cursor-pointer hover:opacity-80 transition-opacity"
                        onClick={onHome}
                    >
                        Pose Animator
                    </div>
                    <div className="h-5 w-px bg-slate-300 mx-2 hidden md:block"></div>
                    <button 
                        onClick={onHome}
                        className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-200/50 transition-all font-bold text-sm"
                    >
                        <span className="material-symbols-outlined text-[18px]">home</span>
                        Home
                    </button>
                </div>
                <div className="flex items-center gap-4">
                    <button className="material-symbols-outlined text-slate-600 hover:text-blue-500 transition-colors hidden sm:block">settings</button>
                    <button 
                        onClick={onSignUp}
                        className="bg-gradient-to-br from-primary to-primary-container text-white px-6 py-2 rounded-xl font-bold transition-all hover:shadow-lg hover:shadow-primary/30 active:scale-95"
                    >
                        Sign Up
                    </button>
                </div>
            </nav>

            <main className="flex-1 flex items-center justify-center pt-28 pb-12 kinetic-bg relative overflow-hidden w-full px-6 md:px-12">
                {/* Abstract Kinetic Elements */}
                <div className="absolute -top-24 -left-24 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
                <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-secondary/5 rounded-full blur-3xl pointer-events-none"></div>
                
                <div className="w-full max-w-md z-10">
                    {/* Login Card */}
                    <div className="bg-surface-container-lowest p-8 md:p-10 rounded-xl shadow-[0_20px_40px_rgba(44,47,49,0.06)] relative overflow-hidden">
                        {/* Inset Highlight */}
                        <div className="absolute top-0 left-0 w-1 h-full bg-primary"></div>
                        
                        <div className="mb-10">
                            <h1 className="text-3xl font-bold font-headline tracking-tight text-on-surface mb-2">Welcome Back</h1>
                            <p className="text-on-surface-variant text-sm font-medium">Enter your credentials to continue your creative journey.</p>
                        </div>
                        
                        {error && (
                            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm font-bold flex items-center gap-2">
                                <span className="material-symbols-outlined text-[18px]">error</span>
                                {error}
                            </div>
                        )}
                        
                        <form className="space-y-6" onSubmit={handleLogin}>
                            {/* Email Field */}
                            <div className="space-y-2">
                                <label className="block font-label text-sm font-semibold text-on-surface-variant ml-1">Email</label>
                                <div className="relative group">
                                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary opacity-0 group-focus-within:opacity-100 transition-opacity rounded-full"></div>
                                    <input 
                                        className="w-full bg-surface-container-highest border-none rounded-lg px-4 py-3 focus:ring-0 focus:bg-surface-dim transition-colors placeholder:text-outline-variant outline-none" 
                                        placeholder="name@example.com" 
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                            
                            {/* Password Field */}
                            <div className="space-y-2">
                                <label className="block font-label text-sm font-semibold text-on-surface-variant ml-1">Password</label>
                                <div className="relative group">
                                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-primary opacity-0 group-focus-within:opacity-100 transition-opacity rounded-full"></div>
                                    <input 
                                        className="w-full bg-surface-container-highest border-none rounded-lg px-4 py-3 focus:ring-0 focus:bg-surface-dim transition-colors placeholder:text-outline-variant outline-none" 
                                        placeholder="••••••••" 
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                            
                            {/* Options */}
                            <div className="flex items-center justify-between text-sm">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input 
                                        className="w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary/20 cursor-pointer accent-primary" 
                                        type="checkbox"
                                    />
                                    <span className="text-on-surface-variant group-hover:text-on-surface transition-colors font-medium">Remember me</span>
                                </label>
                                <a className="text-primary font-bold hover:text-primary-dim transition-colors" href="#">Forgot Password?</a>
                            </div>
                            
                            {/* Primary Action */}
                            <button 
                                type="submit"
                                disabled={loading}
                                className={`w-full py-4 bg-gradient-to-r from-primary to-primary-container text-white font-bold rounded-xl shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] transition-all font-headline tracking-wide uppercase text-sm mt-4 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`} 
                            >
                                {loading ? 'Signing In...' : 'Sign In'}
                            </button>
                        </form>
                        
                        {/* Divider */}
                        <div className="relative my-8">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full h-px bg-surface-container-high"></span>
                            </div>
                            <div className="relative flex justify-center text-xs uppercase tracking-widest font-bold">
                                <span className="bg-surface-container-lowest px-4 text-outline-variant">Or continue with</span>
                            </div>
                        </div>
                        
                        {/* Social Logins */}
                        <div className="grid grid-cols-2 gap-4">
                            <button className="flex items-center justify-center gap-2 py-3 px-4 bg-surface-container-high hover:bg-surface-dim rounded-lg transition-all active:scale-[0.97]">
                                <img 
                                    alt="Google" 
                                    className="w-5 h-5" 
                                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuAwl6KRoilEoM8oysdlhT8ih-gNP7m0eZzsWXX6ev-915o8z8GYL12sPGM9j9I-vZicG139jfnpVt3DEBvURnSXgk1yiau9BGRFXt9IqTCcIaRkUPoz8zUvJMxj9QuhMROTpAXDSdIl-_orHIX3MuaPxoHkV52WssVldatCt--GlTZsw8SIUlPO2Nn_L7RwG_OjWM5jHptFmvfENgyUiFmMhJrtKjCKBW8zo9XdGQ57yU8xOROwDDxEuDtZo6kOM99qLA3cTm8mFS4"
                                />
                                <span className="font-label text-sm font-bold">Google</span>
                            </button>
                            <button className="flex items-center justify-center gap-2 py-3 px-4 bg-surface-container-high hover:bg-surface-dim rounded-lg transition-all active:scale-[0.97] text-slate-800">
                                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.041-1.416-4.041-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-11.386 8.199-11.386 0-6.627-5.373-12-12-12z"></path>
                                </svg>
                                <span className="font-label text-sm font-bold">GitHub</span>
                            </button>
                        </div>
                        
                        <p className="mt-8 text-center text-sm font-medium text-on-surface-variant">
                            Don't have an account? 
                            <button 
                                onClick={onSignUp}
                                className="text-primary font-bold hover:underline ml-1"
                            >
                                Sign Up
                            </button>
                        </p>
                    </div>
                    
                    {/* Asymmetric Accent Image */}
                    <div className="mt-12 opacity-90 hover:opacity-100 transition-opacity flex justify-center pb-4">
                        <div className="relative w-full aspect-video rounded-2xl overflow-hidden shadow-2xl rotate-1 max-w-[400px]">
                            <img 
                                className="w-full h-full object-cover" 
                                alt="Abstract neon human pose mannequin" 
                                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCawvUj-7iOKBGJj6zpWCB8EEmScoPuSfJtRYly2_m4DbBmZINVT9eqHZY1ctNxkbvFZPiMaz6rZyoRbBw-b4DPHmH7HtWOMfyiZAM3muE-DTHNVo5k-5nFTMwhpjFmcXgUFgR0IuydmulmFA1IJeE3KPhQT6OydJyyX-aMXwsvxnd8W_DXGCbJ1p0OUIoGnospOZYOy2pzc_Dsgzcm8tYe-TDOq-s15G2rDA6qvXoOpzTkvVYvFHLbnSLaeg9km3nLkHokADC9mBA"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent"></div>
                        </div>
                    </div>
                </div>
            </main>

        </div>
    );
};

export default SignInPage;
