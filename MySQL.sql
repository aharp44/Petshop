CREATE DATABASE IF NOT EXISTS petplus;
USE petplus;

-- Users Table
CREATE TABLE IF NOT EXISTS Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    hash TEXT NOT NULL,
    cash FLOAT NOT NULL DEFAULT 10000.00
);

-- Transactions Table
CREATE TABLE IF NOT EXISTS Transactions (
    symbol VARCHAR(100),
    quantity INT,
    price FLOAT,
    userId INT,
    FOREIGN KEY (userId) REFERENCES Users(id),
    time DATETIME
);

-- Pets Table (from base schema)
CREATE TABLE IF NOT EXISTS Pets (
    symbol VARCHAR(100), 
    quantity INT, 
    price FLOAT, 
    userId INT, 
    FOREIGN KEY (userId) REFERENCES Users(id)
);

-- Shares Table
CREATE TABLE IF NOT EXISTS Shares (
    symbol VARCHAR(100), 
    quantity INT, 
    price FLOAT,
    userId INT,
    FOREIGN KEY (userId) REFERENCES Users(id)
);

-- Customers Table
CREATE TABLE IF NOT EXISTS Customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT
);

-- Employees Table
CREATE TABLE IF NOT EXISTS Employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50),
    hire_date DATE,
    salary DECIMAL(10,2)
);

-- Products Table
CREATE TABLE IF NOT EXISTS Products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0
);

-- Sales Table
CREATE TABLE IF NOT EXISTS Sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    employee_id INT,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(id),
    FOREIGN KEY (employee_id) REFERENCES Employees(id)
);

-- Sale_Items Table (intermediate)
CREATE TABLE IF NOT EXISTS Sale_Items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES Sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

-- Product_Categories Table
CREATE TABLE IF NOT EXISTS Product_Categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Product_Category_Relation Table (many-to-many)
CREATE TABLE IF NOT EXISTS Product_Category_Relation (
    product_id INT,
    category_id INT,
    PRIMARY KEY (product_id, category_id),
    FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Product_Categories(id) ON DELETE CASCADE
);