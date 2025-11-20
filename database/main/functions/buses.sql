-- ============================================================================
-- BUSES.SQL - Bus Fleet Management Functions
-- ============================================================================
-- Description: Functions for managing buses, tracking locations, and fleet operations
-- Dependencies: Buses, Routes tables, PostGIS extension, utilities.sql
-- ============================================================================

-- ============================================================================
-- BUS CREATION
-- ============================================================================

-- Function: fn_create_bus
-- Description: Creates a new bus with validation
-- Parameters:
--   p_plate_number: Vehicle plate number (unique)
--   p_name: Bus name/identifier
--   p_model: Bus model
--   p_route_id: Route assignment
--   p_status: Bus status (default 'Active')
-- Returns: INT - New bus ID
-- Usage: SELECT fn_create_bus('29A-12345', 'Bus 101', 1, 'Hyundai Universe', 'Active');
CREATE OR REPLACE FUNCTION fn_create_bus(
    p_plate_number VARCHAR(20),
    p_name VARCHAR(100),
    p_route_id INT,
    p_model VARCHAR(50) DEFAULT NULL,
    p_status VARCHAR(20) DEFAULT 'Active'
)
RETURNS INT AS $$
DECLARE
    new_bus_id INT;
    route_exists BOOLEAN;
BEGIN
    -- Validate plate number
    IF p_plate_number IS NULL OR LENGTH(TRIM(p_plate_number)) = 0 THEN
        RAISE EXCEPTION 'Plate number cannot be empty';
    END IF;

    -- Validate route exists
    SELECT EXISTS(SELECT 1 FROM Routes WHERE id = p_route_id) INTO route_exists;
    IF NOT route_exists THEN
        RAISE EXCEPTION 'Route with ID % does not exist', p_route_id;
    END IF;

    -- Validate status
    IF p_status NOT IN ('Active', 'Inactive', 'Maintenance', 'Retired') THEN
        RAISE EXCEPTION 'Invalid status. Must be one of: Active, Inactive, Maintenance, Retired';
    END IF;

    -- Insert bus
    INSERT INTO Buses (plate_number, name, model, route_id, status, current_location)
    VALUES (
        UPPER(TRIM(p_plate_number)),
        TRIM(p_name),
        TRIM(p_model),
        p_route_id,
        p_status,
        NULL
    )
    RETURNING bus_id INTO new_bus_id;

    RAISE NOTICE 'Bus created successfully with ID: %', new_bus_id;
    RETURN new_bus_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Plate number % already exists', p_plate_number;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BUS LOCATION UPDATE
-- ============================================================================

-- Function: fn_update_bus_location
-- Description: Updates bus current location
-- Parameters:
--   p_bus_id: Bus ID
--   p_lat: Latitude
--   p_lon: Longitude
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_bus_location(1, 10.8231, 106.6297);
CREATE OR REPLACE FUNCTION fn_update_bus_location(
    p_bus_id INT,
    p_lat NUMERIC,
    p_lon NUMERIC
)
RETURNS BOOLEAN AS $$
DECLARE
    bus_exists BOOLEAN;
    v_location GEOMETRY(POINT, 4326);
BEGIN
    -- Check if bus exists
    SELECT EXISTS(SELECT 1 FROM Buses WHERE bus_id = p_bus_id) INTO bus_exists;
    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Create point geometry
    v_location := fn_create_point(p_lat, p_lon);

    -- Update bus location
    UPDATE Buses
    SET current_location = v_location
    WHERE bus_id = p_bus_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BUS STATUS UPDATE
-- ============================================================================

-- Function: fn_update_bus_status
-- Description: Updates bus status with validation
-- Parameters:
--   p_bus_id: Bus ID
--   p_new_status: New status
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_bus_status(1, 'Maintenance');
CREATE OR REPLACE FUNCTION fn_update_bus_status(
    p_bus_id INT,
    p_new_status VARCHAR(20)
)
RETURNS BOOLEAN AS $$
DECLARE
    bus_exists BOOLEAN;
