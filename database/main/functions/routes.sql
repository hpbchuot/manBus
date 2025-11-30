-- ============================================================================
-- ROUTES.SQL - Route and Stop Management Functions
-- ============================================================================
-- Description: Functions for managing routes, stops, and spatial operations
-- Dependencies: Routes, Stops, RouteStops tables, PostGIS extension, utilities.sql
-- ============================================================================

-- ============================================================================
-- ROUTE CREATION
-- ============================================================================

-- Function: fn_create_route
-- Description: Creates a new route with geometry from coordinate array
-- Parameters:
--   p_route_name: Name of the route
--   p_coordinates: JSONB array of [lat, lon] pairs
-- Returns: INT - New route ID
-- Usage: SELECT fn_create_route('Route 1', '[[10.8231,106.6297],[10.8241,106.6307]]'::jsonb);
CREATE OR REPLACE FUNCTION fn_create_route(
    p_route_name VARCHAR(100),
    p_coordinates JSONB
)
RETURNS INT AS $$
DECLARE
    new_route_id INT;
    v_route_geom GEOMETRY(LINESTRING, 4326);
BEGIN
    -- Validate route name
    IF p_route_name IS NULL OR LENGTH(TRIM(p_route_name)) = 0 THEN
        RAISE EXCEPTION 'Route name cannot be empty';
    END IF;

    -- Create linestring from coordinates
    v_route_geom := fn_create_linestring(p_coordinates);

    -- Insert route
    INSERT INTO Routes (name, route_geom, current_segment, updated_at)
    VALUES (TRIM(p_route_name), v_route_geom, 0, NOW())
    RETURNING id INTO new_route_id;

    RAISE NOTICE 'Route created successfully with ID: %', new_route_id;
    RETURN new_route_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROUTE UPDATE
-- ============================================================================

-- Function: fn_update_route_geometry
-- Description: Updates route geometry
-- Parameters:
--   p_route_id: Route ID to update
--   p_coordinates: New JSONB array of [lat, lon] pairs
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_route_geometry(1, '[[10.8231,106.6297],[10.8241,106.6307]]'::jsonb);
CREATE OR REPLACE FUNCTION fn_update_route_geometry(
    p_route_id INT,
    p_coordinates JSONB
)
RETURNS BOOLEAN AS $$
DECLARE
    route_exists BOOLEAN;
    v_route_geom GEOMETRY(LINESTRING, 4326);
BEGIN
    -- Check if route exists
    SELECT EXISTS(SELECT 1 FROM Routes WHERE id = p_route_id) INTO route_exists;

    IF NOT route_exists THEN
        RAISE EXCEPTION 'Route with ID % does not exist', p_route_id;
    END IF;

    -- Create linestring from coordinates
    v_route_geom := fn_create_linestring(p_coordinates);

    -- Update route geometry
    UPDATE Routes
    SET
        route_geom = v_route_geom,
        updated_at = NOW()
    WHERE id = p_route_id;

    RAISE NOTICE 'Route % geometry updated successfully', p_route_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- STOP CREATION
-- ============================================================================

-- Function: fn_create_stop
-- Description: Creates a new bus stop
-- Parameters:
--   p_stop_name: Name of the stop
--   p_lat: Latitude
--   p_lon: Longitude
-- Returns: INT - New stop ID
-- Usage: SELECT fn_create_stop('Stop 1', 10.8231, 106.6297);
CREATE OR REPLACE FUNCTION fn_create_stop(
    p_stop_name VARCHAR(255),
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION
)
RETURNS INT AS $$
DECLARE
    new_stop_id INT;
    v_location GEOMETRY(POINT, 4326);
BEGIN
    -- Validate stop name
    IF p_stop_name IS NULL OR LENGTH(TRIM(p_stop_name)) = 0 THEN
        RAISE EXCEPTION 'Stop name cannot be empty';
    END IF;

    -- Create point geometry
    v_location := fn_create_point(p_lat, p_lon);

    -- Insert stop
    INSERT INTO Stops (name, location)
    VALUES (TRIM(p_stop_name), v_location)
    RETURNING id INTO new_stop_id;

    RAISE NOTICE 'Stop created successfully with ID: %', new_stop_id;
    RETURN new_stop_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROUTE-STOP ASSOCIATION
-- ============================================================================

