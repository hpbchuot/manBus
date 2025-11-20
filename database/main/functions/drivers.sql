-- ============================================================================
-- DRIVERS.SQL - Driver Management Functions
-- ============================================================================
-- Description: Functions for managing drivers and bus assignments
-- Dependencies: Drivers, Buses, Users tables
-- ============================================================================

-- ============================================================================
-- DRIVER CREATION
-- ============================================================================

-- Function: fn_create_driver
-- Description: Creates a new driver record
-- Parameters:
--   p_user_id: User ID to associate with driver
--   p_license_number: Driver's license number (unique)
--   p_bus_id: Bus to assign to driver
-- Returns: INT - New driver ID
-- Usage: SELECT fn_create_driver(1, 'DL123456789', 1);
CREATE OR REPLACE FUNCTION fn_create_driver(
    p_user_id INT,
    p_license_number VARCHAR(100),
    p_bus_id INT
)
RETURNS INT AS $$
DECLARE
    new_driver_id INT;
    user_exists BOOLEAN;
    user_already_driver BOOLEAN;
    bus_exists BOOLEAN;
    bus_already_assigned BOOLEAN;
BEGIN
    -- Validate license number
    IF p_license_number IS NULL OR LENGTH(TRIM(p_license_number)) = 0 THEN
        RAISE EXCEPTION 'License number cannot be empty';
    END IF;

    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ) INTO user_exists;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Check if user is already a driver
    SELECT EXISTS(
        SELECT 1 FROM Drivers WHERE user_id = p_user_id
    ) INTO user_already_driver;

    IF user_already_driver THEN
        RAISE EXCEPTION 'User with ID % is already a driver', p_user_id;
    END IF;

    -- Check if bus exists
    SELECT EXISTS(
        SELECT 1 FROM Buses WHERE bus_id = p_bus_id
    ) INTO bus_exists;

    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Check if bus is already assigned to an active driver
    SELECT EXISTS(
        SELECT 1 FROM Drivers WHERE bus_id = p_bus_id AND status = 'Active'
    ) INTO bus_already_assigned;

    IF bus_already_assigned THEN
        RAISE NOTICE 'Warning: Bus % is already assigned to another active driver', p_bus_id;
    END IF;

    -- Insert driver
    INSERT INTO Drivers (user_id, license_number, bus_id, status)
    VALUES (p_user_id, UPPER(TRIM(p_license_number)), p_bus_id, 'Active')
    RETURNING id INTO new_driver_id;

    RAISE NOTICE 'Driver created successfully with ID: %', new_driver_id;
    RETURN new_driver_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'License number % already exists or user is already a driver', p_license_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BUS ASSIGNMENT
-- ============================================================================

