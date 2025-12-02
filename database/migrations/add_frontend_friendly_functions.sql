-- ============================================================================
-- Migration: Add Frontend-Friendly SQL Functions
-- Description: Add functions that return GeoJSON for routes and extracted
--              coordinates for stops, making data frontend-ready
-- Date: 2025-01-30
-- ============================================================================

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
-- VERIFICATION QUERIES
-- ============================================================================

-- Test the new functions:
-- SELECT * FROM fn_get_route_by_id(1);
-- SELECT * FROM fn_get_route_by_name('Route 1');
-- SELECT * FROM fn_get_stop_by_id(1);
-- SELECT * FROM fn_get_all_stops();