-- Function: fn_add_stop_to_route
-- Description: Adds a stop to a route with sequence number
-- Parameters:
--   p_route_id: Route ID
--   p_stop_id: Stop ID
--   p_sequence: Sequence number (order of stop on route)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_add_stop_to_route(1, 1, 1);
CREATE OR REPLACE FUNCTION fn_add_stop_to_route(
    p_route_id INT,
    p_stop_id INT,
    p_sequence INT DEFAULT 0
)
RETURNS BOOLEAN AS $$
DECLARE
    route_exists BOOLEAN;
    stop_exists BOOLEAN;
    already_associated BOOLEAN;
BEGIN
    -- Validate route exists
    SELECT EXISTS(SELECT 1 FROM Routes WHERE id = p_route_id) INTO route_exists;
    IF NOT route_exists THEN
        RAISE EXCEPTION 'Route with ID % does not exist', p_route_id;
    END IF;

    -- Validate stop exists
    SELECT EXISTS(SELECT 1 FROM Stops WHERE id = p_stop_id) INTO stop_exists;
    IF NOT stop_exists THEN
        RAISE EXCEPTION 'Stop with ID % does not exist', p_stop_id;
    END IF;

    -- Check if already associated
    SELECT EXISTS(
        SELECT 1 FROM RouteStops WHERE route_id = p_route_id AND stop_id = p_stop_id
    ) INTO already_associated;

    IF already_associated THEN
        RAISE NOTICE 'Stop % is already on route %', p_stop_id, p_route_id;
        RETURN FALSE;
    END IF;

    -- Add stop to route
    INSERT INTO RouteStops (route_id, stop_id, stop_sequence, created_at)
    VALUES (p_route_id, p_stop_id, p_sequence, NOW());

    RAISE NOTICE 'Stop % added to route % with sequence %', p_stop_id, p_route_id, p_sequence;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROUTE-STOP REMOVAL
-- ============================================================================