BEGIN
    -- Validate status
    IF p_new_status NOT IN ('Active', 'Inactive', 'Maintenance', 'Retired') THEN
        RAISE EXCEPTION 'Invalid status. Must be one of: Active, Inactive, Maintenance, Retired';
    END IF;

    -- Check if bus exists
    SELECT EXISTS(SELECT 1 FROM Buses WHERE bus_id = p_bus_id) INTO bus_exists;
    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Update status
    UPDATE Buses
    SET status = p_new_status
    WHERE bus_id = p_bus_id;

    RAISE NOTICE 'Bus % status updated to %', p_bus_id, p_new_status;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BUS ROUTE ASSIGNMENT
-- ============================================================================

-- Function: fn_assign_bus_to_route
-- Description: Assigns or reassigns a bus to a different route
-- Parameters:
--   p_bus_id: Bus ID
--   p_route_id: New route ID
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_assign_bus_to_route(1, 2);
CREATE OR REPLACE FUNCTION fn_assign_bus_to_route(
    p_bus_id INT,
    p_route_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    bus_exists BOOLEAN;
    route_exists BOOLEAN;
BEGIN
    -- Check if bus exists
    SELECT EXISTS(SELECT 1 FROM Buses WHERE bus_id = p_bus_id) INTO bus_exists;
    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Check if route exists
    SELECT EXISTS(SELECT 1 FROM Routes WHERE id = p_route_id) INTO route_exists;
    IF NOT route_exists THEN
        RAISE EXCEPTION 'Route with ID % does not exist', p_route_id;
    END IF;

    -- Assign bus to route
    UPDATE Buses
    SET route_id = p_route_id
    WHERE bus_id = p_bus_id;

    RAISE NOTICE 'Bus % assigned to route %', p_bus_id, p_route_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET BUSES ON ROUTE
-- ============================================================================

-- Function: fn_get_buses_on_route
-- Description: Returns all buses assigned to a route
-- Parameters:
--   p_route_id: Route ID
-- Returns: TABLE with bus information
-- Usage: SELECT * FROM fn_get_buses_on_route(1);
CREATE OR REPLACE FUNCTION fn_get_buses_on_route(p_route_id INT)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    model VARCHAR(50),
    status VARCHAR(20),
    current_latitude NUMERIC,
    current_longitude NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.bus_id,
        b.plate_number,
        b.name,
        b.model,
        b.status,
        CASE WHEN b.current_location IS NOT NULL THEN ST_Y(b.current_location) ELSE NULL END AS current_latitude,
        CASE WHEN b.current_location IS NOT NULL THEN ST_X(b.current_location) ELSE NULL END AS current_longitude
    FROM Buses b
    WHERE b.route_id = p_route_id
    ORDER BY b.name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FIND NEAREST BUS
-- ============================================================================

-- Function: fn_find_nearest_bus
-- Description: Finds the nearest bus to a location
-- Parameters:
--   p_lat: Latitude
--   p_lon: Longitude
--   p_route_id: Optional route ID filter
--   p_limit: Maximum number of results (default 5)
-- Returns: TABLE with bus information and distance
-- Usage: SELECT * FROM fn_find_nearest_bus(10.8231, 106.6297, NULL, 5);
CREATE OR REPLACE FUNCTION fn_find_nearest_bus(
    p_lat NUMERIC,
    p_lon NUMERIC,
    p_route_id INT DEFAULT NULL,
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    route_id INT,
    route_name VARCHAR(100),
    status VARCHAR(20),
    distance_meters NUMERIC,
    current_latitude NUMERIC,
    current_longitude NUMERIC
) AS $$
DECLARE
    v_point GEOMETRY(POINT, 4326);
BEGIN
    v_point := fn_create_point(p_lat, p_lon);

    RETURN QUERY
    SELECT
        b.bus_id,
        b.plate_number,
        b.name,
        b.route_id,
        r.name AS route_name,
        b.status,
        ST_Distance(b.current_location::geography, v_point::geography) AS distance_meters,
        ST_Y(b.current_location) AS current_latitude,
        ST_X(b.current_location) AS current_longitude
    FROM Buses b
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE b.current_location IS NOT NULL
        AND b.status = 'Active'
        AND (p_route_id IS NULL OR b.route_id = p_route_id)
    ORDER BY b.current_location <-> v_point
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- CHECK IF BUS IS ON ROUTE
-- ============================================================================

-- Function: fn_is_bus_on_route
-- Description: Checks if bus location is within tolerance of assigned route
-- Parameters:
--   p_bus_id: Bus ID
--   p_tolerance_meters: Distance tolerance in meters (default 100)
-- Returns: BOOLEAN - TRUE if on route
-- Usage: SELECT fn_is_bus_on_route(1, 100);
CREATE OR REPLACE FUNCTION fn_is_bus_on_route(
    p_bus_id INT,
    p_tolerance_meters INT DEFAULT 100
)
RETURNS BOOLEAN AS $$
DECLARE
    v_route_id INT;
    v_current_location GEOMETRY;
    v_route_geom GEOMETRY;
    is_on_route BOOLEAN;
BEGIN
    -- Get bus location and route
    SELECT route_id, current_location
    INTO v_route_id, v_current_location
    FROM Buses
    WHERE bus_id = p_bus_id;

    IF v_current_location IS NULL THEN
        RAISE NOTICE 'Bus % has no current location', p_bus_id;
        RETURN FALSE;
    END IF;

    -- Get route geometry
    SELECT route_geom INTO v_route_geom
    FROM Routes
    WHERE id = v_route_id;

    IF v_route_geom IS NULL THEN
        RAISE NOTICE 'Route has no geometry';
        RETURN FALSE;
    END IF;

    -- Check if bus is within tolerance of route
    SELECT ST_DWithin(v_route_geom::geography, v_current_location::geography, p_tolerance_meters)
    INTO is_on_route;

    RETURN is_on_route;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ALL BUSES
-- ============================================================================

-- Function: fn_get_all_buses
-- Description: Returns all buses with route information
-- Parameters:
--   p_include_inactive: Include inactive/maintenance/retired buses (default FALSE)
-- Returns: TABLE with bus information
-- Usage: SELECT * FROM fn_get_all_buses(FALSE);
CREATE OR REPLACE FUNCTION fn_get_all_buses(p_include_inactive BOOLEAN DEFAULT FALSE)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    model VARCHAR(50),
    status VARCHAR(20),
    route_id INT,
    route_name VARCHAR(100),
    current_latitude NUMERIC,
    current_longitude NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.bus_id,
        b.plate_number,
        b.name,
        b.model,
        b.status,
        b.route_id,
        r.name AS route_name,
        CASE WHEN b.current_location IS NOT NULL THEN ST_Y(b.current_location) ELSE NULL END AS current_latitude,
        CASE WHEN b.current_location IS NOT NULL THEN ST_X(b.current_location) ELSE NULL END AS current_longitude
    FROM Buses b
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE p_include_inactive OR b.status = 'Active'
    ORDER BY b.name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET BUS BY PLATE NUMBER
-- ============================================================================

-- Function: fn_get_bus_by_plate
-- Description: Retrieves bus information by plate number
-- Parameters:
--   p_plate_number: Plate number to search
-- Returns: TABLE with bus information
-- Usage: SELECT * FROM fn_get_bus_by_plate('29A-12345');
CREATE OR REPLACE FUNCTION fn_get_bus_by_plate(p_plate_number VARCHAR(20))
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    model VARCHAR(50),
    status VARCHAR(20),
    route_id INT,
    route_name VARCHAR(100),
    current_latitude NUMERIC,
    current_longitude NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.bus_id,
        b.plate_number,
        b.name,
        b.model,
        b.status,
        b.route_id,
        r.name AS route_name,
        CASE WHEN b.current_location IS NOT NULL THEN ST_Y(b.current_location) ELSE NULL END AS current_latitude,
        CASE WHEN b.current_location IS NOT NULL THEN ST_X(b.current_location) ELSE NULL END AS current_longitude
    FROM Buses b
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE UPPER(b.plate_number) = UPPER(TRIM(p_plate_number));
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET BUS LOCATION DETAILS
-- ============================================================================

-- Function: fn_get_bus_location_details
-- Description: Gets detailed location information for a bus
-- Parameters:
--   p_bus_id: Bus ID
-- Returns: TABLE with location details
-- Usage: SELECT * FROM fn_get_bus_location_details(1);
CREATE OR REPLACE FUNCTION fn_get_bus_location_details(p_bus_id INT)
RETURNS TABLE (
    bus_id INT,
    bus_name VARCHAR(100),
    current_latitude NUMERIC,
    current_longitude NUMERIC,
    route_id INT,
    route_name VARCHAR(100),
    is_on_route BOOLEAN,
    nearest_stop_id INT,
    nearest_stop_name VARCHAR(255),
    distance_to_stop_meters NUMERIC
) AS $$
DECLARE
    v_current_location GEOMETRY;
BEGIN
    -- Get current location
    SELECT current_location INTO v_current_location
    FROM Buses
    WHERE Buses.bus_id = p_bus_id;

    RETURN QUERY
    SELECT
        b.bus_id,
        b.name,
        CASE WHEN b.current_location IS NOT NULL THEN ST_Y(b.current_location) ELSE NULL END AS current_latitude,
        CASE WHEN b.current_location IS NOT NULL THEN ST_X(b.current_location) ELSE NULL END AS current_longitude,
        b.route_id,
        r.name AS route_name,
        CASE
            WHEN b.current_location IS NOT NULL THEN fn_is_bus_on_route(b.bus_id, 100)
            ELSE FALSE
        END AS is_on_route,
        nearest.stop_id,
        nearest.stop_name,
        nearest.distance_meters
    FROM Buses b
    INNER JOIN Routes r ON b.route_id = r.id
    LEFT JOIN LATERAL (
        SELECT
            s.id AS stop_id,
            s.name AS stop_name,
            ST_Distance(s.location::geography, b.current_location::geography) AS distance_meters
        FROM Stops s
        INNER JOIN RouteStops rs ON s.id = rs.stop_id
        WHERE rs.route_id = b.route_id
            AND b.current_location IS NOT NULL
        ORDER BY s.location <-> b.current_location
        LIMIT 1
    ) nearest ON TRUE
    WHERE b.bus_id = p_bus_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ACTIVE BUSES COUNT
-- ============================================================================

-- Function: fn_get_active_buses_count
-- Description: Returns count of active buses
-- Returns: INT - Number of active buses
-- Usage: SELECT fn_get_active_buses_count();
CREATE OR REPLACE FUNCTION fn_get_active_buses_count()
RETURNS INT AS $$
DECLARE
    active_count INT;
BEGIN
    SELECT COUNT(*)
    INTO active_count
    FROM Buses
    WHERE status = 'Active';

    RETURN active_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- Create a bus:
-- SELECT fn_create_bus('29A-12345', 'Bus 101', 1, 'Hyundai Universe', 'Active');

-- Update bus location:
-- SELECT fn_update_bus_location(1, 10.8231, 106.6297);

-- Update bus status:
-- SELECT fn_update_bus_status(1, 'Maintenance');

-- Assign bus to route:
-- SELECT fn_assign_bus_to_route(1, 2);

-- Get buses on route:
-- SELECT * FROM fn_get_buses_on_route(1);

-- Find nearest bus:
-- SELECT * FROM fn_find_nearest_bus(10.8231, 106.6297, NULL, 5);

-- Check if bus is on route:
-- SELECT fn_is_bus_on_route(1, 100);

-- Get all buses:
-- SELECT * FROM fn_get_all_buses(FALSE);

-- Get bus by plate number:
-- SELECT * FROM fn_get_bus_by_plate('29A-12345');

-- Get bus location details:
-- SELECT * FROM fn_get_bus_location_details(1);

-- Get active buses count:
-- SELECT fn_get_active_buses_count();
