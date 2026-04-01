import React, { useEffect, useRef, useState } from 'react';
import API_BASE from '../config.js';

// Access MediaPipe from global window object (loaded via CDN in index.html)
const Pose = window.Pose;
const POSE_CONNECTIONS = window.POSE_CONNECTIONS;
const Camera = window.Camera;

const StudioPage = ({ onBack, onHome, user }) => {
    const videoRef = useRef(null);
    const inputCanvasRef = useRef(null);
    const outputCanvasRef = useRef(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isAnimating, setIsAnimating] = useState(true);
    const [frameCount, setFrameCount] = useState(0);
    const lastSyncedFrameRef = useRef(0);
    const [fps, setFps] = useState(60);
    const [latency, setLatency] = useState(12);
    const cameraRef = useRef(null);

    useEffect(() => {
        const pose = new Pose({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });

        pose.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        pose.onResults((results) => {
            if (!results.image) return;

            const inputCanvas = inputCanvasRef.current;
            const outputCanvas = outputCanvasRef.current;
            if (!inputCanvas || !outputCanvas) return;

            const inputCtx = inputCanvas.getContext('2d');
            const outputCtx = outputCanvas.getContext('2d');

            // --- 1. Draw Input Feed (Mirror + Skeleton) ---
            inputCtx.save();
            inputCtx.clearRect(0, 0, inputCanvas.width, inputCanvas.height);
            inputCtx.translate(inputCanvas.width, 0);
            inputCtx.scale(-1, 1);
            inputCtx.drawImage(results.image, 0, 0, inputCanvas.width, inputCanvas.height);

            if (results.poseLandmarks) {
                drawSkeleton(inputCtx, results.poseLandmarks, inputCanvas.width, inputCanvas.height);
            }
            inputCtx.restore();

            // --- 2. Draw Stylized Output ---
            renderOutput(outputCtx, results.poseLandmarks, outputCanvas.width, outputCanvas.height);

            // Update Stats
            setFrameCount(prev => prev + 1);
            if (Math.random() > 0.9) {
                setFps(Math.round(55 + Math.random() * 10));
                setLatency(Math.round(10 + Math.random() * 5));
            }
        });

        if (videoRef.current) {
            cameraRef.current = new Camera(videoRef.current, {
                onFrame: async () => {
                    await pose.send({ image: videoRef.current });
                },
                width: 640,
                height: 360
            });
            if (isAnimating) {
                cameraRef.current.start();
            }
        }

        return () => {
            if (cameraRef.current) {
                cameraRef.current.stop();
                cameraRef.current = null;
            }
            pose.close();
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        if (cameraRef.current) {
            if (isAnimating) {
                cameraRef.current.start();
            } else {
                cameraRef.current.stop();
            }
        }
    }, [isAnimating]);

    // Statistics Sync: Push frameCount delta to backend
    useEffect(() => {
        const syncFrames = async () => {
            const delta = frameCount - lastSyncedFrameRef.current;
            if (delta > 0 && user?.id) {
                try {
                    await fetch(`${API_BASE}/api/stats`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ userId: user.id, delta })
                    });
                    lastSyncedFrameRef.current = frameCount;
                    console.log(`Synced ${delta} frames for user ${user.id}`);
                } catch (err) {
                    console.error('Stats Sync Error:', err);
                }
            }
        };

        // Sync every 500 frames
        if (frameCount % 500 === 0 && frameCount !== 0) {
            syncFrames();
        }

        // Final sync on unmount
        return () => {
            syncFrames();
        };
    }, [frameCount, user?.id]);

    const drawSkeleton = (ctx, landmarks, width, height) => {
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#6a37d4'; // Secondary
        ctx.fillStyle = '#2444eb';    // Primary

        POSE_CONNECTIONS.forEach(([start, end]) => {
            const a = landmarks[start];
            const b = landmarks[end];
            if (a.visibility > 0.5 && b.visibility > 0.5) {
                ctx.beginPath();
                ctx.moveTo(a.x * width, a.y * height);
                ctx.lineTo(b.x * width, b.y * height);
                ctx.stroke();
            }
        });

        landmarks.forEach(l => {
            if (l.visibility > 0.5) {
                ctx.beginPath();
                ctx.arc(l.x * width, l.y * height, 4, 0, 2 * Math.PI);
                ctx.fill();
            }
        });
    };

    const renderOutput = (ctx, landmarks, width, height) => {
        ctx.save();
        ctx.fillStyle = '#1a1c1e'; // Dark Studio BG
        ctx.fillRect(0, 0, width, height);

        if (landmarks) {
            ctx.lineWidth = 6;
            ctx.strokeStyle = 'rgba(106, 55, 212, 0.4)';
            
            POSE_CONNECTIONS.forEach(([start, end]) => {
                const a = landmarks[start];
                const b = landmarks[end];
                if (a.visibility > 0.3 && b.visibility > 0.3) {
                    ctx.beginPath();
                    ctx.moveTo(a.x * width, a.y * height);
                    ctx.lineTo(b.x * width, b.y * height);
                    ctx.stroke();
                }
            });

            const pulse = (Math.sin(Date.now() / 200) + 1) / 2;
            landmarks.forEach(l => {
                if (l.visibility > 0.5) {
                    ctx.fillStyle = `rgba(36, 68, 235, ${0.4 + pulse * 0.4})`;
                    ctx.beginPath();
                    ctx.arc(l.x * width, l.y * height, 6 + pulse * 4, 0, 2 * Math.PI);
                    ctx.fill();
                }
            });
        }
        ctx.restore();
    };

    return (
        <div className="bg-surface h-screen overflow-hidden flex flex-col text-on-surface font-body selection:bg-primary/20 w-full">
            {/* Nav */}
            <nav className="w-full shrink-0 z-50 bg-white shadow-sm flex items-center justify-between px-6 md:px-12 py-4 font-headline tracking-tight border-b border-outline-variant/20">
                <div className="w-full flex justify-between items-center h-full">
                    <div className="flex items-center gap-4">
                        <span 
                            className="text-2xl font-black text-slate-900 italic font-headline tracking-tight cursor-pointer hover:opacity-80 transition-opacity" 
                            onClick={onHome}
                            title="Return to Homepage"
                        >
                            Pose Animator
                        </span>
                        <div className="h-5 w-px bg-slate-300 mx-2 hidden md:block"></div>
                        <button 
                            onClick={onHome}
                            className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-200/50 transition-all font-bold text-sm"
                        >
                            <span className="material-symbols-outlined text-[18px]">home</span>
                            Home
                        </button>
                    </div>
                    
                    <div className="hidden md:flex items-center gap-8 pl-8">
                        <a className="text-on-surface-variant hover:text-primary transition-colors font-medium cursor-pointer" onClick={onBack}>Dashboard</a>
                        <a className="text-primary font-bold border-b-2 border-primary pb-1" href="#">Project</a>
                        <a className="text-on-surface-variant hover:text-primary transition-colors font-medium" href="#">Timeline</a>
                        <a className="text-on-surface-variant hover:text-primary transition-colors font-medium" href="#">Export</a>
                    </div>
                    
                    <div className="flex items-center gap-6 ml-auto">
                    <button className="px-5 py-2 text-sm font-bold text-on-surface-variant hover:text-primary transition-colors">Render</button>
                    <button className="px-6 py-2.5 text-sm font-bold bg-primary text-white rounded-lg hover:shadow-lg transition-all active:scale-95">New Scene</button>
                    <div className="flex gap-4 ml-4">
                        <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary">notifications</span>
                        <span className="material-symbols-outlined text-on-surface-variant cursor-pointer hover:text-primary">account_circle</span>
                    </div>
                    </div>
                </div>
            </nav>

            <main className="flex-1 overflow-y-auto px-6 md:px-12 py-10 w-full scroll-smooth">
                <div className="flex flex-col w-full min-h-full pb-10">
                    {/* Header */}
                    <div className="flex flex-col md:flex-row justify-between md:items-end gap-6 mb-10 w-full shrink-0">

                    <div>
                        <h1 className="font-headline text-5xl font-bold tracking-tighter mb-3">Workspace Studio</h1>
                        <p className="text-on-surface-variant font-medium text-lg">Session: Kinetic_Sequence_04 // {fps} FPS // Live Link Active</p>
                    </div>
                    <div className="flex gap-4">
                        <div className="flex items-center gap-3 bg-surface-container-high px-5 py-2.5 rounded-2xl shadow-sm border border-outline-variant/10">
                            <span className={`material-symbols-outlined text-sm ${isAnimating ? 'text-primary animate-pulse' : 'text-amber-500'}`} style={{ fontVariationSettings: "'FILL' 1" }}>{isAnimating ? 'fiber_manual_record' : 'pause_circle'}</span>
                            <span className="font-label text-xs font-bold uppercase tracking-widest">{isAnimating ? 'Live Sync' : 'Paused'}</span>
                        </div>
                        <div className="flex items-center gap-3 bg-tertiary-container px-5 py-2.5 rounded-2xl shadow-sm border border-tertiary/10">
                            <span className="material-symbols-outlined text-tertiary text-sm">wifi</span>
                            <span className="font-label text-xs font-bold uppercase tracking-widest text-on-tertiary-container">Latency: {latency}ms</span>
                        </div>
                    </div>
                </div>

                {/* Workspace Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-10 w-full shrink-0">
                    {/* Live Feed */}
                    <div className="flex flex-col gap-4">

                        <div className="flex items-center justify-between px-2">
                            <div className="flex items-center gap-3">
                                <span className="material-symbols-outlined text-primary text-3xl">videocam</span>
                                <h2 className="font-headline text-2xl font-bold tracking-tight">Live Camera Feed</h2>
                            </div>
                            <div className="flex gap-3">
                                <button className="p-3 rounded-xl bg-surface-container hover:bg-surface-container-highest transition-all"><span className="material-symbols-outlined text-on-surface-variant">settings_input_component</span></button>
                                <button className="p-3 rounded-xl bg-surface-container hover:bg-surface-container-highest transition-all"><span className="material-symbols-outlined text-on-surface-variant">grid_view</span></button>
                            </div>
                        </div>
                        <div className="relative aspect-video rounded-3xl overflow-hidden bg-surface-container-highest shadow-2xl border border-outline-variant/30 group">
                            <video ref={videoRef} className="hidden" playsInline muted />
                            <canvas ref={inputCanvasRef} width="640" height="360" className="w-full h-full object-cover" />
                            <div className="absolute top-6 left-6 flex items-center gap-2 px-3 py-1 bg-black/40 backdrop-blur-md rounded-full border border-white/20">
                                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                                <span className="text-[10px] font-bold text-white uppercase tracking-widest">Source: FaceCam HD</span>
                            </div>
                            <div className="absolute bottom-6 left-6 right-6 flex justify-between items-center glass-panel p-4 rounded-2xl border border-white/20 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                <div className="flex gap-6">
                                    <button className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest hover:text-primary transition-colors"><span className="material-symbols-outlined text-sm">visibility</span> Skeleton</button>
                                    <button className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-on-surface/40"><span className="material-symbols-outlined text-sm">analytics</span> Markers</button>
                                </div>
                                <div className="text-[10px] font-bold text-primary uppercase bg-primary-container/30 px-3 py-1 rounded-full">Retargeting Active</div>
                            </div>
                        </div>
                    </div>

                    {/* Output */}
                    <div className="flex flex-col gap-4">
                        <div className="flex items-center justify-between px-2">

                            <div className="flex items-center gap-3">
                                <span className="material-symbols-outlined text-secondary text-3xl">animation</span>
                                <h2 className="font-headline text-2xl font-bold tracking-tight">Kinetic Output</h2>
                            </div>
                            <div className="flex gap-3">
                                <button className="p-3 rounded-xl bg-surface-container hover:bg-surface-container-highest transition-all"><span className="material-symbols-outlined text-on-surface-variant">texture</span></button>
                                <button className="p-3 rounded-xl bg-surface-container hover:bg-surface-container-highest transition-all"><span className="material-symbols-outlined text-on-surface-variant">fullscreen</span></button>
                            </div>
                        </div>
                        <div className="relative aspect-video rounded-3xl overflow-hidden bg-surface-dim shadow-2xl border border-outline-variant/30 group">
                            <canvas ref={outputCanvasRef} width="640" height="360" className="w-full h-full object-cover" />
                            <div className="absolute bottom-6 left-6 right-6 flex justify-between items-center glass-panel p-4 rounded-2xl border border-white/20 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                <div className="flex gap-6">
                                    <button className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest hover:text-secondary transition-colors"><span className="material-symbols-outlined text-sm">person_outline</span> Mesh: V8_Male</button>
                                    <button className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest hover:text-secondary transition-colors"><span className="material-symbols-outlined text-sm">layers</span> Env: Void</button>
                                </div>
                                <div className="text-[10px] font-bold text-secondary uppercase bg-secondary-container/30 px-3 py-1 rounded-full">Precision Engine v2</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Controls */}
                <div className="mt-8 mb-10 grid grid-cols-1 lg:grid-cols-12 gap-8 w-full shrink-0">
                    <div className="col-span-1 lg:col-span-8 bg-surface-container-low p-6 md:p-8 rounded-[2rem] flex flex-col xl:flex-row items-center justify-between border border-outline-variant/10 shadow-sm gap-8 relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent pointer-events-none"></div>
                        <div className="flex flex-wrap sm:flex-nowrap justify-center sm:justify-start gap-8 sm:gap-12 w-full xl:w-auto relative z-10">
                            <div className="flex flex-col items-center sm:items-start text-center sm:text-left">
                                <span className="text-[10px] uppercase tracking-widest font-bold text-on-surface-variant mb-2">Frame</span>
                                <span className="font-headline text-4xl lg:text-5xl font-bold tracking-tight text-primary">{(frameCount % 9999).toLocaleString()}</span>
                            </div>
                            <div className="flex flex-col items-center sm:items-start text-center sm:text-left sm:border-l sm:border-outline-variant/30 sm:pl-8">
                                <span className="text-[10px] uppercase tracking-widest font-bold text-on-surface-variant mb-2">Delta (XYZ)</span>
                                <span className="font-headline text-xl lg:text-2xl text-secondary font-medium tabular-nums mt-auto pb-1">12.4, -4.2, 0.8</span>
                            </div>
                        </div>
                        <div className="flex flex-wrap sm:flex-nowrap items-center justify-center gap-4 relative z-10 w-full xl:w-auto">
                            <button 
                                onClick={() => setIsAnimating(!isAnimating)}
                                className={`h-14 px-6 shrink-0 rounded-2xl font-headline font-bold flex items-center justify-center gap-3 transition-all active:scale-95 border ${!isAnimating ? 'bg-amber-50 text-amber-600 border-amber-200 shadow-sm' : 'bg-surface-container-highest text-on-surface hover:bg-surface-dim border-outline-variant/20 shadow-md'}`}
                            >
                                <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>{isAnimating ? 'pause_circle' : 'play_circle'}</span>
                                {isAnimating ? 'Pause engine' : 'Resume engine'}
                            </button>
                            <button 
                                onClick={() => setIsRecording(!isRecording)}
                                className={`h-14 px-6 md:px-8 shrink-0 rounded-2xl font-headline font-bold flex items-center justify-center gap-3 shadow-xl transition-all active:scale-95 ${isRecording ? 'bg-error text-white shadow-error/20' : 'bg-primary text-white shadow-primary/20 hover:bg-primary/90'}`}
                            >
                                <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: "'FILL' 1" }}>{isRecording ? 'stop_circle' : 'fiber_manual_record'}</span>
                                {isRecording ? 'Stop' : 'Record'}
                            </button>
                            <button className="h-14 px-6 md:px-8 shrink-0 rounded-2xl bg-surface-container-highest text-on-surface font-headline border border-outline-variant/20 font-bold flex items-center justify-center gap-3 hover:bg-surface-dim transition-all shadow-md active:scale-95"><span className="material-symbols-outlined text-[20px]">cloud_upload</span> Sync</button>
                        </div>
                    </div>

                    <div className="col-span-1 lg:col-span-4 bg-surface-container-highest p-6 md:p-8 rounded-[2rem] border border-outline-variant/10 shadow-sm relative overflow-hidden flex flex-col h-full">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl rounded-full"></div>
                        <h3 className="font-headline font-bold text-xl mb-6 flex items-center gap-3">
                            <span className="material-symbols-outlined text-primary">history</span> Session Logs
                        </h3>
                        <div className="space-y-4 relative z-10">
                            <div className="flex justify-between items-center p-4 bg-white/60 backdrop-blur-sm rounded-2xl border border-outline-variant/10">
                                <span className="text-sm font-bold text-on-surface-variant">Calibrated T-Pose</span>
                                <span className="text-[10px] bg-tertiary-container text-on-tertiary-container px-3 py-1 rounded-full uppercase font-bold tracking-wider">Success</span>
                            </div>
                            <div className="flex justify-between items-center p-4 bg-white/60 backdrop-blur-sm rounded-2xl border border-outline-variant/10">
                                <span className="text-sm font-bold text-on-surface-variant">Rig Mapping Complete</span>
                                <span className="text-[10px] bg-tertiary-container text-on-tertiary-container px-3 py-1 rounded-full uppercase font-bold tracking-wider">Success</span>
                            </div>
                            <div className="flex justify-between items-center p-4 bg-white/20 rounded-2xl border border-outline-variant/5 opacity-50">
                                <span className="text-sm font-bold text-on-surface-variant italic">Lighting Bake</span>
                                <span className="text-[10px] bg-surface-container-high text-on-surface-variant px-3 py-1 rounded-full uppercase font-bold tracking-wider">Pending</span>
                            </div>
                        </div>
                        </div>
                    </div>
                </div>
            </main>

            <footer className="shrink-0 w-full bg-white/80 backdrop-blur-md border-t border-outline-variant/10 px-6 md:px-12 py-3 font-body text-[10px] uppercase tracking-[0.2em] font-bold text-on-surface-variant/60 z-[60]">
                <div className="w-full flex flex-col md:flex-row justify-between items-center gap-2 md:gap-0">
                    <div className="flex gap-4 md:gap-10">

                    <span className="flex items-center gap-2">System Status: <span className="text-emerald-500">Online</span></span>
                    <span className="flex items-center gap-2">Protocol: <span className="text-primary font-bold tracking-normal uppercase">Livelink v2</span></span>
                    </div>
                    <div>© 2024 PoseStudio Kinetic Engine</div>
                </div>
            </footer>
        </div>
    );
};

export default StudioPage;