-- Function: fn_assign_bus_to_driver
-- Description: Assigns or reassigns a bus to a driver
-- Parameters:
--   p_driver_id: Driver ID
--   p_bus_id: New bus ID to assign
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_assign_bus_to_driver(1, 2);
CREATE OR REPLACE FUNCTION fn_assign_bus_to_driver(
    p_driver_id INT,
    p_bus_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    driver_exists BOOLEAN;
    bus_exists BOOLEAN;
    bus_already_assigned BOOLEAN;
BEGIN
    -- Check if driver exists
    SELECT EXISTS(
        SELECT 1 FROM Drivers WHERE id = p_driver_id
    ) INTO driver_exists;

    IF NOT driver_exists THEN
        RAISE EXCEPTION 'Driver with ID % does not exist', p_driver_id;
    END IF;

    -- Check if bus exists
    SELECT EXISTS(
        SELECT 1 FROM Buses WHERE bus_id = p_bus_id
    ) INTO bus_exists;

    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Check if bus is already assigned to another active driver
    SELECT EXISTS(
        SELECT 1 FROM Drivers
        WHERE bus_id = p_bus_id
            AND id != p_driver_id
            AND status = 'Active'
    ) INTO bus_already_assigned;

    IF bus_already_assigned THEN
        RAISE NOTICE 'Warning: Bus % is already assigned to another active driver', p_bus_id;
    END IF;

    -- Assign bus to driver
    UPDATE Drivers
    SET bus_id = p_bus_id
    WHERE id = p_driver_id;

    RAISE NOTICE 'Bus % assigned to driver %', p_bus_id, p_driver_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DRIVER STATUS UPDATE
-- ============================================================================

-- Function: fn_set_driver_status
-- Description: Updates driver status
-- Parameters:
--   p_driver_id: Driver ID
--   p_new_status: New status (Active, Inactive, Suspended)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_set_driver_status(1, 'Inactive');
CREATE OR REPLACE FUNCTION fn_set_driver_status(
    p_driver_id INT,
    p_new_status VARCHAR(10)
)
RETURNS BOOLEAN AS $$
DECLARE
    driver_exists BOOLEAN;
BEGIN
    -- Validate status
    IF p_new_status NOT IN ('Active', 'Inactive', 'Suspended') THEN
        RAISE EXCEPTION 'Invalid status. Must be one of: Active, Inactive, Suspended';
    END IF;

    -- Check if driver exists
    SELECT EXISTS(
        SELECT 1 FROM Drivers WHERE id = p_driver_id
    ) INTO driver_exists;

    IF NOT driver_exists THEN
        RAISE EXCEPTION 'Driver with ID % does not exist', p_driver_id;
    END IF;

    -- Update status
    UPDATE Drivers
    SET status = p_new_status
    WHERE id = p_driver_id;

    RAISE NOTICE 'Driver % status updated to %', p_driver_id, p_new_status;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET DRIVER BY USER ID
-- ============================================================================

-- Function: fn_get_driver_by_user
-- Description: Retrieves driver information for a user
-- Parameters:
--   p_user_id: User ID
-- Returns: TABLE with driver information
-- Usage: SELECT * FROM fn_get_driver_by_user(1);
CREATE OR REPLACE FUNCTION fn_get_driver_by_user(p_user_id INT)
RETURNS TABLE (
    driver_id INT,
    license_number VARCHAR(100),
    status VARCHAR(10),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_id INT,
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS driver_id,
        d.license_number,
        d.status,
        d.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        b.route_id,
        r.name AS route_name
    FROM Drivers d
    INNER JOIN Buses b ON d.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE d.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ACTIVE DRIVERS
-- ============================================================================

-- Function: fn_get_active_drivers
-- Description: Returns all active drivers with their assignments
-- Returns: TABLE with driver information
-- Usage: SELECT * FROM fn_get_active_drivers();
CREATE OR REPLACE FUNCTION fn_get_active_drivers()
RETURNS TABLE (
    driver_id INT,
    driver_name VARCHAR(100),
    driver_email VARCHAR(255),
    driver_phone VARCHAR(11),
    license_number VARCHAR(100),
    status VARCHAR(10),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_id INT,
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS driver_id,
        u.name AS driver_name,
        u.email AS driver_email,
        u.phone AS driver_phone,
        d.license_number,
        d.status,
        d.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        b.route_id,
        r.name AS route_name
    FROM Drivers d
    INNER JOIN Users u ON d.user_id = u.id
    INNER JOIN Buses b ON d.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE d.status = 'Active'
        AND u.is_deleted = FALSE
    ORDER BY u.name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ALL DRIVERS
-- ============================================================================

-- Function: fn_get_all_drivers
-- Description: Returns all drivers regardless of status
-- Parameters:
--   p_include_deleted_users: Include drivers whose users are deleted (default FALSE)
-- Returns: TABLE with driver information
-- Usage: SELECT * FROM fn_get_all_drivers(FALSE);
CREATE OR REPLACE FUNCTION fn_get_all_drivers(p_include_deleted_users BOOLEAN DEFAULT FALSE)
RETURNS TABLE (
    driver_id INT,
    driver_name VARCHAR(100),
    driver_email VARCHAR(255),
    driver_phone VARCHAR(11),
    license_number VARCHAR(100),
    status VARCHAR(10),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_id INT,
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS driver_id,
        u.name AS driver_name,
        u.email AS driver_email,
        u.phone AS driver_phone,
        d.license_number,
        d.status,
        d.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        b.route_id,
        r.name AS route_name
    FROM Drivers d
    INNER JOIN Users u ON d.user_id = u.id
    INNER JOIN Buses b ON d.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE p_include_deleted_users OR u.is_deleted = FALSE
    ORDER BY u.name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET DRIVER BY BUS
-- ============================================================================

-- Function: fn_get_driver_by_bus
-- Description: Retrieves driver assigned to a specific bus
-- Parameters:
--   p_bus_id: Bus ID
-- Returns: TABLE with driver information
-- Usage: SELECT * FROM fn_get_driver_by_bus(1);
CREATE OR REPLACE FUNCTION fn_get_driver_by_bus(p_bus_id INT)
RETURNS TABLE (
    driver_id INT,
    driver_name VARCHAR(100),
    driver_email VARCHAR(255),
    driver_phone VARCHAR(11),
    license_number VARCHAR(100),
    status VARCHAR(10),
    user_id INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS driver_id,
        u.name AS driver_name,
        u.email AS driver_email,
        u.phone AS driver_phone,
        d.license_number,
        d.status,
        d.user_id
    FROM Drivers d
    INNER JOIN Users u ON d.user_id = u.id
    WHERE d.bus_id = p_bus_id
        AND u.is_deleted = FALSE
    ORDER BY d.status DESC; -- Active drivers first
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET DRIVERS ON ROUTE
-- ============================================================================

-- Function: fn_get_drivers_on_route
-- Description: Returns all drivers assigned to buses on a specific route
-- Parameters:
--   p_route_id: Route ID
-- Returns: TABLE with driver information
-- Usage: SELECT * FROM fn_get_drivers_on_route(1);
CREATE OR REPLACE FUNCTION fn_get_drivers_on_route(p_route_id INT)
RETURNS TABLE (
    driver_id INT,
    driver_name VARCHAR(100),
    driver_email VARCHAR(255),
    driver_phone VARCHAR(11),
    license_number VARCHAR(100),
    driver_status VARCHAR(10),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    bus_status VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id AS driver_id,
        u.name AS driver_name,
        u.email AS driver_email,
        u.phone AS driver_phone,
        d.license_number,
        d.status AS driver_status,
        d.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        b.status AS bus_status
    FROM Drivers d
    INNER JOIN Users u ON d.user_id = u.id
    INNER JOIN Buses b ON d.bus_id = b.bus_id
    WHERE b.route_id = p_route_id
        AND u.is_deleted = FALSE
    ORDER BY u.name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- UPDATE DRIVER LICENSE
-- ============================================================================

-- Function: fn_update_driver_license
-- Description: Updates driver's license number
-- Parameters:
--   p_driver_id: Driver ID
--   p_new_license: New license number
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_driver_license(1, 'DL987654321');
CREATE OR REPLACE FUNCTION fn_update_driver_license(
    p_driver_id INT,
    p_new_license VARCHAR(100)
)
RETURNS BOOLEAN AS $$
DECLARE
    driver_exists BOOLEAN;
BEGIN
    -- Validate license number
    IF p_new_license IS NULL OR LENGTH(TRIM(p_new_license)) = 0 THEN
        RAISE EXCEPTION 'License number cannot be empty';
    END IF;

    -- Check if driver exists
    SELECT EXISTS(
        SELECT 1 FROM Drivers WHERE id = p_driver_id
    ) INTO driver_exists;

    IF NOT driver_exists THEN
        RAISE EXCEPTION 'Driver with ID % does not exist', p_driver_id;
    END IF;

    -- Update license
    UPDATE Drivers
    SET license_number = UPPER(TRIM(p_new_license))
    WHERE id = p_driver_id;

    RAISE NOTICE 'Driver % license updated', p_driver_id;
    RETURN TRUE;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'License number % already exists', p_new_license;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CHECK IF USER IS DRIVER
-- ============================================================================

-- Function: fn_is_user_driver
-- Description: Checks if a user is a driver
-- Parameters:
--   p_user_id: User ID to check
-- Returns: BOOLEAN - TRUE if user is a driver
-- Usage: SELECT fn_is_user_driver(1);
CREATE OR REPLACE FUNCTION fn_is_user_driver(p_user_id INT)
RETURNS BOOLEAN AS $$
DECLARE
    is_driver BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM Drivers WHERE user_id = p_user_id
    ) INTO is_driver;

    RETURN is_driver;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET DRIVER COUNT
-- ============================================================================

-- Function: fn_get_driver_count
-- Description: Returns count of drivers by status
-- Parameters:
--   p_status: Status filter (NULL for all)
-- Returns: INT - Number of drivers
-- Usage: SELECT fn_get_driver_count('Active');
CREATE OR REPLACE FUNCTION fn_get_driver_count(p_status VARCHAR(10) DEFAULT NULL)
RETURNS INT AS $$
DECLARE
    driver_count INT;
BEGIN
    IF p_status IS NOT NULL THEN
        SELECT COUNT(*)
        INTO driver_count
        FROM Drivers d
        INNER JOIN Users u ON d.user_id = u.id
        WHERE d.status = p_status
            AND u.is_deleted = FALSE;
    ELSE
        SELECT COUNT(*)
        INTO driver_count
        FROM Drivers d
        INNER JOIN Users u ON d.user_id = u.id
        WHERE u.is_deleted = FALSE;
    END IF;

    RETURN driver_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- Create a driver:
-- SELECT fn_create_driver(1, 'DL123456789', 1);

-- Assign bus to driver:
-- SELECT fn_assign_bus_to_driver(1, 2);

-- Set driver status:
-- SELECT fn_set_driver_status(1, 'Inactive');

-- Get driver by user:
-- SELECT * FROM fn_get_driver_by_user(1);

-- Get active drivers:
-- SELECT * FROM fn_get_active_drivers();

-- Get all drivers:
-- SELECT * FROM fn_get_all_drivers(FALSE);

-- Get driver by bus:
-- SELECT * FROM fn_get_driver_by_bus(1);

-- Get drivers on route:
-- SELECT * FROM fn_get_drivers_on_route(1);

-- Update driver license:
-- SELECT fn_update_driver_license(1, 'DL987654321');

-- Check if user is driver:
-- SELECT fn_is_user_driver(1);

-- Get driver count:
-- SELECT fn_get_driver_count('Active');
-- SELECT fn_get_driver_count(NULL); -- All drivers
