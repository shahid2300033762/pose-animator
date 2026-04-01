import mysql from 'mysql2/promise';

let pool;
function getPool() {
  if (!pool) {
    pool = mysql.createPool({
      host: process.env.DB_HOST,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      waitForConnections: true,
      connectionLimit: 5
    });
  }
  return pool;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ message: 'Method not allowed' });

  const { name, email, password } = req.body;
  try {
    const db = getPool();
    const [result] = await db.query(
      'INSERT INTO users (name, email, password, total_frames) VALUES (?, ?, ?, 0)',
      [name, email, password]
    );
    res.status(201).json({
      message: 'User Registered Successfully',
      user: { id: result.insertId, name, email, total_frames: 0 }
    });
  } catch (err) {
    res.status(500).json({ message: 'Registration Failed', error: err.message });
  }
}
