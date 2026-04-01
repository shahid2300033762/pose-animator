import express from 'express';
import mysql from 'mysql2';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Database Connection
let connectionConfig = {
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '3306'),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: { rejectUnauthorized: false }
};

if (process.env.DATABASE_URL) {
  try {
    const parsedUrl = new URL(process.env.DATABASE_URL);
    connectionConfig = {
      host: parsedUrl.hostname,
      port: parsedUrl.port ? parseInt(parsedUrl.port) : 3306,
      user: parsedUrl.username,
      password: parsedUrl.password,
      database: parsedUrl.pathname.replace(/^\//, ''),
      ssl: { rejectUnauthorized: false }
    };
  } catch (err) {
    console.warn('Could not parse DATABASE_URL, falling back to individual variables');
  }
}

const db = mysql.createConnection(connectionConfig);

db.connect((err) => {
  if (err) {
    console.error('MySQL Connection Error (Full):', err);
    return;
  }
  console.log('Connected to MySQL Database: ' + process.env.DB_NAME);

  // Migration: Ensure total_frames column exists
  const checkQuery = `
    SELECT count(*) AS col_exists
    FROM information_schema.columns
    WHERE table_schema = ? AND table_name = 'users' AND column_name = 'total_frames'
  `;
  db.query(checkQuery, [process.env.DB_NAME], (checkErr, results) => {
    if (checkErr) {
      console.error('Migration Check Error:', checkErr.message);
      return;
    }
    if (results[0].col_exists === 0) {
      db.query('ALTER TABLE users ADD COLUMN total_frames BIGINT DEFAULT 0', (addErr) => {
        if (addErr) console.error('Migration Error:', addErr.message);
        else console.log('Migration: total_frames column added.');
      });
    } else {
      console.log('Migration: total_frames column already exists.');
    }
  });
});

// Login
app.post('/api/login', (req, res) => {
  const { email, password } = req.body;
  const query = 'SELECT * FROM users WHERE email = ? AND password = ?';
  db.query(query, [email, password], (err, results) => {
    if (err) return res.status(500).json({ message: 'Database Error', error: err });
    if (results.length > 0) {
      res.status(200).json({ message: 'Login Successful', user: results[0] });
    } else {
      res.status(401).json({ message: 'Invalid Credentials' });
    }
  });
});

// Register
app.post('/api/register', (req, res) => {
  const { name, email, password } = req.body;
  const query = 'INSERT INTO users (name, email, password, total_frames) VALUES (?, ?, ?, 0)';
  db.query(query, [name, email, password], (err, results) => {
    if (err) return res.status(500).json({ message: 'Registration Failed', error: err });
    res.status(201).json({
      message: 'User Registered Successfully',
      user: { id: results.insertId, name, email, total_frames: 0 }
    });
  });
});

// Stats: Get
app.get('/api/stats/:userId', (req, res) => {
  const { userId } = req.params;
  db.query('SELECT total_frames FROM users WHERE id = ?', [userId], (err, results) => {
    if (err) return res.status(500).json({ message: 'Stats Fetch Error', error: err });
    if (results.length > 0) {
      res.status(200).json({ total_frames: results[0].total_frames });
    } else {
      res.status(404).json({ message: 'User not found' });
    }
  });
});

// Stats: Increment
app.post('/api/stats/increment', (req, res) => {
  const { userId, delta } = req.body;
  if (!userId || !delta) return res.status(400).json({ message: 'Missing userId or delta' });
  db.query('UPDATE users SET total_frames = total_frames + ? WHERE id = ?', [delta, userId], (err) => {
    if (err) return res.status(500).json({ message: 'Stats Update Error', error: err });
    res.status(200).json({ message: 'Stats updated successfully' });
  });
});

// Projects
app.get('/api/projects', (req, res) => {
  const projects = [
    {
      id: 1,
      title: "Neo-Modern Flow",
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDSmbfqMADZArvfVOk09ObQKpn-Lmotv_4gZ1qWILGSq7zXUVqCs0p_d9RTj8avPMCFInY9-S0E9e0CrOTkk8u6aICgQ4kWbPnke5Jfhd9xbdK4ZBJMpR0-1WtrwPoUDKDckHb1dRMKWCsVA8w5w9hmBLVIP1jKRreSL2YEwVpmaKqg30MGUyTbe5DTmlRUxkOQ23LSRe8w86oTBD_x-vJrOMbr3ulBF3NRRYmNBst3YOnisSnq-PxSpWwua4H8jZxbPW4tjrovz18",
      youtubeLink: "https://youtu.be/lKScqfdcN_s?si=DdbhfybisGLEkcIy",
      tags: ["4K RAW", "60 FPS"]
    },
    {
      id: 2,
      title: "Kinetic Study 09",
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDNzJR4yj7Hb1jgCGEXH90EO5a0cHiiVHyJ5loxU_NiSRwAfzDUyu3VYMDZhXLW4SsmUX-kIgEjA_2VuqV96csEy28qC7hlFCxXUmLrPfw1nwyf9luOhYk84i0MOByqNauwevrogKkcfUo2uX2StkVInmcATrKgISxlc_njFPT84acWVSi14KjeGoK1yJ_NaIZs-NOqGAp8admeHiEEjnxXhI-ldGoDM4HuZ8Br4uyFNg42z9vW1M8wH4xL5Zi_mwiWrMk-aSLTKtE",
      youtubeLink: "https://youtube.com/shorts/_XFwdaIxIdE?si=635vXq4f80uTXYy-",
      tags: ["Skeletal", "Experimental"]
    }
  ];
  res.status(200).json(projects);
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
