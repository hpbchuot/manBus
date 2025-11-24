CREATE EXTENSION postgis;
CREATE EXTENSION pgcrypto;

-- Authentication and blacklist tokens
DROP TABLE IF EXISTS BlacklistTokens CASCADE;
CREATE TABLE BlacklistTokens (
    id SERIAL PRIMARY KEY,
    token VARCHAR(500) UNIQUE NOT NULL,
    blacklisted_on TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Predefined roles
DROP TABLE IF EXISTS Roles CASCADE;
CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users table
DROP TABLE IF EXISTS Users CASCADE;
CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(11) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    registered_on TIMESTAMP NOT NULL DEFAULT NOW(),
    admin BOOLEAN NOT NULL DEFAULT FALSE,
    public_id VARCHAR(100) UNIQUE,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(100),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Many-to-many relationship between users and roles
DROP TABLE IF EXISTS UserRoles CASCADE;
CREATE TABLE UserRoles (
    user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES Roles(role_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- Routes table
DROP TABLE IF EXISTS Routes CASCADE;
CREATE TABLE Routes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    route_geom GEOMETRY(LINESTRING, 4326),
    current_segment INT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Bus stops table
DROP TABLE IF EXISTS Stops CASCADE;
CREATE TABLE Stops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL
);

-- Junction table for routes and stops
DROP TABLE IF EXISTS RouteStops CASCADE;
CREATE TABLE RouteStops (
    route_id INT NOT NULL REFERENCES Routes(id) ON DELETE CASCADE,
    stop_id INT NOT NULL REFERENCES Stops(id) ON DELETE CASCADE,
    stop_sequence INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (route_id, stop_id)
);

-- Buses table
DROP TABLE IF EXISTS Buses CASCADE;
CREATE TABLE Buses (
    bus_id SERIAL PRIMARY KEY,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    model VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Active',
    route_id INT NOT NULL REFERENCES Routes(id),
    current_location GEOMETRY(POINT, 4326),
    FOREIGN KEY (route_id) REFERENCES Routes(id) ON DELETE RESTRICT
);

-- Spatial index for bus current location
DROP INDEX IF EXISTS idx_bus_current_location CASCADE;
CREATE INDEX idx_bus_current_location ON Buses USING GIST(current_location);

-- Spatial index for route 
DROP INDEX IF EXISTS idx_route_geom CASCADE;
CREATE INDEX idx_route_geom ON Routes USING GIST(route_geom);

-- Spatial index for stop locations
DROP INDEX IF EXISTS idx_stop_location CASCADE;
CREATE INDEX idx_stop_location ON Stops USING GIST(location);

-- Drivers table (one-to-one with Users)
DROP TABLE IF EXISTS Drivers CASCADE;
CREATE TABLE Drivers (
    id SERIAL PRIMARY KEY,
    license_number VARCHAR(100) UNIQUE NOT NULL,
    bus_id INT NOT NULL REFERENCES Buses(bus_id),
    user_id INT NOT NULL UNIQUE REFERENCES Users(id) ON DELETE CASCADE,
    status VARCHAR(10) NOT NULL DEFAULT 'Active',
    FOREIGN KEY (bus_id) REFERENCES Buses(bus_id) ON DELETE RESTRICT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
);

-- Notifications table (linked to users)
DROP TABLE IF EXISTS Notifications CASCADE;
CREATE TABLE Notifications (
    id SERIAL PRIMARY KEY,
    message VARCHAR(255) NOT NULL,
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    type VARCHAR(50),
    link VARCHAR(255),
    user_id INT REFERENCES Users(id) ON DELETE CASCADE
);

-- Feedback table
DROP TABLE IF EXISTS Feedback CASCADE;
CREATE TABLE Feedback (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    bus_id INT NOT NULL REFERENCES Buses(bus_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES Users(id) ON DELETE CASCADE
);