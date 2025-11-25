-- ENUM Types for the manBus database
-- Run this file BEFORE tables.sql to create the types

CREATE TYPE roles AS ENUM (
    'Admin',
    'Driver',
    'User'
);

CREATE TYPE bus_status AS ENUM (
    'Active',
    'Inactive',
    'Maintenance'
);

CREATE TYPE driver_status AS ENUM (
    'Active',
    'Inactive',
    'On Leave'
);