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

db.connect((err) => {
  if (err) {
    console.error('Connection failed:', err.message);
    process.exit(1);
  }

  const query = 'ALTER TABLE users ADD total_frames BIGINT DEFAULT 0';
  db.query(query, (err, res) => {
    if (err) {
      if (err.errno === 1060 || err.code === 'ER_DUP_COLUMN_NAME') {
        console.log('Column total_frames already exists.');
      } else {
        console.error('Migration failed:', err.message);
      }
    } else {
      console.log('Column total_frames added successfully.');
    }
    db.end();
    process.exit(0);
  });
});
