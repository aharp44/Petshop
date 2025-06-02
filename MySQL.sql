CREATE DATABASE IF NOT EXISTS petplus;
USE petplus;

CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    hash TEXT NOT NULL,
    cash FLOAT NOT NULL DEFAULT 10000.00
);

CREATE TABLE IF NOT EXISTS Transactions(
    symbol VARCHAR(100),
    quantity INT,
    price FLOAT,
    userId INT,
    FOREIGN KEY (userId) REFERENCES Users(id),
    time DATETIME
);

-- CREATE TABLE IF NOT EXISTS Pets(
-- 	symbol VARCHAR(100),
--     quantity INT,
--     price FLOAT,
--     userId INT,
--     FOREIGN KEY (userId) REFERENCES Users(id)
-- );

-- CREATE TABLE IF NOT EXISTS Shares(
-- 	symbol VARCHAR(100),
--     quantity INT,
--     price FLOAT,
--     userId INT,
--     FOREIGN KEY (userId) REFERENCES Users(id)
-- );


