CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL, 
    description TEXT, 
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE Permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL, 
    description TEXT, 
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE RolePermissions (
    role_id INT NOT NULL REFERENCES Roles(role_id) ON DELETE CASCADE,
    permission_id INT NOT NULL REFERENCES Permissions(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE UserRoles (
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    role_id INT NOT NULL REFERENCES Roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Bảng Users
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    isDeleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);


-- Bảng Drivers
CREATE TABLE Drivers (
    driver_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    bus_id INT,
    status ENUM('Active', 'On Leave', 'Inactive') DEFAULT 'Active',
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (bus_id) REFERENCES Buses(bus_id)
);

-- Bảng Buses
CREATE TABLE Buses (
    bus_id SERIAL PRIMARY KEY,
    plate_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100),
    model VARCHAR(50),
    status ENUM('Active', 'Maintenance', 'Inactive') DEFAULT 'Active',
    route_id INT,
    current_location GEOMETRY(Point, 4326),
    FOREIGN KEY (route_id) REFERENCES Routes(route_id)
);

-- Bảng Routes
CREATE TABLE Routes (
    route_id SERIAL PRIMARY KEY,
    route_name VARCHAR(255) NOT NULL,
    route_path GEOMETRY(LINESTRING, 4326) NOT NULL, 
    duration INT NOT NULL
);

CREATE TABLE BusStop (
    stop_id INT NOT NULL REFERENCES Stops(stop_id) ON DELETE CASCADE,
    route_id INT NOT NULL REFERENCES Routes(route_id) ON DELETE CASCADE,
    stopSequence INT DEFAULT 0,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (stop_id, route_id)
);

-- Bảng Stops
CREATE TABLE Stops (
    stop_id SERIAL PRIMARY KEY,
    stop_name VARCHAR(255) NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL
);



-- Bảng Notifications
CREATE TABLE Notifications (
    notification_id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    bus_id INT REFERENCES Buses(bus_id) ON DELETE CASCADE,
    type VARCHAR(50) DEFAULT 'General', -- Type of notification
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bảng Feedback
CREATE TABLE Feedback (
    feedback_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    plate_number VARCHAR(50) NOT NULL REFERENCES Buses(plate_number) ON DELETE CASCADE,
    status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);


