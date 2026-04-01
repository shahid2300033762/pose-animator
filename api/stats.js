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
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const db = getPool();

  if (req.method === 'GET') {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ message: 'Missing userId' });
    try {
      const [rows] = await db.query('SELECT total_frames FROM users WHERE id = ?', [userId]);
      if (rows.length > 0) {
        res.status(200).json({ total_frames: rows[0].total_frames });
      } else {
        res.status(404).json({ message: 'User not found' });
      }
    } catch (err) {
      res.status(500).json({ message: 'Stats Fetch Error', error: err.message });
    }
  } else if (req.method === 'POST') {
    const { userId, delta } = req.body;
    if (!userId || !delta) return res.status(400).json({ message: 'Missing userId or delta' });
    try {
      await db.query('UPDATE users SET total_frames = total_frames + ? WHERE id = ?', [delta, userId]);
      res.status(200).json({ message: 'Stats updated successfully' });
    } catch (err) {
      res.status(500).json({ message: 'Stats Update Error', error: err.message });
    }
  } else {
    res.status(405).json({ message: 'Method not allowed' });
  }
}
