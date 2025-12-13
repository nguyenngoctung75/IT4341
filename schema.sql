DROP DATABASE IF EXISTS convenience_store_db;
CREATE DATABASE convenience_store_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE convenience_store_db;

CREATE TABLE districts (
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE wards (
    id INT PRIMARY KEY,
    district_id INT,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE
);

CREATE TABLE ward_demographics (
    id INT PRIMARY KEY,
    ward_id INT,
    population INT,
    density FLOAT,
    FOREIGN KEY (ward_id) REFERENCES wards(id) ON DELETE CASCADE
);

CREATE TABLE opponent_stores (
    id INT PRIMARY KEY,
    district_id INT,
    ward_id INT,
    name VARCHAR(255),
    address TEXT,
    latitude DOUBLE,
    longitude DOUBLE,
    FOREIGN KEY (district_id) REFERENCES districts(id),
    FOREIGN KEY (ward_id) REFERENCES wards(id)
);

CREATE TABLE rental_shops (
    id INT PRIMARY KEY,
    ward_id INT,
    address TEXT,
    price FLOAT, -- Million VND/month
    area FLOAT, -- m2
    frontage FLOAT, -- m
    description TEXT,
    FOREIGN KEY (ward_id) REFERENCES wards(id) ON DELETE SET NULL
);

CREATE TABLE shop_opponent_distances (
    id INT PRIMARY KEY,
    shop_id INT,
    opponent_id INT,
    distance_km FLOAT,
    FOREIGN KEY (shop_id) REFERENCES rental_shops(id) ON DELETE CASCADE,
    FOREIGN KEY (opponent_id) REFERENCES opponent_stores(id) ON DELETE CASCADE
);

CREATE TABLE other_factors (
    id INT PRIMARY KEY,
    rental_shop_id INT,
    foot_traffic INT,
    employee_cost FLOAT,
    utilities_cost FLOAT,
    FOREIGN KEY (rental_shop_id) REFERENCES rental_shops(id) ON DELETE CASCADE
);
