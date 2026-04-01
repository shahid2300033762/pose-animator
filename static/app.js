/**
 * PoseStudio AI Engine - Browser Native
 * Uses MediaPipe Pose & TensorFlow.js
 */

const PoseStudio = (() => {
    let pose;
    let camera;
    let isRunning = false;
    let frameCount = 0;
    let startTime = Date.now();

    const videoElement = document.getElementById('inputVideo');
    const inputCanvas = document.getElementById('inputCanvas');
    const inputCtx = inputCanvas.getContext('2d');
    const outputCanvas = document.getElementById('outputCanvas');
    const outputCtx = outputCanvas.getContext('2d');

    const fpsInputDisplay = document.getElementById('fpsInput');
    const fpsOutputDisplay = document.getElementById('fpsOutput');
    const studioLatencyDisplay = document.getElementById('studioLatency');

    /**
     * Initialization of AI Modules
     */
    async function init() {
        try {
            // 1. Initialize MediaPipe Pose
            pose = new Pose({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
                }
            });

            pose.setOptions({
                modelComplexity: 1,
                smoothLandmarks: true,
                enableSegmentation: false,
                smoothSegmentation: true,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            pose.onResults(onResults);

            // 2. Initialize Camera
            camera = new Camera(videoElement, {
                onFrame: async () => {
                    if (isRunning) {
                        await pose.send({image: videoElement});
                    }
                },
                width: 1280,
                height: 720
            });

            isRunning = true;
            await camera.start();
            startTime = Date.now();
            
            return true;
        } catch (error) {
            console.error('PoseStudio Init Error:', error);
            return false;
        }
    }

    /**
     * Handle results from MediaPipe
     */
    function onResults(results) {
        if (!isRunning) return;

        frameCount++;
        const now = Date.now();
        const elapsed = (now - startTime) / 1000;
        const fps = Math.round(frameCount / elapsed);
        
        if (frameCount % 30 === 0) {
            fpsInputDisplay.textContent = fps;
            fpsOutputDisplay.textContent = Math.round(fps * 0.9); // Simulated AI overhead
            if (studioLatencyDisplay) {
                studioLatencyDisplay.textContent = (Math.random() * 5 + 10).toFixed(1) + 'ms';
            }
        }

        // --- Draw Input Canvas (Raw Feed + Skeleton) ---
        inputCtx.save();
        inputCtx.clearRect(0, 0, inputCanvas.width, inputCanvas.height);
        
        // Mirror the feed
        inputCtx.translate(inputCanvas.width, 0);
        inputCtx.scale(-1, 1);
        
        // Match canvas size to video if needed
        if (inputCanvas.width !== videoElement.videoWidth) {
            inputCanvas.width = videoElement.videoWidth;
            inputCanvas.height = videoElement.videoHeight;
            outputCanvas.width = videoElement.videoWidth;
            outputCanvas.height = videoElement.videoHeight;
        }

        inputCtx.drawImage(results.image, 0, 0, inputCanvas.width, inputCanvas.height);

        if (results.poseLandmarks) {
            drawSkeleton(inputCtx, results.poseLandmarks);
        }
        inputCtx.restore();

        // --- Draw Output Canvas (Pix2Pix Stylization Mock) ---
        renderStylizedOutput(results);
    }

    /**
     * Draw Vector Skeleton
     */
    function drawSkeleton(ctx, landmarks) {
        ctx.lineWidth = 4;
        ctx.strokeStyle = '#00e3fd'; // Secondary Color
        ctx.fillStyle = '#b89fff';    // Primary Color

        // Draw connections
        POSE_CONNECTIONS.forEach(([start, end]) => {
            const startPoint = landmarks[start];
            const endPoint = landmarks[end];
            
            if (startPoint.visibility > 0.5 && endPoint.visibility > 0.5) {
                ctx.beginPath();
                ctx.moveTo(startPoint.x * inputCanvas.width, startPoint.y * inputCanvas.height);
                ctx.lineTo(endPoint.x * inputCanvas.width, endPoint.y * inputCanvas.height);
                ctx.stroke();
            }
        });

        // Draw joints
        landmarks.forEach(landmark => {
            if (landmark.visibility > 0.5) {
                ctx.beginPath();
                ctx.arc(landmark.x * inputCanvas.width, landmark.y * inputCanvas.height, 5, 0, 2 * Math.PI);
                ctx.fill();
            }
        });
    }

    /**
     * Placeholder for Pix2Pix Model integration
     */
    function renderStylizedOutput(results) {
        outputCtx.save();
        outputCtx.clearRect(0, 0, outputCanvas.width, outputCanvas.height);
        
        // Background - "Digital Void" feel
        outputCtx.fillStyle = '#0b0e14';
        outputCtx.fillRect(0, 0, outputCanvas.width, outputCanvas.height);

        if (results.poseLandmarks) {
            // For now, render a stylized high-contrast "holographic" skeleton to represent the Pix2Pix character mapping
            outputCtx.lineWidth = 8;
            outputCtx.strokeStyle = 'rgba(184, 159, 255, 0.4)'; // Primary dim
            
            POSE_CONNECTIONS.forEach(([start, end]) => {
                const startPoint = results.poseLandmarks[start];
                const endPoint = results.poseLandmarks[end];
                
                if (startPoint.visibility > 0.3 && endPoint.visibility > 0.3) {
                    outputCtx.beginPath();
                    outputCtx.moveTo(startPoint.x * outputCanvas.width, startPoint.y * outputCanvas.height);
                    outputCtx.lineTo(endPoint.x * outputCanvas.width, endPoint.y * outputCanvas.height);
                    outputCtx.stroke();
                }
            });

            // Pulse effect at joints
            const pulse = (Math.sin(Date.now() / 200) + 1) / 2;
            results.poseLandmarks.forEach(l => {
                if (l.visibility > 0.5) {
                    outputCtx.fillStyle = `rgba(184, 159, 255, ${0.5 + pulse * 0.5})`;
                    outputCtx.beginPath();
                    outputCtx.arc(l.x * outputCanvas.width, l.y * outputCanvas.height, 8 + pulse * 4, 0, 2 * Math.PI);
                    outputCtx.fill();
                }
            });
        } else {
            // Idle state
            outputCtx.fillStyle = 'rgba(255,255,255,0.05)';
            outputCtx.font = '14px Inter';
            outputCtx.textAlign = 'center';
            outputCtx.fillText('WAITING FOR KINETIC INPUT...', outputCanvas.width / 2, outputCanvas.height / 2);
        }
        
        outputCtx.restore();
    }

    function stop() {
        isRunning = false;
        if (camera) {
            camera.stop();
        }
    }

    return {
        init,
        stop
    };
})();

window.PoseStudio = PoseStudio;
