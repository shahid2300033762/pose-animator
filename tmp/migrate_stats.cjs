const mysql = require('mysql2');
const dotenv = require('dotenv');
const path = require('path');
dotenv.config({ path: path.join(__dirname, '../server/.env') });

const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

const query = 'ALTER TABLE users ADD COLUMN total_frames BIGINT DEFAULT 0';

db.query(query, (err, res) => {
  if (err) {
    if (err.code === 'ER_DUP_COLUMN_NAME') {
      console.log('Column already exists');
    } else {
      console.error('Migration failed:', err);
    }
  } else {
    console.log('Column total_frames added successfully');
  }
  process.exit();
});
