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
    p_status bus_status DEFAULT 'Active'
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
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION
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
--   p_new_status: New status (Active, Inactive, Maintenance)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_bus_status(1, 'Maintenance');
DROP FUNCTION IF EXISTS fn_update_bus_status;
CREATE OR REPLACE FUNCTION fn_update_bus_status(
    p_bus_id INT,
    p_new_status bus_status
)
RETURNS BOOLEAN AS $$
DECLARE
    bus_exists BOOLEAN;
BEGIN
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
DROP FUNCTION IF EXISTS fn_assign_bus_to_route;
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
DROP FUNCTION IF EXISTS fn_get_buses_on_route;
CREATE OR REPLACE FUNCTION fn_get_buses_on_route(p_route_id INT)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    model VARCHAR(50),
    status bus_status,
    current_latitude DOUBLE PRECISION,
    current_longitude DOUBLE PRECISION
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
DROP FUNCTION IF EXISTS fn_find_nearest_bus;
CREATE OR REPLACE FUNCTION fn_find_nearest_bus(
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION,
    p_route_id INT DEFAULT NULL,
    p_limit INT DEFAULT 5
)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    route_id INT,
    route_name VARCHAR(100),
    status bus_status,
    distance_meters DOUBLE PRECISION,
    current_latitude DOUBLE PRECISION,
    current_longitude DOUBLE PRECISION
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
DROP FUNCTION IF EXISTS fn_is_bus_on_route;
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
DROP FUNCTION IF EXISTS fn_get_all_buses;
CREATE OR REPLACE FUNCTION fn_get_all_buses(p_include_inactive BOOLEAN DEFAULT FALSE)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    model VARCHAR(50),
    status bus_status,
    route_id INT,
    route_name VARCHAR(100),
    current_latitude DOUBLE PRECISION,
    current_longitude DOUBLE PRECISION
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
DROP FUNCTION IF EXISTS fn_get_bus_by_plate;
CREATE OR REPLACE FUNCTION fn_get_bus_by_plate(p_plate_number VARCHAR(20))
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR(20),
    name VARCHAR(100),
    model VARCHAR(50),
    status bus_status,
    route_id INT,
    route_name VARCHAR(100),
    current_latitude DOUBLE PRECISION,
    current_longitude DOUBLE PRECISION
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
DROP FUNCTION IF EXISTS fn_get_bus_location_details;
CREATE OR REPLACE FUNCTION fn_get_bus_location_details(p_bus_id INT)
RETURNS TABLE (
    bus_id INT,
    bus_name VARCHAR(100),
    current_latitude DOUBLE PRECISION,
    current_longitude DOUBLE PRECISION,
    route_id INT,
    route_name VARCHAR(100),
    is_on_route BOOLEAN,
    nearest_stop_id INT,
    nearest_stop_name VARCHAR(255),
    distance_to_stop_meters DOUBLE PRECISION
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
DROP FUNCTION IF EXISTS fn_get_active_buses_count;
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
-- INITIALIZE BUS POSITIONS
-- ============================================================================

-- Function: fn_initialize_bus_positions
-- Description: Initializes positions for buses without current_location or route_progress
-- Returns: INT - Count of buses initialized
-- Usage: SELECT fn_initialize_bus_positions();
DROP FUNCTION IF EXISTS fn_initialize_bus_positions;
CREATE OR REPLACE FUNCTION fn_initialize_bus_positions()
RETURNS INT AS $$
DECLARE
    v_bus RECORD;
    v_first_stop_location GEOMETRY;
    v_route_geom GEOMETRY;
    v_progress DOUBLE PRECISION;
    initialized_count INT := 0;
BEGIN
    -- Loop through buses that need initialization
    FOR v_bus IN
        SELECT bus_id, route_id
        FROM Buses
        WHERE current_location IS NULL OR route_progress IS NULL
    LOOP
        -- Get route geometry
        SELECT route_geom INTO v_route_geom
        FROM Routes
        WHERE id = v_bus.route_id;

        IF v_route_geom IS NULL THEN
            RAISE NOTICE 'Bus % has route % with no geometry, skipping', v_bus.bus_id, v_bus.route_id;
            CONTINUE;
        END IF;

        -- Get first stop on route
        SELECT s.location INTO v_first_stop_location
        FROM Stops s
        INNER JOIN RouteStops rs ON s.id = rs.stop_id
        WHERE rs.route_id = v_bus.route_id
        ORDER BY rs.stop_sequence ASC
        LIMIT 1;

        -- If no stops, start at beginning of route
        IF v_first_stop_location IS NULL THEN
            v_first_stop_location := ST_StartPoint(v_route_geom);
            v_progress := 0.0;
        ELSE
            -- Calculate progress along route for first stop
            v_progress := ST_LineLocatePoint(v_route_geom, v_first_stop_location);
        END IF;

        -- Update bus with initial position
        UPDATE Buses
        SET current_location = v_first_stop_location,
            route_progress = v_progress,
            direction = 1,
            last_updated = NOW()
        WHERE bus_id = v_bus.bus_id;

        initialized_count := initialized_count + 1;
        RAISE NOTICE 'Initialized bus % at progress %', v_bus.bus_id, v_progress;
    END LOOP;

    RAISE NOTICE 'Initialized % buses', initialized_count;
    RETURN initialized_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SNAP BUS TO ROUTE
-- ============================================================================

-- Function: fn_snap_bus_to_route
-- Description: Snaps an off-route bus back to the nearest point on its assigned route
-- Parameters:
--   p_bus_id: Bus ID
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_snap_bus_to_route(1);
DROP FUNCTION IF EXISTS fn_snap_bus_to_route;
CREATE OR REPLACE FUNCTION fn_snap_bus_to_route(p_bus_id INT)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_location GEOMETRY;
    v_route_geom GEOMETRY;
    v_closest_point GEOMETRY;
    v_progress DOUBLE PRECISION;
BEGIN
    -- Get bus location and route geometry
    SELECT b.current_location, r.route_geom
    INTO v_current_location, v_route_geom
    FROM Buses b
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE b.bus_id = p_bus_id;

    IF v_current_location IS NULL THEN
        RAISE EXCEPTION 'Bus % has no current location', p_bus_id;
    END IF;

    IF v_route_geom IS NULL THEN
        RAISE EXCEPTION 'Bus % route has no geometry', p_bus_id;
    END IF;

    -- Find closest point on route
    v_closest_point := ST_ClosestPoint(v_route_geom, v_current_location);

    -- Calculate progress along route
    v_progress := ST_LineLocatePoint(v_route_geom, v_closest_point);

    -- Update bus position
    UPDATE Buses
    SET current_location = v_closest_point,
        route_progress = v_progress,
        last_updated = NOW()
    WHERE bus_id = p_bus_id;

    RAISE NOTICE 'Snapped bus % to route at progress %', p_bus_id, v_progress;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- AUTO-UPDATE BUS POSITIONS
-- ============================================================================

-- Function: fn_update_bus_positions_auto
-- Description: Moves all active buses along their routes by one step
-- Parameters:
--   p_speed_meters_per_second: Bus speed in m/s (default 10.0 = 36 km/h)
--   p_time_step_seconds: Time elapsed since last update (default 30 seconds)
-- Returns: TABLE with update results
-- Usage: SELECT * FROM fn_update_bus_positions_auto(10.0, 30);
DROP FUNCTION IF EXISTS fn_update_bus_positions_auto;
CREATE OR REPLACE FUNCTION fn_update_bus_positions_auto(
    p_speed_meters_per_second DOUBLE PRECISION DEFAULT 10.0,
    p_time_step_seconds INT DEFAULT 30
)
RETURNS TABLE (
    bus_id INT,
    updated BOOLEAN,
    new_progress DOUBLE PRECISION,
    new_latitude DOUBLE PRECISION,
    new_longitude DOUBLE PRECISION
) AS $$
DECLARE
    v_bus RECORD;
    v_route_length DOUBLE PRECISION;
    v_distance_to_move DOUBLE PRECISION;
    v_progress_delta DOUBLE PRECISION;
    v_new_progress DOUBLE PRECISION;
    v_new_location GEOMETRY;
    v_new_direction INT;
BEGIN
    -- Calculate distance to move
    v_distance_to_move := p_speed_meters_per_second * p_time_step_seconds;

    -- Loop through all active buses
    FOR v_bus IN
        SELECT b.bus_id, b.route_id, b.current_location, b.route_progress,
               b.direction, r.route_geom
        FROM Buses b
        INNER JOIN Routes r ON b.route_id = r.id
        WHERE b.status = 'Active' AND r.route_geom IS NOT NULL
    LOOP
        BEGIN
            -- Calculate route length in meters
            v_route_length := ST_Length(v_bus.route_geom::geography);

            -- Skip if route has no length
            IF v_route_length = 0 OR v_route_length IS NULL THEN
                RAISE NOTICE 'Bus % route has zero length, skipping', v_bus.bus_id;
                CONTINUE;
            END IF;

            -- Initialize progress if NULL
            IF v_bus.route_progress IS NULL THEN
                IF v_bus.current_location IS NULL THEN
                    v_bus.route_progress := 0.0;
                    v_bus.current_location := ST_StartPoint(v_bus.route_geom);
                ELSE
                    v_bus.route_progress := ST_LineLocatePoint(v_bus.route_geom, v_bus.current_location);
                END IF;
                v_bus.direction := 1;
            END IF;

            -- Calculate progress delta (fraction of route)
            v_progress_delta := v_distance_to_move / v_route_length;

            -- Calculate new progress based on direction
            v_new_progress := v_bus.route_progress + (v_progress_delta * v_bus.direction);
            v_new_direction := v_bus.direction;

            -- Handle route endpoints (reverse direction)
            IF v_new_progress >= 1.0 THEN
                v_new_progress := 2.0 - v_new_progress; -- Bounce back
                v_new_direction := -1;
                IF v_new_progress < 0 THEN
                    v_new_progress := 0.01;
                END IF;
            ELSIF v_new_progress <= 0.0 THEN
                v_new_progress := ABS(v_new_progress); -- Bounce back
                v_new_direction := 1;
                IF v_new_progress > 1.0 THEN
                    v_new_progress := 0.99;
                END IF;
            END IF;

            -- Clamp progress to valid range
            v_new_progress := GREATEST(0.0, LEAST(1.0, v_new_progress));

            -- Get new location point on route
            v_new_location := ST_LineInterpolatePoint(v_bus.route_geom, v_new_progress);

            -- Update bus position
            UPDATE Buses
            SET current_location = v_new_location,
                route_progress = v_new_progress,
                direction = v_new_direction,
                last_updated = NOW()
            WHERE Buses.bus_id = v_bus.bus_id;

            -- Return result
            bus_id := v_bus.bus_id;
            updated := TRUE;
            new_progress := v_new_progress;
            new_latitude := ST_Y(v_new_location);
            new_longitude := ST_X(v_new_location);
            RETURN NEXT;

        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error updating bus %: %', v_bus.bus_id, SQLERRM;
            bus_id := v_bus.bus_id;
            updated := FALSE;
            new_progress := NULL;
            new_latitude := NULL;
            new_longitude := NULL;
            RETURN NEXT;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

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
