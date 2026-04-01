-- Create the Database
CREATE DATABASE IF NOT EXISTS pose_studio_db;

-- Use the Database
USE pose_studio_db;

-- Create the Users Table
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OPTIONAL: Insert a Sample User (Remove in production)
-- INSERT INTO users (name, email, password) VALUES ('Test User', 'test@example.com', 'testpass');
