import React, { useState, useEffect } from 'react';
import API_BASE from '../config.js';

const DashboardPage = ({ user, onNewProject, onOpenStudio, onHome }) => {
    const userName = user?.name || 'Creator';
    const [projects, setProjects] = useState([]);
    const [stats, setStats] = useState({ total_frames: 0 });

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch Projects
                const projectsResponse = await fetch(`${API_BASE}/api/projects`);
                const projectsData = await projectsResponse.json();
                setProjects(projectsData);

                // Fetch User Stats
                if (user?.id) {
                    const statsResponse = await fetch(`${API_BASE}/api/stats?userId=${user.id}`);
                    const statsData = await statsResponse.json();
                    setStats(statsData);
                }
            } catch (error) {
                console.error('Error fetching dashboard data:', error);
            }
        };
        fetchData();
    }, [user?.id]);

    const handleProjectClick = (url) => {
        if (url) {
            window.open(url, '_blank', 'noopener,noreferrer');
        }
    };
    
    return (
        <div className="bg-surface font-body text-on-surface antialiased h-screen overflow-hidden flex flex-col w-full">

            {/* TopAppBar */}
            <header className="shrink-0 w-full z-50 bg-slate-50/40 backdrop-blur-xl shadow-[0_20px_40px_rgba(44,47,49,0.06)] h-20 px-6 md:px-12">
                <div className="w-full flex justify-between items-center h-full">
                    <div className="flex items-center gap-4">
                        <div 
                            className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity" 
                            onClick={onHome}
                            title="Return to Homepage"
                        >
                            <span className="text-2xl font-black text-slate-900 italic font-headline tracking-tight">Pose Animator</span>
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
                    {/* Search */}
                    <div className="hidden md:flex items-center bg-white border border-slate-200 rounded-full px-4 py-2 w-96 shadow-sm">
                        <span className="material-symbols-outlined text-slate-400 mr-2">search</span>
                        <input type="text" placeholder="Search projects, renders..." className="bg-transparent border-none outline-none text-sm w-full text-slate-700 placeholder:text-slate-400" />
                    </div>
                    {/* User */}
                    <div className="flex items-center gap-6">
                        <div className="relative cursor-pointer">
                            <span className="material-symbols-outlined text-slate-600 hover:text-slate-900 transition-colors">notifications</span>
                            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-indigo-500 rounded-full border-2 border-white"></span>
                        </div>
                        <div className="flex items-center gap-3">
                            <span className="text-sm font-bold text-slate-700 hidden sm:block">{userName}</span>
                            <img src={`https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=e0e7ff&color=4f46e5`} alt="User" className="w-10 h-10 rounded-full cursor-pointer shadow-sm hover:shadow-md transition-shadow border-2 border-white" />
                        </div>
                    </div>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto bg-white/40 overflow-x-hidden w-full scroll-smooth">
                <div className="w-full py-10 px-6 md:px-12">

                    {/* Welcome & Quick Actions */}
                    <section className="flex flex-col md:flex-row justify-between items-end gap-8">
                        <div className="space-y-2">
                            <h1 className="text-5xl font-black font-headline tracking-tighter text-on-surface">
                                Welcome, <span className="text-primary">{userName.split(' ')[0]}</span>
                            </h1>
                            <p className="text-on-surface-variant text-lg max-w-md">
                                Capture, refine, and export human motion with millisecond precision.
                            </p>
                        </div>
                        <div className="flex gap-4">
                            <button onClick={onOpenStudio} className="flex items-center gap-3 bg-surface-container-highest px-8 py-5 rounded-xl font-bold text-on-surface-variant hover:bg-surface-dim transition-all group">
                                <span className="material-symbols-outlined text-secondary">folder_open</span>
                                Open Studio
                            </button>
                            <button onClick={onNewProject} className="flex items-center gap-3 kinetic-gradient px-8 py-5 rounded-xl font-bold text-white shadow-xl shadow-primary/30 transition-all scale-100 hover:scale-[1.02] active:scale-95 group">
                                <span className="material-symbols-outlined">add_circle</span>
                                New Project
                            </button>
                        </div>
                    </section>

                    {/* Main Bento Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                        {/* Motion Stats Column */}
                        <div className="md:col-span-4 space-y-8">
                            <div className="bg-surface-container-low p-8 rounded-xl space-y-6">
                                <h2 className="font-headline text-xl font-bold uppercase tracking-widest text-on-surface-variant">Performance</h2>
                                <div className="space-y-4">
                                    <div className="bg-surface-container-lowest p-5 rounded-lg border-l-4 border-primary shadow-sm">
                                        <p className="text-label-md text-on-surface-variant font-medium">Total Frames Captured</p>
                                        <h3 className="text-3xl font-black font-headline text-on-surface mt-1">{(stats.total_frames || 0).toLocaleString()}</h3>
                                    </div>
                                    <div className="bg-surface-container-lowest p-5 rounded-lg border-l-4 border-secondary shadow-sm">
                                        <p className="text-label-md text-on-surface-variant font-medium">Capture Sessions</p>
                                        <h3 className="text-3xl font-black font-headline text-on-surface mt-1">24 <span className="text-sm font-normal text-on-surface-variant">this week</span></h3>
                                    </div>
                                    <div className="bg-surface-container-lowest p-5 rounded-lg border-l-4 border-tertiary shadow-sm">
                                        <p className="text-label-md text-on-surface-variant font-medium">Storage Used</p>
                                        <h3 className="text-3xl font-black font-headline text-on-surface mt-1">1.2 <span className="text-sm font-normal text-on-surface-variant">GB</span></h3>
                                    </div>
                                </div>
                                {/* Mini Chart Visualization */}
                                <div className="pt-4 h-32 flex items-end justify-between gap-1">
                                    <div className="w-full bg-primary/20 rounded-t-sm h-[40%]"></div>
                                    <div className="w-full bg-primary/20 rounded-t-sm h-[60%]"></div>
                                    <div className="w-full bg-primary/20 rounded-t-sm h-[30%]"></div>
                                    <div className="w-full bg-primary/20 rounded-t-sm h-[80%]"></div>
                                    <div className="w-full bg-primary rounded-t-sm h-[100%] shadow-[0_0_15px_rgba(36,68,235,0.4)]"></div>
                                    <div className="w-full bg-primary/20 rounded-t-sm h-[50%]"></div>
                                    <div className="w-full bg-primary/20 rounded-t-sm h-[70%]"></div>
                                </div>
                            </div>
                            {/* Recent Activity Feed */}
                            <div className="space-y-4">
                                <h2 className="font-headline text-xl font-bold text-on-surface px-2">Activity Stream</h2>
                                <div className="space-y-2">
                                    <div className="flex items-center gap-4 p-4 bg-surface hover:bg-surface-container-high transition-colors rounded-lg group">
                                        <div className="w-10 h-10 rounded-full bg-tertiary-container flex items-center justify-center text-on-tertiary-container">
                                            <span className="material-symbols-outlined text-[18px]">check_circle</span>
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold">Export Complete</p>
                                            <p className="text-xs text-on-surface-variant">Dance_Routine_01.fbx</p>
                                        </div>
                                        <span className="ml-auto text-[10px] text-on-surface-variant font-bold uppercase tracking-tighter">2m ago</span>
                                    </div>
                                    <div className="flex items-center gap-4 p-4 bg-surface hover:bg-surface-container-high transition-colors rounded-lg group">
                                        <div className="w-10 h-10 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container">
                                            <span className="material-symbols-outlined text-[18px]">edit_note</span>
                                        </div>
                                        <div>
                                            <p className="text-sm font-bold">Pose Refined</p>
                                            <p className="text-xs text-on-surface-variant">Fight_Stance_V2</p>
                                        </div>
                                        <span className="ml-auto text-[10px] text-on-surface-variant font-bold uppercase tracking-tighter">1h ago</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {/* Main Workspace Column */}
                        <div className="md:col-span-8 space-y-8">
                            {/* Featured Carousel / Gallery */}
                            <div className="space-y-6">
                                <div className="flex justify-between items-center px-2">
                                    <h2 className="font-headline text-2xl font-bold tracking-tight">Recently Recorded</h2>
                                    <a className="text-primary font-bold text-sm hover:underline underline-offset-4 decoration-2" href="#">View Library</a>
                                </div>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                                    {projects.map((project) => (
                                        <div 
                                            key={project.id}
                                            className="group relative overflow-hidden bg-surface-container-lowest rounded-xl shadow-[0_20px_40px_rgba(44,47,49,0.06)] hover:shadow-xl transition-all border border-transparent hover:border-primary/10 cursor-pointer"
                                            onClick={() => handleProjectClick(project.youtubeLink)}
                                        >
                                            <div className="aspect-video relative overflow-hidden">
                                                <img className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" alt={project.title} src={project.image} />
                                                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                    <div className="w-14 h-14 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center transform scale-90 group-hover:scale-100 transition-transform">
                                                        <span className="material-symbols-outlined text-white text-4xl">play_arrow</span>
                                                    </div>
                                                </div>
                                                <div className="absolute top-4 right-4 bg-black/40 backdrop-blur-sm text-white px-2 py-1 rounded text-[10px] font-bold">
                                                    YOUTUBE
                                                </div>
                                            </div>
                                            <div className="p-5 flex justify-between items-start">
                                                <div>
                                                    <h4 className="font-bold text-on-surface">{project.title}</h4>
                                                    <div className="flex gap-2 mt-2">
                                                        {project.tags.map((tag, index) => (
                                                            <span key={index} className={`${index === 0 ? 'bg-tertiary-container text-on-tertiary-container' : 'bg-secondary-container text-on-secondary-container'} text-[10px] px-2 py-0.5 rounded-full font-bold uppercase`}>
                                                                {tag}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                                <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary">more_vert</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {/* Projects Table */}
                            <div className="bg-surface-container-low p-8 rounded-xl">
                                <h2 className="font-headline text-2xl font-bold mb-8">Archived Projects</h2>
                                <div className="space-y-4">
                                    <div className="grid grid-cols-12 items-center px-4 py-3 bg-surface-container-lowest rounded-lg hover:shadow-md transition-shadow">
                                        <div className="col-span-5 flex items-center gap-4">
                                            <div className="w-12 h-12 bg-surface-container rounded overflow-hidden">
                                                <img className="w-full h-full object-cover" alt="minimalist silhouette" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCu_15T-A28nQeDf_kOB7dHqEr16Pk-hAX_Bg5hAwgFQCl6gGiXPH6thMd1kBRRsQAbI-FgHnTOp8ZwEiAFgurwX87DAwFvFe-qZ9JBPIQ3mkK0UTlztt9L4TP_dtRRFXL4vDzmAXn2SjjAPcWBjX9CHgZ18JtZAV_DBzH049lsSd_USGujfaINWkdvCW271zLvMAUkYCE1bSDwWdRU3isjB0s1GelpiujOXzQOXhbmFPCSmY4hvP8-xYLgQg6vRfEWs5sH_3M8Ksw" />
                                            </div>
                                            <div>
                                                <p className="font-bold text-sm">Sprint_Analysis_Final</p>
                                                <p className="text-[10px] text-on-surface-variant uppercase font-bold tracking-widest">July 12, 2024</p>
                                            </div>
                                        </div>
                                        <div className="col-span-3">
                                            <span className="text-xs font-headline font-bold text-on-surface-variant">1,240 Nodes</span>
                                        </div>
                                        <div className="col-span-2">
                                            <span className="px-3 py-1 bg-tertiary/10 text-tertiary text-[10px] font-black rounded-full">OPTIMIZED</span>
                                        </div>
                                        <div className="col-span-2 text-right">
                                            <button className="text-primary material-symbols-outlined">download</button>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-12 items-center px-4 py-3 bg-surface-container-lowest rounded-lg hover:shadow-md transition-shadow">
                                        <div className="col-span-5 flex items-center gap-4">
                                            <div className="w-12 h-12 bg-surface-container rounded overflow-hidden">
                                                <img className="w-full h-full object-cover" alt="close up of lens" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCQGJ8MhMbYP8BiDZ13NAwM-794Kug0Uo9y5PEWl2nMskSm6mH4XLFaE79GaxxMZuMqwmq3Msuw1lolRlvXjgXFfa3SUaPcTIPrA4caAGIh0deSwGt_-FUbQ4r3EWn4KzM2xQ7gi2YaeZwbHCHk03sZoWkICmMcdyprSb1eBDGptBBMuRyaBxwCREecM2UOOzG6XICLHBlHXeLwO8RalH5AriDROxDLjs0C13koPhlHEW7MEI4fflOXn55pCbCMhtqQMwU4fsAnAyU" />
                                            </div>
                                            <div>
                                                <p className="font-bold text-sm">Martial_Arts_Mockup</p>
                                                <p className="text-[10px] text-on-surface-variant uppercase font-bold tracking-widest">July 08, 2024</p>
                                            </div>
                                        </div>
                                        <div className="col-span-3">
                                            <span className="text-xs font-headline font-bold text-on-surface-variant">8,900 Nodes</span>
                                        </div>
                                        <div className="col-span-2">
                                            <span className="px-3 py-1 bg-secondary/10 text-secondary text-[10px] font-black rounded-full">REFINING</span>
                                        </div>
                                        <div className="col-span-2 text-right">
                                            <button className="text-primary material-symbols-outlined">download</button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>


        </div>
    );
};

export default DashboardPage;
