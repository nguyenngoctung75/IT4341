-- MySQL Schema for Convenience Store Location Optimization

-- Table: wards (formerly phuong)
CREATE TABLE wards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Table: premises (formerly mat_bang)
CREATE TABLE premises (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ward_id INT NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    is_rented BOOLEAN DEFAULT FALSE,
    frontage_width FLOAT COMMENT 'Width of frontage in meters',
    area_sqm FLOAT COMMENT 'Total area in square meters', -- Added based on original requirements
    has_parking BOOLEAN,
    annual_rent FLOAT COMMENT 'Annual rent cost (Million VND)',
    monthly_transport_cost FLOAT COMMENT 'Monthly transport cost (Million VND)',
    daily_traffic INT COMMENT 'Daily traffic volume',
    FOREIGN KEY (ward_id) REFERENCES wards(id) ON DELETE CASCADE
);

-- Table: location_factors (formerly yeu_to_khac)
CREATE TABLE location_factors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    premise_id INT UNIQUE,
    monthly_staff_cost FLOAT COMMENT 'Monthly staff cost (Million VND)',
    monthly_manager_cost FLOAT COMMENT 'Monthly manager cost (Million VND)',
    monthly_utility_cost FLOAT COMMENT 'Monthly utilities cost (Million VND)',
    legal_risk_score FLOAT COMMENT 'Legal risk score (0.0 - 1.0)',
    environment_desc VARCHAR(255) COMMENT 'Environment description',
    FOREIGN KEY (premise_id) REFERENCES premises(id) ON DELETE CASCADE
);

-- Table: demographics (formerly dan_cu)
CREATE TABLE demographics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    premise_id INT UNIQUE,
    population_density FLOAT COMMENT 'People per km2',
    avg_income FLOAT COMMENT 'Average income (Million VND/month)',
    avg_age INT COMMENT 'Average age',
    FOREIGN KEY (premise_id) REFERENCES premises(id) ON DELETE CASCADE
);

-- Table: existing_stores (formerly cua_hang)
CREATE TABLE existing_stores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ward_id INT NOT NULL,
    latitude DOUBLE NOT NULL,
    longitude DOUBLE NOT NULL,
    name VARCHAR(200),
    store_type ENUM('COMPETITOR', 'OWN_STORE') DEFAULT 'COMPETITOR',
    FOREIGN KEY (ward_id) REFERENCES wards(id) ON DELETE CASCADE
);

-- Table: distances (formerly khoang_cach_cua_hang)
CREATE TABLE distances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    premise_id INT,
    store_id INT,
    distance_meters FLOAT COMMENT 'Distance in meters',
    UNIQUE (premise_id, store_id),
    FOREIGN KEY (premise_id) REFERENCES premises(id) ON DELETE CASCADE,
    FOREIGN KEY (store_id) REFERENCES existing_stores(id) ON DELETE CASCADE
);
