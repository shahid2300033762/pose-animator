import React, { useState } from 'react';

const SignUpPage = ({ onHome, onSignIn, onRegister }) => {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                console.log('Registration successful:', data);
                onRegister(data.user); // Successfully registered with user data
            } else {
                setError(data.message || 'Registration failed');
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
                    <button 
                        onClick={onSignIn}
                        className="text-slate-600 hover:text-primary font-bold text-sm transition-colors"
                    >
                        Sign In
                    </button>
                    <button className="bg-gradient-to-br from-primary to-primary-container text-white px-6 py-2 rounded-xl font-bold transition-all hover:shadow-lg hover:shadow-primary/30 active:scale-95">Sign Up</button>
                </div>
            </nav>

            <main className="flex-1 flex items-center justify-center pt-28 pb-12 kinetic-bg relative overflow-hidden w-full px-6 md:px-12">
                <div className="absolute -top-24 -left-24 w-96 h-96 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
                <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-secondary/5 rounded-full blur-3xl pointer-events-none"></div>
                
                <div className="w-full max-w-md z-10">
                    <div className="bg-surface-container-lowest p-8 md:p-10 rounded-xl shadow-[0_20px_40px_rgba(44,47,49,0.06)] relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-1 h-full bg-primary"></div>
                        
                        <div className="mb-8">
                            <h1 className="text-3xl font-bold font-headline tracking-tight text-on-surface mb-2">Create Account</h1>
                            <p className="text-on-surface-variant text-sm font-medium">Join our community of creators today.</p>
                        </div>
                        
                        {error && (
                            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm font-bold flex items-center gap-2">
                                <span className="material-symbols-outlined text-[18px]">error</span>
                                {error}
                            </div>
                        )}
                        
                        <form className="space-y-4" onSubmit={handleRegister}>
                            {/* Name Field */}
                            <div className="space-y-1">
                                <label className="block font-label text-xs font-bold text-on-surface-variant ml-1 uppercase tracking-wider">Full Name</label>
                                <div className="relative group">
                                    <input 
                                        className="w-full bg-surface-container-highest border-none rounded-lg px-4 py-3 focus:ring-1 focus:ring-primary/20 focus:bg-surface-dim transition-all outline-none" 
                                        placeholder="John Doe" 
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            {/* Email Field */}
                            <div className="space-y-1">
                                <label className="block font-label text-xs font-bold text-on-surface-variant ml-1 uppercase tracking-wider">Email Address</label>
                                <div className="relative group">
                                    <input 
                                        className="w-full bg-surface-container-highest border-none rounded-lg px-4 py-3 focus:ring-1 focus:ring-primary/20 focus:bg-surface-dim transition-all outline-none" 
                                        placeholder="name@example.com" 
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                            
                            {/* Password Field */}
                            <div className="space-y-1">
                                <label className="block font-label text-xs font-bold text-on-surface-variant ml-1 uppercase tracking-wider">Password</label>
                                <div className="relative group">
                                    <input 
                                        className="w-full bg-surface-container-highest border-none rounded-lg px-4 py-3 focus:ring-1 focus:ring-primary/20 focus:bg-surface-dim transition-all outline-none" 
                                        placeholder="••••••••" 
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>

                            {/* Confirm Password Field */}
                            <div className="space-y-1">
                                <label className="block font-label text-xs font-bold text-on-surface-variant ml-1 uppercase tracking-wider">Confirm Password</label>
                                <div className="relative group">
                                    <input 
                                        className="w-full bg-surface-container-highest border-none rounded-lg px-4 py-3 focus:ring-1 focus:ring-primary/20 focus:bg-surface-dim transition-all outline-none" 
                                        placeholder="••••••••" 
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        required
                                    />
                                </div>
                            </div>
                            
                            <button 
                                type="submit"
                                disabled={loading}
                                className={`w-full py-4 bg-gradient-to-r from-primary to-primary-container text-white font-bold rounded-xl shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 active:scale-[0.98] transition-all font-headline tracking-wide uppercase text-sm mt-6 ${loading ? 'opacity-70 cursor-not-allowed' : ''}`} 
                            >
                                {loading ? 'Creating Account...' : 'Create Account'}
                            </button>
                        </form>
                        
                        <p className="mt-8 text-center text-sm font-medium text-on-surface-variant">
                            Already have an account? 
                            <button 
                                onClick={onSignIn}
                                className="text-primary font-bold hover:underline ml-1"
                            >
                                Sign In
                            </button>
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default SignUpPage;
