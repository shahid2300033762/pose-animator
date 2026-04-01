# Pose Animator: Kinetic Studio ⚡

A real-time, high-fidelity human motion capture and retargeting studio suite built with **React, WebGL, and Google MediaPipe**. 

This application acts as the primary frontend interface for capturing 33-point 3D skeletal data from any standard webcam, rendering a stylized "Kinetic Skeleton," and logging animation sessions to a cloud database. It is designed to act as the extraction layer for a **Python-based Pix2Pix/GAN** or **Stable Diffusion ControlNet** backend to translate the skeleton output into fully-rendered characters.

---

## Features ✨

* **Real-Time Pose Detection**: Leverages Google's MediaPipe `pose` and `camera_utils` models running directly in the browser at ~60 FPS.
* **Production-Ready Bundling**: Specifically optimized with CDN scripts alongside Vite to permanently patch the known `@mediapipe` CommonJS module constructor bugs on deployment.
* **User Accounts & Dashboard**: Secure authentication system connected to a cloud database, with an accessible **Guest Mode** bypass for rapid testing.
* **Persistent Sessions**: Syncs animation session data (frames captured) to a Node.js API to track user metric data over time.

## Architecture 🏗️

The application uses an entirely decoupled full-stack architecture:

* **Frontend Environment**: React 18, Vite, Tailwind CSS
* **Computer Vision Layer**: `window.Pose` (MediaPipe via jsdelivr CDN)
* **Backend API Layer**: Node.js, Express.js, `mysql2` driver
* **Database Layer**: MySQL (Aiven Cloud)
* **Hosting Targets**: Vercel (Frontend) & Render.com (Backend Web Service)

---

## Getting Started Locally 💻

### 1. Database Setup
You will need a MySQL database. Create a file called `server/.env` and paste your connection string (supports direct parsing for Aiven and PlanetScale):

```env
DATABASE_URL="mysql://username:password@host:port/database_name?ssl-mode=REQUIRED"
```

### 2. Run the Backend Node Server
Open a terminal, navigate to the `server/` directory, install dependencies, and start Express.
```bash
cd server
npm install
npm start
```
*The server will gracefully automatically run on `http://localhost:10000` (or `process.env.PORT`).*

### 3. Run the Frontend React Studio
In a new terminal window at the project root folder, ensure the app connects to your new local backend. Edit `src/config.js`:
```javascript
// src/config.js
const API_BASE = 'http://localhost:10000';
export default API_BASE;
```

Then, start the Vite development server:
```bash
npm install
npm run dev
```
Visit `http://localhost:5173` in your browser.

---

## Production Deployment 🚀

1. **Deploy Backend to Render**: Create a new Web Service on Render, target the `server/` root directory, and set the Build Command to `npm install` and Start Command to `npm start`. Add your `DATABASE_URL` connection string to the Environment Variables.
2. **Deploy Frontend to Vercel**: Import the root repository to Vercel. In Vercel's Environment settings, create a new variable called `VITE_API_URL` and set its value to your newly deployed Render URL (e.g., `https://pose-animator-backend.onrender.com`). Vercel will automatically build the site using Vite's production protocols.

---

*Note: For the GAN integration, an additional Python server running `flask` or `fastapi` alongside PyTorch and Pix2Pix would take image buffers sent via `fetch` calls from `StudioPage.jsx`'s `onFrame` loop.*
