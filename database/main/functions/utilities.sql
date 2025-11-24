-- ============================================================================
-- UTILITIES.SQL - Cross-domain utility functions
-- ============================================================================
-- Description: Helper functions for validation, conversion, and utilities
--              used across multiple domains in the manBus system
-- ============================================================================

-- ============================================================================
-- COORDINATE VALIDATION
-- ============================================================================

-- Function: fn_validate_coordinates
-- Description: Validates latitude and longitude are within valid WGS84 ranges
-- Parameters:
--   lat: Latitude value to validate
--   lon: Longitude value to validate
-- Returns: BOOLEAN - TRUE if valid, FALSE otherwise
-- Usage: SELECT fn_validate_coordinates(10.8231, 106.6297);
CREATE OR REPLACE FUNCTION fn_validate_coordinates(lat DOUBLE PRECISION, lon DOUBLE PRECISION)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN lat IS NOT NULL
        AND lon IS NOT NULL
        AND lat BETWEEN -90 AND 90
        AND lon BETWEEN -180 AND 180;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- PHONE NUMBER VALIDATION
-- ============================================================================

-- Function: fn_validate_phone
-- Description: Validates Vietnamese phone number format (11 digits)
-- Parameters:
--   phone: Phone number string to validate
-- Returns: BOOLEAN - TRUE if valid, FALSE otherwise
-- Usage: SELECT fn_validate_phone('08412345678');
CREATE OR REPLACE FUNCTION fn_validate_phone(phone TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN phone IS NOT NULL
        AND phone ~ '^[0-9]{11}$';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- EMAIL VALIDATION
-- ============================================================================

-- Function: fn_validate_email
-- Description: Validates email address format using regex
-- Parameters:
--   email: Email address to validate
-- Returns: BOOLEAN - TRUE if valid, FALSE otherwise
-- Usage: SELECT fn_validate_email('user@example.com');
CREATE OR REPLACE FUNCTION fn_validate_email(email TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN email IS NOT NULL
        AND email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- UUID GENERATION
-- ============================================================================

-- Function: fn_generate_uuid
-- Description: Generates a UUID string for public_id fields
-- Returns: TEXT - UUID string without hyphens
-- Usage: SELECT fn_generate_uuid();
CREATE OR REPLACE FUNCTION fn_generate_uuid()
RETURNS TEXT AS $$
BEGIN
    RETURN REPLACE(gen_random_uuid()::TEXT, '-', '');
END;
$$ LANGUAGE plpgsql VOLATILE;

-- ============================================================================
-- DISTANCE CONVERSION
-- ============================================================================

-- Function: fn_meters_to_degrees
-- Description: Converts meters to degrees for spatial queries at a given latitude
-- Parameters:
--   meters: Distance in meters
--   latitude: Latitude at which to calculate (affects longitude conversion)
-- Returns: DOUBLE PRECISION - Approximate degrees
-- Note: This is an approximation. For precise calculations, use PostGIS ST_DWithin
-- Usage: SELECT fn_meters_to_degrees(1000, 10.8231);
CREATE OR REPLACE FUNCTION fn_meters_to_degrees(meters DOUBLE PRECISION, latitude DOUBLE PRECISION DEFAULT 0)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    meters_per_degree DOUBLE PRECISION := 111320; -- meters per degree at equator
    cos_lat DOUBLE PRECISION;
BEGIN
    -- Convert latitude to radians and get cosine for longitude adjustment
    cos_lat := COS(RADIANS(latitude));

    -- Return average of lat/lon degree conversion
    -- Latitude: ~111,320 meters per degree (constant)
    -- Longitude: varies by latitude (111,320 * cos(latitude))
    RETURN meters / ((meters_per_degree + (meters_per_degree * cos_lat)) / 2.0);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- POINT CREATION HELPER
-- ============================================================================

-- Function: fn_create_point
-- Description: Creates a PostGIS POINT geometry from lat/lon coordinates
-- Parameters:
--   lat: Latitude
--   lon: Longitude
-- Returns: GEOMETRY(POINT, 4326) - PostGIS point
-- Usage: SELECT fn_create_point(10.8231, 106.6297);
CREATE OR REPLACE FUNCTION fn_create_point(lat DOUBLE PRECISION, lon DOUBLE PRECISION)
RETURNS GEOMETRY(POINT, 4326) AS $$
BEGIN
    IF NOT fn_validate_coordinates(lat, lon) THEN
        RAISE EXCEPTION 'Invalid coordinates: lat=%, lon=%', lat, lon;
    END IF;

    RETURN ST_SetSRID(ST_MakePoint(lon, lat), 4326);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- LINESTRING CREATION HELPER
-- ============================================================================

-- Function: fn_create_linestring
-- Description: Creates a PostGIS LINESTRING from array of coordinate pairs
-- Parameters:
--   coordinates: Array of lat/lon pairs as TEXT in format '[[lat1,lon1],[lat2,lon2],...]'
-- Returns: GEOMETRY(LINESTRING, 4326) - PostGIS linestring
-- Usage: SELECT fn_create_linestring('[[10.8231,106.6297],[10.8241,106.6307]]');
CREATE OR REPLACE FUNCTION fn_create_linestring(coordinates JSONB)
RETURNS GEOMETRY(LINESTRING, 4326) AS $$
DECLARE
    point_array GEOMETRY[];
    coord JSONB;
    lat DOUBLE PRECISION;
    lon DOUBLE PRECISION;
BEGIN
    -- Validate minimum 2 points
    IF jsonb_array_length(coordinates) < 2 THEN
        RAISE EXCEPTION 'LineString requires at least 2 points';
    END IF;

    -- Build array of points
    FOR coord IN SELECT * FROM jsonb_array_elements(coordinates)
    LOOP
        lat := (coord->>0)::DOUBLE PRECISION;
        lon := (coord->>1)::DOUBLE PRECISION;

        IF NOT fn_validate_coordinates(lat, lon) THEN
            RAISE EXCEPTION 'Invalid coordinates in array: lat=%, lon=%', lat, lon;
        END IF;

        point_array := array_append(point_array, ST_MakePoint(lon, lat));
    END LOOP;

    RETURN ST_SetSRID(ST_MakeLine(point_array), 4326);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- DISTANCE CALCULATION
-- ============================================================================

-- Function: fn_calculate_distance
-- Description: Calculates distance in meters between two lat/lon points
-- Parameters:
--   lat1, lon1: First point coordinates
--   lat2, lon2: Second point coordinates
-- Returns: DOUBLE PRECISION - Distance in meters
-- Usage: SELECT fn_calculate_distance(10.8231, 106.6297, 10.8241, 106.6307);
CREATE OR REPLACE FUNCTION fn_calculate_distance(
    lat1 DOUBLE PRECISION,
    lon1 DOUBLE PRECISION,
    lat2 DOUBLE PRECISION,
    lon2 DOUBLE PRECISION
)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    point1 GEOMETRY;
    point2 GEOMETRY;
BEGIN
    point1 := fn_create_point(lat1, lon1);
    point2 := fn_create_point(lat2, lon2);

    -- ST_Distance returns degrees, ST_DistanceSphere returns meters
    RETURN ST_DistanceSphere(point1, point2);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- SELECT fn_validate_coordinates(10.8231, 106.6297);  -- Returns TRUE
-- SELECT fn_validate_coordinates(91, 106.6297);       -- Returns FALSE
-- SELECT fn_validate_phone('08412345678');            -- Returns TRUE
-- SELECT fn_validate_email('test@example.com');       -- Returns TRUE
-- SELECT fn_generate_uuid();                          -- Returns UUID string
-- SELECT fn_meters_to_degrees(1000, 10.8231);         -- Returns ~0.009
-- SELECT fn_create_point(10.8231, 106.6297);          -- Returns PostGIS POINT
-- SELECT fn_calculate_distance(10.8231, 106.6297, 10.8241, 106.6307); -- Returns distance in meters
