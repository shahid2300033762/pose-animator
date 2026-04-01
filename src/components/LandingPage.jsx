import React, { useEffect } from 'react';

const LandingPage = ({ onLaunch, onSignIn, onSignUp }) => {
    useEffect(() => {
        const observerOptions = {
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el));
        
        return () => observer.disconnect();
    }, []);

    return (
        <div className="bg-background text-on-surface selection:bg-primary/20 h-screen font-body overflow-hidden w-full flex flex-col">

            {/* TopNavBar */}
            <nav className="w-full shrink-0 z-50 bg-white/90 backdrop-blur-xl border-b border-slate-100 h-[72px] px-6 md:px-12">
                <div className="flex justify-between items-center h-full w-full">
                    <div className="flex items-center gap-4">
                        <div 
                            className="text-xl font-bold text-slate-900 italic font-headline tracking-tight cursor-pointer"
                            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                        >
                            Pose Animator
                        </div>
                        <div className="h-4 w-px bg-slate-200 mx-2 hidden md:block"></div>
                        <button 
                            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                            className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors font-semibold text-sm"
                        >
                            <span className="material-symbols-outlined text-[16px]">home</span>
                            Home
                        </button>
                    </div>
                    <div className="hidden md:flex items-center justify-center gap-8 font-body text-sm font-semibold tracking-wide flex-1">
                        <a className="text-slate-600 hover:text-slate-900 transition-colors cursor-pointer" onClick={onLaunch}>
                            Dashboard
                        </a>
                        <a className="text-slate-600 hover:text-slate-900 transition-colors cursor-pointer" onClick={onLaunch}>
                            Animate
                        </a>
                        <a className="text-slate-600 hover:text-slate-900 transition-colors cursor-pointer" href="#pricing">
                            Pricing
                        </a>
                    </div>
                    <div className="flex items-center justify-end gap-6 w-48">
                        <button onClick={onSignIn} className="text-slate-600 hover:text-slate-900 font-semibold text-sm transition-colors hidden sm:block">Sign In</button>
                        <button 
                            className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-bold shadow-sm hover:shadow-md hover:bg-blue-700 transition-all active:scale-95"
                            onClick={onSignUp}
                        >
                            Sign Up
                        </button>
                    </div>
                </div>
            </nav>

            {/* Main Content Area */}
            <main className="flex-1 w-full overflow-y-auto overflow-x-hidden relative scroll-smooth">
                {/* Hero Section */}
                <section className="relative min-h-[calc(100vh-72px)] flex items-center justify-center pt-10 md:pt-0 overflow-hidden w-full px-6 md:px-12">
                    {/* Background Noise & Gradients */}
                    <div className="absolute inset-0 z-0 pointer-events-none">
                        <div className="absolute top-0 right-0 w-[800px] h-[800px] bg-blue-50/40 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/3"></div>
                        <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-indigo-50/40 rounded-full blur-[100px] translate-y-1/2 -translate-x-1/3"></div>
                    </div>

                    <div className="w-full max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center relative z-10 lg:px-8">
                        {/* Left Content */}
                        <div className="space-y-6 md:space-y-8 animate-fade-in-up">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100/50">
                                <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                                <span className="text-[10px] font-bold text-blue-500 uppercase tracking-widest">Version 2.0 Live</span>
                            </div>
                            
                            <h1 className="text-6xl md:text-7xl lg:text-[5.5rem] font-headline font-black leading-[0.85] tracking-tighter text-slate-900 max-w-xl">
                                MOTION
                                <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-500 block mt-2">
                                    REDEFINED.
                                </span>
                            </h1>
                            
                            <p className="text-lg text-slate-500 font-medium leading-relaxed max-w-sm">
                                The professional suite for high-fidelity pose animation. Transform static vision into fluid performance with AI-driven kinetic precision.
                            </p>
                            
                            <div className="flex flex-wrap items-center gap-4 pt-2">
                                <button 
                                    className="bg-[#6366f1] text-white px-8 py-3.5 rounded-xl font-bold text-sm hover:shadow-[0_15px_30px_rgba(99,102,241,0.25)] transition-all hover:-translate-y-0.5 active:scale-95"
                                    onClick={onLaunch}
                                >
                                    Start Animating
                                </button>
                                <button className="px-8 py-3.5 rounded-xl font-bold text-sm text-slate-700 bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all hover:-translate-y-0.5 active:scale-95">
                                    View Showcase
                                </button>
                            </div>
                        </div>

                        {/* Right Image/Widget */}
                        <div className="relative group lg:ml-10">
                            <div className="relative aspect-square rounded-[2rem] overflow-hidden bg-slate-900 border border-slate-800 shadow-2xl transition-transform duration-700 hover:scale-[1.01]">
                                <img
                                    src="/hero_motion_capture.png"
                                    alt="Professional contemporary dancer in dynamic motion capture pose"
                                    className="w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform duration-[2000ms]"
                                />
                                
                                {/* Bottom Glass Banner Widget */}
                                <div className="absolute bottom-6 left-6 right-6">
                                    <div className="bg-white/20 backdrop-blur-md p-5 rounded-2xl border border-white/20 shadow-xl overflow-hidden relative">
                                        <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent pointer-events-none"></div>
                                        
                                        <div className="flex items-center justify-between mb-4 relative z-10">
                                            <span className="text-[10px] font-headline font-bold text-blue-500 uppercase tracking-widest leading-none">Motion Track 01</span>
                                            <span className="material-symbols-outlined text-blue-500/80 text-[14px] animate-[pulse_4s_infinite]">3d_rotation</span>
                                        </div>
                                        
                                        <div className="flex justify-between items-end relative z-10 h-10">
                                            {/* Custom Audio/Motion Visualizer Bars */}
                                            <div className="flex items-end gap-[3px] h-full object-bottom">
                                                <div className="w-[5px] rounded-full bg-blue-400/80 animate-[ping_1.5s_infinite] h-[50%]"></div>
                                                <div className="w-[5px] rounded-full bg-indigo-400/90 animate-[pulse_2s_infinite] h-[80%]"></div>
                                                <div className="w-[5px] rounded-full bg-purple-400 animate-[pulse_1.7s_infinite] h-[40%]"></div>
                                                <div className="w-[5px] rounded-full bg-blue-500/80 animate-[pulse_1.2s_infinite] h-[100%]"></div>
                                                <div className="w-[5px] rounded-full bg-indigo-500 animate-[pulse_2.2s_infinite] h-[60%]"></div>
                                                <div className="w-[5px] rounded-full bg-purple-500/90 animate-[pulse_1.8s_infinite] h-[30%]"></div>
                                                <div className="w-[5px] rounded-full bg-blue-400 animate-[pulse_2.5s_infinite] h-[70%]"></div>
                                            </div>
                                            
                                            <div className="text-blue-600 font-headline font-bold text-sm tracking-wide">
                                                24.00 FPS
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Process Section */}
                <section className="py-24 md:py-32 px-4 md:px-8 bg-slate-50 overflow-hidden">
                    <div className="w-full max-w-7xl mx-auto">

                        <div className="mb-20 flex flex-col md:flex-row md:items-end justify-between gap-12 reveal-on-scroll">
                            <div>
                                <h2 className="text-5xl font-headline font-bold mb-6 text-on-surface">The Precision Workflow</h2>
                                <p className="text-on-surface-variant max-w-xl text-lg">Move from concept to capture in three refined stages. No borders, just flow.</p>
                            </div>
                            <div className="w-full md:w-5/12 aspect-video rounded-2xl overflow-hidden shadow-2xl border-[12px] border-white group">
                                <img
                                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuDJqJEFnghXEXbf-sXrK24rmcaozi0NLnzi3VIigZ22oRJQIM-u-Z5Rn7cLdkhfJv2GKdyyGhSBOsZXxjy5swYHt8eNqEo1m4-Gbx0fNacivvjaU5B8uBIvnAfHF5DjOJZLzatOSp-rwcGaUKRUi_a9rkxvqqfxmHTo1iLDrgA6xLRRf4UVlzOG5MgfLQ-S1nJuiK_aRRjqsrpLajkSPMJJERf6glserhfhkiuqA6S0tgcGTOq464izlZVN5Rm-hUI2QtV2_2qB0Is"
                                    alt="3D Animation Rigging"
                                    className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110"
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            {/* Step 1 */}
                            <div className="md:col-span-2 bg-white p-12 rounded-3xl border border-outline-variant/50 flex flex-col justify-between group hover:border-primary/40 transition-all duration-500 shadow-sm hover:shadow-xl reveal-on-scroll" style={{ transitionDelay: '100ms' }}>
                                <div>
                                    <div className="text-primary text-6xl font-headline font-bold mb-8 group-hover:scale-110 transition-transform inline-block">01</div>
                                    <h3 className="text-3xl font-bold mb-6 text-on-surface">Pose Synthesis</h3>
                                    <p className="text-on-surface-variant leading-relaxed text-lg max-w-lg">Our neural engine interprets human movement with sub-millimeter accuracy, converting raw data into clean, manipulatable keyframes.</p>
                                </div>
                                <div className="mt-16 flex gap-6">
                                    <div className="w-14 h-14 rounded-xl bg-primary-container flex items-center justify-center transition-transform hover:rotate-12">
                                        <span className="material-symbols-outlined text-primary text-3xl">psychology</span>
                                    </div>
                                    <div className="w-14 h-14 rounded-xl bg-primary-container flex items-center justify-center transition-transform hover:-rotate-12">
                                        <span className="material-symbols-outlined text-secondary text-3xl">analytics</span>
                                    </div>
                                </div>
                            </div>
                            {/* Step 2 */}
                            <div className="bg-white p-12 rounded-3xl border border-outline-variant/50 group hover:border-secondary/40 transition-all duration-500 shadow-sm hover:shadow-xl reveal-on-scroll" style={{ transitionDelay: '200ms' }}>
                                <div className="text-secondary text-6xl font-headline font-bold mb-8 group-hover:scale-110 transition-transform inline-block">02</div>
                                <h3 className="text-3xl font-bold mb-6 text-on-surface">Kinetic Sculpting</h3>
                                <p className="text-on-surface-variant leading-relaxed text-lg">Refine every arc and pivot using our proprietary Bezier-Motion curves.</p>
                                <div className="mt-10 aspect-square rounded-2xl bg-surface-container overflow-hidden">
                                    <img
                                        src="https://lh3.googleusercontent.com/aida-public/AB6AXuDVzzuTYoCbnjzGsRzcoIhBrhwk8pwxyHrB8lyieiFc7BQcjYiIZDuRB-LGmp3Aw_9ba35RD-qAqjnUWFc776WH_DyeLDWE1W7KaUZw5lMzPi60H_pGb8CjCo4RZjAZ--8qLlYHJDkSpZMsVJfwZEEA38pL57O5BmHeS0z2VR4Ek_Xg14wD0lKPOi0FfeyTlJioKDiM3bTW_U9uYK4Giqwzd_4FYS_WqrDsRdEcq-n_t9_gPwBdZa6Cyd9gBBSpsJxCkeZ4GSGfrZ8"
                                        alt="Kinetic movement visualization"
                                        className="w-full h-full object-cover transition-transform duration-[1.5s] group-hover:scale-110"
                                    />
                                </div>
                            </div>
                            {/* Step 3 */}
                            <div className="md:col-span-3 bg-gradient-to-br from-primary to-secondary p-16 rounded-3xl flex flex-col md:flex-row items-center gap-16 text-white group reveal-on-scroll" style={{ transitionDelay: '300ms' }}>
                                <div className="flex-1">
                                    <div className="text-white/40 text-6xl font-headline font-bold mb-8">03</div>
                                    <h3 className="text-4xl font-bold mb-6">Universal Export</h3>
                                    <p className="text-white/80 leading-relaxed text-xl">Push your performance directly to Unreal, Unity, or Blender. One click, infinite compatibility.</p>
                                    <div className="mt-12 flex flex-wrap gap-10">
                                        <span className="text-sm font-bold tracking-[0.2em] text-white/50 uppercase transition-all hover:text-white hover:tracking-[0.4em]">FBX</span>
                                        <span className="text-sm font-bold tracking-[0.2em] text-white/50 uppercase transition-all hover:text-white hover:tracking-[0.4em]">OBJ</span>
                                        <span className="text-sm font-bold tracking-[0.2em] text-white/50 uppercase transition-all hover:text-white hover:tracking-[0.4em]">USDZ</span>
                                        <span className="text-sm font-bold tracking-[0.2em] text-white/50 uppercase transition-all hover:text-white hover:tracking-[0.4em]">GLTF</span>
                                    </div>
                                </div>
                                <div className="w-full md:w-5/12 aspect-video rounded-2xl overflow-hidden shadow-2xl border-[12px] border-white group relative">
                                    <img
                                        src="/universal_export_ui.png"
                                        alt="Universal Export Dashboard"
                                        className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Gallery Section */}
                <section className="py-24 md:py-32 px-4 md:px-8 bg-white">
                    <div className="w-full max-w-7xl mx-auto">

                        <div className="flex flex-col md:flex-row md:items-end justify-between mb-20 gap-8 reveal-on-scroll">
                            <h2 className="text-7xl font-headline font-bold tracking-tighter leading-none text-on-surface">THE<br /><span className="text-primary">ARCHIVE</span></h2>
                            <p className="text-on-surface-variant max-w-sm mb-2 text-lg font-body">A curated collection of performances captured using Kinetic Precision v2.0.</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <div className="lg:row-span-2 group relative rounded-2xl overflow-hidden aspect-[4/5] lg:aspect-auto shadow-xl reveal-on-scroll">
                                <img
                                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuC9hN1BNIfBTUNnJC9zNRSMC-4vLfPYkkdRtJh4NbnymWjssyV3KhWYtagZnqCE54tgCIx7Ds320B8voAGAzMHW_3yVVFjBCc50-UHY6vlvpXkanSc3Y-u7rxKVJxmS1mKE6UYa9k34md9VuW9_D1kXrpOOVS9szvLih-zm2gw-jQjGCLOdH3DhK10lZbvLCtB7pLstHXp-aUO71VOVIgm9WjDzPOvEkapQCdwA5Is982EtXs489s7VOFpkL1l7MvWqaXTg0hSloPs"
                                    alt="Dynamic jump"
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-primary/90 via-primary/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex flex-col justify-end p-8">
                                    <span className="text-xs text-white font-bold uppercase tracking-widest mb-2">Performance</span>
                                    <h4 className="text-2xl font-headline font-bold text-white">Fluidity Study #09</h4>
                                </div>
                            </div>
                            <div className="group relative rounded-2xl overflow-hidden aspect-square shadow-md reveal-on-scroll" style={{ transitionDelay: '100ms' }}>
                                <img
                                    src="https://lh3.googleusercontent.com/aida-public/AB6AXuCv-Lto_n6ejFVFrYIee4vaOVTRelYO6954dH-S1LL8sk-Vnx5v3pUCdWOntYM4pdO1QPly2EcQXZgmHf7c4grPXa1fTqZjUU0DFmLMQL0NOGntcdKhpzrQVS_6nqjDZ8Ha-TpTT7H9K92mNI4-YiBY7wnlL__FqCNRpRgaKkpwCCDWXscAraLwx03L5-AsnF8o_nX-uZ0Vgcxo2GwRkOSikolKQwu7WB20s_vGvGCO5aPA7WKyaxRBQD1VbmnFztbo0dm6QnCnO8U"
                                    alt="Active pose"
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
                                />
                                <div className="absolute inset-0 bg-secondary/10 group-hover:bg-transparent transition-colors duration-500"></div>
                                <div className="absolute top-4 right-4"><span className="material-symbols-outlined text-white bg-primary p-3 rounded-full shadow-lg group-hover:rotate-12 transition-transform">bolt</span></div>
                            </div>
                            <div className="group relative rounded-2xl overflow-hidden aspect-square shadow-md reveal-on-scroll" style={{ transitionDelay: '200ms' }}>
                                <img
                                    src="/archive_ballet_leap.png"
                                    alt="Ballet leap capture"
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
                                />
                                <div className="absolute inset-0 bg-gradient-to-tr from-primary/10 to-transparent"></div>
                                <div className="absolute bottom-4 left-4"><span className="text-white font-bold text-xs bg-black/40 px-3 py-1 rounded-full backdrop-blur-sm">LEAP.STUDY</span></div>
                            </div>
                            <div className="group relative rounded-2xl overflow-hidden aspect-square shadow-md reveal-on-scroll" style={{ transitionDelay: '300ms' }}>
                                <img
                                    src="/archive_parkour_vault.png"
                                    alt="Parkour vault motion"
                                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000"
                                />
                                <div className="absolute inset-0 bg-gradient-to-bl from-secondary/10 to-transparent"></div>
                                <div className="absolute bottom-4 left-4"><span className="text-white font-bold text-xs bg-black/40 px-3 py-1 rounded-full backdrop-blur-sm">VAULT.KINETICS</span></div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Pricing Section */}
                <section id="pricing" className="py-24 md:py-32 px-6 md:px-12 bg-slate-50 scroll-mt-20 w-full">
                    <div className="w-full">
                        <div className="text-center mb-16 reveal-on-scroll">
                            <h2 className="text-5xl md:text-6xl font-headline font-black mb-6 text-slate-900">
                                Choose Your <span className="text-blue-600 italic">Kinetic</span> Edge
                            </h2>
                            <p className="text-slate-500 max-w-2xl mx-auto text-lg font-medium">
                                Scalable precision for every stage of your creative workflow. From solo experimentation to global production teams.
                            </p>
                        </div>

                        {/* Pricing Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                            {/* Starter / Free */}
                            <div className="bg-slate-100 rounded-[2rem] p-8 md:p-10 flex flex-col reveal-on-scroll border border-slate-200/50 hover:shadow-lg transition-shadow">
                                <span className="px-3 py-1 bg-slate-200 text-slate-500 text-[10px] font-bold uppercase tracking-widest rounded-full inline-block w-max mb-6">
                                    STARTER
                                </span>
                                <h3 className="text-4xl font-headline font-black mb-2 text-slate-900">Free</h3>
                                <p className="text-slate-500 text-sm mb-10 h-10">For hobbyists and curious motion designers.</p>
                                
                                <ul className="space-y-4 mb-10 flex-1">
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-emerald-600 bg-emerald-100 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">Single Export Format (MP4)</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-emerald-600 bg-emerald-100 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">Max 15s Recording</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-emerald-600 bg-emerald-100 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">1GB Cloud Storage</span>
                                    </li>
                                    <li className="flex items-center gap-3 opacity-50 mt-4">
                                        <span className="material-symbols-outlined text-slate-500 bg-slate-200 rounded-full p-0.5 text-[14px] font-bold">close</span> 
                                        <span className="text-slate-500 text-sm font-medium">Batch Processing</span>
                                    </li>
                                </ul>
                                <button className="w-full mt-auto py-4 bg-slate-200 hover:bg-slate-300 text-slate-700 font-bold rounded-2xl transition-colors active:scale-95 text-sm">
                                    Start Free
                                </button>
                            </div>

                            {/* Pro Professional */}
                            <div className="bg-white rounded-[2rem] p-8 md:p-10 flex flex-col shadow-2xl relative overflow-hidden transform md:-translate-y-4 border border-blue-100 z-10 reveal-on-scroll" style={{ transitionDelay: '100ms' }}>
                                <div className="absolute top-0 right-0 w-32 h-32 overflow-hidden pointer-events-none">
                                    <div className="absolute top-6 -right-8 bg-blue-600 text-white text-[9px] font-black uppercase tracking-widest py-1.5 px-10 rotate-45 transform text-center shadow-md">
                                        MOST POPULAR
                                    </div>
                                </div>
                                <span className="px-3 py-1 bg-purple-100 text-[#a855f7] text-[10px] font-bold uppercase tracking-widest rounded-full inline-block w-max mb-6">
                                    PRO PROFESSIONAL
                                </span>
                                <h3 className="text-[3.5rem] leading-none font-headline font-black mb-2 text-blue-600 flex items-baseline">
                                    $49 <span className="text-lg text-slate-400 font-medium ml-1 tracking-normal">/mo</span>
                                </h3>
                                <p className="text-slate-500 text-sm mb-10 h-10 pr-6">Advanced tools for serious animators and studios.</p>
                                
                                <ul className="space-y-5 mb-10 flex-1">
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-white bg-emerald-400 rounded-full p-0.5 text-[14px] font-bold shadow-sm">check</span> 
                                        <span className="text-slate-800 text-sm font-bold">All Export Formats (FBX, BVH, MP4)</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-white bg-emerald-400 rounded-full p-0.5 text-[14px] font-bold shadow-sm">check</span> 
                                        <span className="text-slate-800 text-sm font-bold">Max 10min Recording</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-white bg-emerald-400 rounded-full p-0.5 text-[14px] font-bold shadow-sm">check</span> 
                                        <span className="text-slate-800 text-sm font-bold">50GB High-Speed Cloud Storage</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-white bg-emerald-400 rounded-full p-0.5 text-[14px] font-bold shadow-sm">check</span> 
                                        <span className="text-slate-800 text-sm font-bold">Batch AI Processing</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-white bg-emerald-400 rounded-full p-0.5 text-[14px] font-bold shadow-sm">check</span> 
                                        <span className="text-slate-800 text-sm font-bold">Priority Render Queue</span>
                                    </li>
                                </ul>
                                <button className="w-full mt-auto py-4 bg-[#6366f1] hover:bg-indigo-600 text-white font-bold rounded-2xl transition-all shadow-[0_10px_20px_rgba(99,102,241,0.25)] hover:shadow-[0_15px_30px_rgba(99,102,241,0.35)] active:scale-95 text-sm">
                                    Go Pro Now
                                </button>
                            </div>

                            {/* Enterprise */}
                            <div className="bg-slate-100/80 rounded-[2rem] p-8 md:p-10 flex flex-col reveal-on-scroll border border-slate-200/50 hover:shadow-lg transition-shadow" style={{ transitionDelay: '200ms' }}>
                                <span className="px-3 py-1 bg-[#1e293b] text-white text-[10px] font-bold uppercase tracking-widest rounded-full inline-block w-max mb-6">
                                    ENTERPRISE
                                </span>
                                <h3 className="text-4xl font-headline font-black mb-2 text-slate-800">Custom</h3>
                                <p className="text-slate-500 text-sm mb-10 h-10 pr-2">Tailored solutions for large-scale production pipelines.</p>
                                
                                <ul className="space-y-4 mb-10 flex-1">
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-indigo-600 border border-indigo-600 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">Unlimited Recording & Storage</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-indigo-600 border border-indigo-600 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">Custom API Integrations</span>
                                    </li>
                                    <li className="flex items-center gap-3">
                                        <span className="material-symbols-outlined text-indigo-600 border border-indigo-600 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">Dedicated Account Manager</span>
                                    </li>
                                    <li className="flex items-center gap-3 flex-wrap">
                                        <span className="material-symbols-outlined text-indigo-600 border border-indigo-600 rounded-full p-0.5 text-[14px] font-bold">check</span> 
                                        <span className="text-slate-700 text-sm font-medium">On-Premise Deployment Options</span>
                                    </li>
                                </ul>
                                <button className="w-full mt-auto py-4 bg-[#27272a] hover:bg-black text-white font-bold rounded-2xl transition-colors active:scale-95 shadow-md text-sm">
                                    Contact Sales
                                </button>
                            </div>
                        </div>

                        {/* Feature Cards Bottom Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-6xl mx-auto mt-16 pb-10">
                            {/* Real-time Stream */}
                            <div className="md:col-span-2 bg-[#e2e8f0] rounded-[2rem] flex items-center overflow-hidden reveal-on-scroll relative group">
                                <div className="w-[55%] p-8 z-10 relative">
                                    <h4 className="text-2xl font-headline font-bold text-slate-900 mb-2">Real-time Stream</h4>
                                    <p className="text-slate-500 text-sm leading-relaxed">Low-latency motion capture direct to your engine.</p>
                                </div>
                                <div className="absolute right-0 top-0 bottom-0 w-[55%] mix-blend-overlay opacity-60 group-hover:opacity-80 transition-opacity">
                                    <img src="https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000&auto=format&fit=crop" alt="Circuit board processing" className="w-full h-full object-cover" />
                                    <div className="absolute inset-0 bg-gradient-to-r from-[#e2e8f0] via-transparent to-transparent"></div>
                                </div>
                            </div>

                            {/* Infinite Sync */}
                            <div className="md:col-span-1 bg-[#e9d5ff] rounded-[2rem] p-8 flex flex-col justify-end reveal-on-scroll hover:-translate-y-1 transition-transform" style={{ transitionDelay: '100ms' }}>
                                <span className="material-symbols-outlined text-purple-700 mb-auto pb-10 text-[2rem]">sync_saved_locally</span>
                                <h4 className="text-xl font-headline font-bold text-purple-900 mb-2">Infinite Sync</h4>
                                <p className="text-purple-800/80 text-sm">Access your poses across any device, anywhere.</p>
                            </div>

                            {/* 99% Precision */}
                            <div className="md:col-span-1 bg-[#6ee7b7] rounded-[2rem] p-8 flex flex-col justify-end reveal-on-scroll hover:-translate-y-1 transition-transform" style={{ transitionDelay: '200ms' }}>
                                <span className="material-symbols-outlined text-emerald-900 mb-auto pb-10 text-[2rem]">precision_manufacturing</span>
                                <h4 className="text-xl font-headline font-bold text-emerald-950 mb-2">99% Precision</h4>
                                <p className="text-emerald-900/80 text-sm">Sub-millimeter tracking for professional cinematic results.</p>
                            </div>
                        </div>

                    </div>
                </section>

                {/* CTA Section */}
                <section className="py-24 md:py-32 px-4 md:px-8 overflow-hidden bg-white">
                    <div className="w-full max-w-6xl mx-auto rounded-[2rem] md:rounded-[3rem] signature-gradient p-10 md:p-20 text-center relative shadow-[0_40px_100px_rgba(61,90,254,0.3)] overflow-hidden reveal-on-scroll">

                        <h2 className="text-6xl md:text-7xl font-headline font-bold text-white mb-8 relative z-10 tracking-tighter">READY TO MOVE?</h2>
                        <button className="bg-white text-primary px-12 py-5 rounded-2xl font-bold text-xl hover:scale-105 transition-all shadow-2xl hover:shadow-white/20 active:scale-95 relative z-10">Start Your Project</button>
                    </div>
                </section>
                {/* Footer */}
                <footer className="w-full py-10 px-6 md:px-12 bg-slate-50 border-t border-slate-200/50 shrink-0">
                    <div className="w-full flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="text-left">
                            <div className="text-lg font-bold text-slate-800 font-headline mb-1 italic">Pose Animator</div>
                            <p className="font-body text-xs text-slate-500">© 2024 Pose Animator. Built with Kinetic Precision.</p>
                        </div>
                        <div className="flex gap-6 text-sm text-slate-400 font-medium">
                            <a href="#" className="hover:text-slate-600 transition-colors border-b border-transparent hover:border-slate-300 pb-0.5">Privacy Policy</a>
                            <a href="#" className="hover:text-slate-600 transition-colors border-b border-transparent hover:border-slate-300 pb-0.5">Terms of Service</a>
                            <a href="#" className="hover:text-slate-600 transition-colors border-b border-transparent hover:border-slate-300 pb-0.5">Support</a>
                            <a href="#" className="hover:text-slate-600 transition-colors border-b border-transparent hover:border-slate-300 pb-0.5">API Documentation</a>
                        </div>
                    </div>
                </footer>
            </main>
        </div>
    );
};

export default LandingPage;