-- Function: fn_remove_stop_from_route
-- Description: Removes a stop from a route
-- Parameters:
--   p_route_id: Route ID
--   p_stop_id: Stop ID
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_remove_stop_from_route(1, 1);
CREATE OR REPLACE FUNCTION fn_remove_stop_from_route(
    p_route_id INT,
    p_stop_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    deleted_count INT;
BEGIN
    DELETE FROM RouteStops
    WHERE route_id = p_route_id AND stop_id = p_stop_id;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    IF deleted_count = 0 THEN
        RAISE NOTICE 'Stop % was not on route %', p_stop_id, p_route_id;
        RETURN FALSE;
    END IF;

    RAISE NOTICE 'Stop % removed from route %', p_stop_id, p_route_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- REORDER ROUTE STOPS
-- ============================================================================

-- Function: fn_reorder_route_stops
-- Description: Updates stop sequences for a route
-- Parameters:
--   p_route_id: Route ID
--   p_stop_sequences: JSONB array of objects with stop_id and sequence
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_reorder_route_stops(1, '[{"stop_id":1,"sequence":1},{"stop_id":2,"sequence":2}]'::jsonb);
CREATE OR REPLACE FUNCTION fn_reorder_route_stops(
    p_route_id INT,
    p_stop_sequences JSONB
)
RETURNS BOOLEAN AS $$
DECLARE
    stop_data JSONB;
    v_stop_id INT;
    v_sequence INT;
    route_exists BOOLEAN;
BEGIN
    -- Check if route exists
    SELECT EXISTS(SELECT 1 FROM Routes WHERE id = p_route_id) INTO route_exists;
    IF NOT route_exists THEN
        RAISE EXCEPTION 'Route with ID % does not exist', p_route_id;
    END IF;

    -- Update each stop sequence
    FOR stop_data IN SELECT * FROM jsonb_array_elements(p_stop_sequences)
    LOOP
        v_stop_id := (stop_data->>'stop_id')::INT;
        v_sequence := (stop_data->>'sequence')::INT;

        UPDATE RouteStops
        SET stop_sequence = v_sequence
        WHERE route_id = p_route_id AND stop_id = v_stop_id;
    END LOOP;

    RAISE NOTICE 'Route % stops reordered successfully', p_route_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SPATIAL QUERIES - ROUTE LENGTH
-- ============================================================================

-- Function: fn_get_route_length
-- Description: Calculates route length in meters
-- Parameters:
--   p_route_id: Route ID
-- Returns: DOUBLE PRECISION - Length in meters
-- Usage: SELECT fn_get_route_length(1);
CREATE OR REPLACE FUNCTION fn_get_route_length(p_route_id INT)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    route_length DOUBLE PRECISION;
    v_route_geom GEOMETRY;
BEGIN
    SELECT route_geom INTO v_route_geom
    FROM Routes
    WHERE id = p_route_id;

    IF v_route_geom IS NULL THEN
        RAISE EXCEPTION 'Route with ID % does not exist or has no geometry', p_route_id;
    END IF;

    -- ST_Length returns degrees, ST_Length with geography cast returns meters
    route_length := ST_Length(v_route_geom::geography);

    RETURN route_length;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SPATIAL QUERIES - NEAREST STOPS
-- ============================================================================

-- Function: fn_find_nearest_stops
-- Description: Finds stops within a radius of a location
-- Parameters:
--   p_lat: Latitude
--   p_lon: Longitude
--   p_radius_meters: Search radius in meters
--   p_limit: Maximum number of results (default 10)
-- Returns: TABLE with stop information and distance
-- Usage: SELECT * FROM fn_find_nearest_stops(10.8231, 106.6297, 1000, 10);
CREATE OR REPLACE FUNCTION fn_find_nearest_stops(
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION,
    p_radius_meters INT DEFAULT 1000,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    stop_id INT,
    stop_name VARCHAR(255),
    distance_meters DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
) AS $$
DECLARE
    v_point GEOMETRY(POINT, 4326);
BEGIN
    v_point := fn_create_point(p_lat, p_lon);

    RETURN QUERY
    SELECT
        s.id,
        s.name,
        ST_Distance(s.location::geography, v_point::geography) AS distance_meters,
        ST_Y(s.location) AS latitude,
        ST_X(s.location) AS longitude
    FROM Stops s
    WHERE ST_DWithin(s.location::geography, v_point::geography, p_radius_meters)
    ORDER BY s.location <-> v_point
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SPATIAL QUERIES - ROUTES NEAR LOCATION
-- ============================================================================

-- Function: fn_find_routes_near_location
-- Description: Finds routes passing near a location
-- Parameters:
--   p_lat: Latitude
--   p_lon: Longitude
--   p_radius_meters: Search radius in meters
-- Returns: TABLE with route information and distance
-- Usage: SELECT * FROM fn_find_routes_near_location(10.8231, 106.6297, 500);
CREATE OR REPLACE FUNCTION fn_find_routes_near_location(
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION,
    p_radius_meters INT DEFAULT 500
)
RETURNS TABLE (
    route_id INT,
    route_name VARCHAR(100),
    distance_meters DOUBLE PRECISION
) AS $$
DECLARE
    v_point GEOMETRY(POINT, 4326);
BEGIN
    v_point := fn_create_point(p_lat, p_lon);

    RETURN QUERY
    SELECT
        r.id,
        r.name,
        ST_Distance(r.route_geom::geography, v_point::geography) AS distance_meters
    FROM Routes r
    WHERE r.route_geom IS NOT NULL
        AND ST_DWithin(r.route_geom::geography, v_point::geography, p_radius_meters)
    ORDER BY r.route_geom <-> v_point;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- SPATIAL QUERIES - POINT ON ROUTE CHECK
-- ============================================================================

-- Function: fn_is_point_on_route
-- Description: Checks if a point is within tolerance of a route
-- Parameters:
--   p_route_id: Route ID
--   p_lat: Latitude
--   p_lon: Longitude
--   p_tolerance_meters: Distance tolerance in meters (default 100)
-- Returns: BOOLEAN - TRUE if point is on route
-- Usage: SELECT fn_is_point_on_route(1, 10.8231, 106.6297, 100);
CREATE OR REPLACE FUNCTION fn_is_point_on_route(
    p_route_id INT,
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION,
    p_tolerance_meters INT DEFAULT 100
)
RETURNS BOOLEAN AS $$
DECLARE
    v_point GEOMETRY(POINT, 4326);
    v_route_geom GEOMETRY;
    is_on_route BOOLEAN;
BEGIN
    v_point := fn_create_point(p_lat, p_lon);

    SELECT route_geom INTO v_route_geom
    FROM Routes
    WHERE id = p_route_id;

    IF v_route_geom IS NULL THEN
        RAISE EXCEPTION 'Route with ID % does not exist or has no geometry', p_route_id;
    END IF;

    SELECT ST_DWithin(v_route_geom::geography, v_point::geography, p_tolerance_meters)
    INTO is_on_route;

    RETURN is_on_route;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET STOPS ON ROUTE
-- ============================================================================

-- Function: fn_get_stops_on_route
-- Description: Returns all stops for a route ordered by sequence
-- Parameters:
--   p_route_id: Route ID
-- Returns: TABLE with stop information
-- Usage: SELECT * FROM fn_get_stops_on_route(1);
CREATE OR REPLACE FUNCTION fn_get_stops_on_route(p_route_id INT)
RETURNS TABLE (
    stop_id INT,
    stop_name VARCHAR(255),
    stop_sequence INT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        rs.stop_sequence,
        ST_Y(s.location) AS latitude,
        ST_X(s.location) AS longitude
    FROM RouteStops rs
    INNER JOIN Stops s ON rs.stop_id = s.id
    WHERE rs.route_id = p_route_id
    ORDER BY rs.stop_sequence;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ALL ROUTES
-- ============================================================================

-- Function: fn_get_all_routes
-- Description: Returns all routes with basic information
-- Returns: TABLE with route information
-- Usage: SELECT * FROM fn_get_all_routes();
CREATE OR REPLACE FUNCTION fn_get_all_routes()
RETURNS TABLE (
    route_id INT,
    route_name VARCHAR(100),
    stop_count BIGINT,
    route_length_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name,
        COUNT(rs.stop_id) AS stop_count,
        CASE
            WHEN r.route_geom IS NOT NULL THEN ST_Length(r.route_geom::geography)
            ELSE NULL
        END AS route_length_meters
    FROM Routes r
    LEFT JOIN RouteStops rs ON r.id = rs.route_id
    GROUP BY r.id, r.name, r.route_geom
    ORDER BY r.id;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ROUTE BY ID WITH GEOJSON
-- ============================================================================

-- Function: fn_get_route_by_id
-- Description: Returns route by ID with geometry as GeoJSON
-- Parameters:
--   p_route_id: Route ID
-- Returns: TABLE with route information and GeoJSON geometry
-- Usage: SELECT * FROM fn_get_route_by_id(1);
CREATE OR REPLACE FUNCTION fn_get_route_by_id(p_route_id INT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    route_geom JSON,
    current_segment INT,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name,
        ST_AsGeoJSON(r.route_geom)::JSON AS route_geom,
        r.current_segment,
        r.updated_at
    FROM Routes r
    WHERE r.id = p_route_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ROUTE BY NAME WITH GEOJSON
-- ============================================================================

-- Function: fn_get_route_by_name
-- Description: Returns route by name with geometry as GeoJSON
-- Parameters:
--   p_route_name: Route name
-- Returns: TABLE with route information and GeoJSON geometry
-- Usage: SELECT * FROM fn_get_route_by_name('Route 1');
CREATE OR REPLACE FUNCTION fn_get_route_by_name(p_route_name VARCHAR(100))
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    route_geom JSON,
    current_segment INT,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.name,
        ST_AsGeoJSON(r.route_geom)::JSON AS route_geom,
        r.current_segment,
        r.updated_at
    FROM Routes r
    WHERE r.name = p_route_name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ROUTE AS GEOJSON (GEOMETRY ONLY)
-- ============================================================================

-- Function: fn_get_route_geojson
-- Description: Returns route geometry as GeoJSON for API consumption
-- Parameters:
--   p_route_id: Route ID
-- Returns: JSON - GeoJSON representation of route
-- Usage: SELECT fn_get_route_geojson(1);
CREATE OR REPLACE FUNCTION fn_get_route_geojson(p_route_id INT)
RETURNS JSON AS $$
DECLARE
    route_geojson JSON;
BEGIN
    SELECT ST_AsGeoJSON(route_geom)::JSON
    INTO route_geojson
    FROM Routes
    WHERE id = p_route_id;

    IF route_geojson IS NULL THEN
        RAISE EXCEPTION 'Route with ID % does not exist or has no geometry', p_route_id;
    END IF;

    RETURN route_geojson;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FIND ROUTES TO DESTINATION
-- ============================================================================

-- Function: fn_find_routes_to_destination
-- Description: Finds routes that pass near both origin AND destination points
-- Parameters:
--   p_origin_lat: Origin latitude
--   p_origin_lon: Origin longitude
--   p_dest_lat: Destination latitude
--   p_dest_lon: Destination longitude
--   p_radius_meters: Search radius in meters (default 500)
--   p_limit: Maximum number of results (default 10)
-- Returns: TABLE with route information and distances
-- Usage: SELECT * FROM fn_find_routes_to_destination(21.0285, 105.8542, 21.0368, 105.8347, 500, 5);
DROP FUNCTION IF EXISTS fn_find_routes_to_destination;
CREATE OR REPLACE FUNCTION fn_find_routes_to_destination(
    p_origin_lat DOUBLE PRECISION,
    p_origin_lon DOUBLE PRECISION,
    p_dest_lat DOUBLE PRECISION,
    p_dest_lon DOUBLE PRECISION,
    p_radius_meters INT DEFAULT 500,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    route_id INT,
    route_name VARCHAR,
    origin_distance_meters DOUBLE PRECISION,
    dest_distance_meters DOUBLE PRECISION,
    total_walking_distance DOUBLE PRECISION,
    active_bus_count BIGINT,
    nearest_origin_stop_id INT,
    nearest_origin_stop_name VARCHAR,
    nearest_dest_stop_id INT,
    nearest_dest_stop_name VARCHAR,
    route_length_meters DOUBLE PRECISION
) AS $$
DECLARE
    v_origin_point GEOMETRY(POINT, 4326);
    v_dest_point GEOMETRY(POINT, 4326);
BEGIN
    -- Create origin and destination points
    v_origin_point := fn_create_point(p_origin_lat, p_origin_lon);
    v_dest_point := fn_create_point(p_dest_lat, p_dest_lon);

    RETURN QUERY
    SELECT
        r.id AS route_id,
        r.name AS route_name,
        ST_Distance(r.route_geom::geography, v_origin_point::geography) AS origin_distance_meters,
        ST_Distance(r.route_geom::geography, v_dest_point::geography) AS dest_distance_meters,
        ST_Distance(r.route_geom::geography, v_origin_point::geography) +
            ST_Distance(r.route_geom::geography, v_dest_point::geography) AS total_walking_distance,
        (SELECT COUNT(*) FROM Buses b WHERE b.route_id = r.id AND b.status = 'Active') AS active_bus_count,
        origin_stop.stop_id AS nearest_origin_stop_id,
        origin_stop.stop_name AS nearest_origin_stop_name,
        dest_stop.stop_id AS nearest_dest_stop_id,
        dest_stop.stop_name AS nearest_dest_stop_name,
        ST_Length(r.route_geom::geography) AS route_length_meters
    FROM Routes r
    -- Find nearest stop to origin on this route
    LEFT JOIN LATERAL (
        SELECT s.id AS stop_id, s.name AS stop_name
        FROM Stops s
        INNER JOIN RouteStops rs ON s.id = rs.stop_id
        WHERE rs.route_id = r.id
        ORDER BY s.location <-> v_origin_point
        LIMIT 1
    ) origin_stop ON TRUE
    -- Find nearest stop to destination on this route
    LEFT JOIN LATERAL (
        SELECT s.id AS stop_id, s.name AS stop_name
        FROM Stops s
        INNER JOIN RouteStops rs ON s.id = rs.stop_id
        WHERE rs.route_id = r.id
        ORDER BY s.location <-> v_dest_point
        LIMIT 1
    ) dest_stop ON TRUE
    WHERE r.route_geom IS NOT NULL
        -- Route must pass within radius of BOTH origin AND destination
        AND ST_DWithin(r.route_geom::geography, v_origin_point::geography, p_radius_meters)
        AND ST_DWithin(r.route_geom::geography, v_dest_point::geography, p_radius_meters)
    ORDER BY total_walking_distance ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- FIND BUSES TO DESTINATION
-- ============================================================================

-- Function: fn_find_buses_to_destination
-- Description: Finds active buses on routes that connect origin and destination
-- Parameters:
--   p_origin_lat: Origin latitude
--   p_origin_lon: Origin longitude
--   p_dest_lat: Destination latitude
--   p_dest_lon: Destination longitude
--   p_radius_meters: Search radius in meters (default 500)
--   p_limit: Maximum number of results (default 10)
-- Returns: TABLE with bus and route information
-- Usage: SELECT * FROM fn_find_buses_to_destination(21.0285, 105.8542, 21.0368, 105.8347, 500, 5);
DROP FUNCTION IF EXISTS fn_find_buses_to_destination;
CREATE OR REPLACE FUNCTION fn_find_buses_to_destination(
    p_origin_lat DOUBLE PRECISION,
    p_origin_lon DOUBLE PRECISION,
    p_dest_lat DOUBLE PRECISION,
    p_dest_lon DOUBLE PRECISION,
    p_radius_meters INT DEFAULT 500,
    p_limit INT DEFAULT 10
)
RETURNS TABLE (
    bus_id INT,
    plate_number VARCHAR,
    bus_name VARCHAR,
    route_id INT,
    route_name VARCHAR,
    bus_distance_from_origin DOUBLE PRECISION,
    origin_distance_from_route DOUBLE PRECISION,
    dest_distance_from_route DOUBLE PRECISION,
    bus_lat DOUBLE PRECISION,
    bus_lon DOUBLE PRECISION
) AS $$
DECLARE
    v_origin_point GEOMETRY(POINT, 4326);
BEGIN
    -- Create origin point for distance calculation
    v_origin_point := fn_create_point(p_origin_lat, p_origin_lon);

    RETURN QUERY
    SELECT
        b.bus_id,
        b.plate_number,
        b.name AS bus_name,
        b.route_id,
        valid_routes.route_name,
        CASE
            WHEN b.current_location IS NOT NULL THEN
                ST_Distance(b.current_location::geography, v_origin_point::geography)
            ELSE NULL
        END AS bus_distance_from_origin,
        valid_routes.origin_distance_meters,
        valid_routes.dest_distance_meters,
        CASE WHEN b.current_location IS NOT NULL THEN ST_Y(b.current_location) ELSE NULL END AS bus_lat,
        CASE WHEN b.current_location IS NOT NULL THEN ST_X(b.current_location) ELSE NULL END AS bus_lon
    FROM fn_find_routes_to_destination(
        p_origin_lat, p_origin_lon,
        p_dest_lat, p_dest_lon,
        p_radius_meters,
        50  -- Get more routes to find buses
    ) valid_routes
    INNER JOIN Buses b ON b.route_id = valid_routes.route_id
    WHERE b.status = 'Active'
        AND b.current_location IS NOT NULL
    ORDER BY bus_distance_from_origin ASC NULLS LAST
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- ============================================================================
-- GET STOP BY ID WITH COORDINATES
-- ============================================================================

-- Function: fn_get_stop_by_id
-- Description: Returns stop by ID with extracted coordinates
-- Parameters:
--   p_stop_id: Stop ID
-- Returns: TABLE with stop information and extracted coordinates
-- Usage: SELECT * FROM fn_get_stop_by_id(1);
CREATE OR REPLACE FUNCTION fn_get_stop_by_id(p_stop_id INT)
RETURNS TABLE (
    id INT,
    name VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        ST_Y(s.location) AS latitude,
        ST_X(s.location) AS longitude
    FROM Stops s
    WHERE s.id = p_stop_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ALL STOPS WITH COORDINATES
-- ============================================================================

-- Function: fn_get_all_stops
-- Description: Returns all stops with extracted coordinates
-- Returns: TABLE with stop information and extracted coordinates
-- Usage: SELECT * FROM fn_get_all_stops();
CREATE OR REPLACE FUNCTION fn_get_all_stops()
RETURNS TABLE (
    id INT,
    name VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        ST_Y(s.location) AS latitude,
        ST_X(s.location) AS longitude
    FROM Stops s
    ORDER BY s.name;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- Create a route:
-- SELECT fn_create_route('Route 1', '[[10.8231,106.6297],[10.8241,106.6307],[10.8251,106.6317]]'::jsonb);

-- Update route geometry:
-- SELECT fn_update_route_geometry(1, '[[10.8231,106.6297],[10.8241,106.6307]]'::jsonb);

-- Create a stop:
-- SELECT fn_create_stop('Ben Thanh Market', 10.7723, 106.6981);

-- Add stop to route:
-- SELECT fn_add_stop_to_route(1, 1, 1);

-- Remove stop from route:
-- SELECT fn_remove_stop_from_route(1, 1);

-- Reorder stops:
-- SELECT fn_reorder_route_stops(1, '[{"stop_id":1,"sequence":2},{"stop_id":2,"sequence":1}]'::jsonb);

-- Get route length:
-- SELECT fn_get_route_length(1);

-- Find nearest stops:
-- SELECT * FROM fn_find_nearest_stops(10.8231, 106.6297, 1000, 5);

-- Find routes near location:
-- SELECT * FROM fn_find_routes_near_location(10.8231, 106.6297, 500);

-- Check if point is on route:
-- SELECT fn_is_point_on_route(1, 10.8231, 106.6297, 100);

-- Get stops on route:
-- SELECT * FROM fn_get_stops_on_route(1);

-- Get all routes:
-- SELECT * FROM fn_get_all_routes();

-- Get route as GeoJSON:
-- SELECT fn_get_route_geojson(1);
