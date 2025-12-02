-- ============================================================================
-- MIGRATION: Add Bus Position Tracking Columns
-- ============================================================================
-- Description: Safely adds route_progress, direction, and last_updated columns
--              to existing Buses table without losing data
-- Date: 2025-11-28
-- Dependencies: Buses table, Routes table, PostGIS extension
-- ============================================================================

-- ============================================================================
-- BACKUP REMINDER
-- ============================================================================
-- IMPORTANT: Before running this migration, backup your database!
-- Command: pg_dump -U <user> -d manBusDB -F c -f manBusDB_backup_$(date +%Y%m%d).dump

-- ============================================================================
-- STEP 1: ADD NEW COLUMNS TO BUSES TABLE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=== STEP 1: Adding new columns to Buses table ===';

    -- Add route_progress column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'buses' AND column_name = 'route_progress'
    ) THEN
        ALTER TABLE Buses ADD COLUMN route_progress DOUBLE PRECISION DEFAULT 0.0;
        RAISE NOTICE 'Added route_progress column';
    ELSE
        RAISE NOTICE 'route_progress column already exists, skipping';
    END IF;

    -- Add direction column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'buses' AND column_name = 'direction'
    ) THEN
        ALTER TABLE Buses ADD COLUMN direction INT DEFAULT 1;
        RAISE NOTICE 'Added direction column';
    ELSE
        RAISE NOTICE 'direction column already exists, skipping';
    END IF;

    -- Add last_updated column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'buses' AND column_name = 'last_updated'
    ) THEN
        ALTER TABLE Buses ADD COLUMN last_updated TIMESTAMP DEFAULT NOW();
        RAISE NOTICE 'Added last_updated column';
    ELSE
        RAISE NOTICE 'last_updated column already exists, skipping';
    END IF;
END $$;

-- ============================================================================
-- STEP 2: CALCULATE CORRECT ROUTE_PROGRESS FOR EXISTING BUSES
-- ============================================================================

DO $$
DECLARE
    v_updated_count INT := 0;
    v_null_location_count INT := 0;
    v_null_route_geom_count INT := 0;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== STEP 2: Calculating route_progress for existing buses ===';

    -- Update route_progress for buses with valid locations and routes
    UPDATE Buses b
    SET route_progress = ST_LineLocatePoint(r.route_geom, b.current_location),
        last_updated = NOW()
    FROM Routes r
    WHERE b.route_id = r.id
      AND b.current_location IS NOT NULL
      AND r.route_geom IS NOT NULL;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;
    RAISE NOTICE 'Calculated route_progress for % buses', v_updated_count;

    -- Count buses with NULL locations
    SELECT COUNT(*) INTO v_null_location_count
    FROM Buses
    WHERE current_location IS NULL;

    IF v_null_location_count > 0 THEN
        RAISE NOTICE '% buses have NULL current_location (will be initialized by fn_initialize_bus_positions)', v_null_location_count;
    END IF;

    -- Count buses on routes with no geometry
    SELECT COUNT(*) INTO v_null_route_geom_count
    FROM Buses b
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE r.route_geom IS NULL;

    IF v_null_route_geom_count > 0 THEN
        RAISE NOTICE '% buses are on routes with NULL geometry', v_null_route_geom_count;
    END IF;
END $$;

-- ============================================================================
-- STEP 3: UPDATE fn_update_bus_location() TO HANDLE NEW COLUMNS
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== STEP 3: Updating fn_update_bus_location() function ===';
END $$;

CREATE OR REPLACE FUNCTION fn_update_bus_location(
    p_bus_id INT,
    p_lat DOUBLE PRECISION,
    p_lon DOUBLE PRECISION
)
RETURNS BOOLEAN AS $$
DECLARE
    bus_exists BOOLEAN;
    v_location GEOMETRY(POINT, 4326);
    v_route_id INT;
    v_route_geom GEOMETRY;
    v_route_progress DOUBLE PRECISION;
BEGIN
    -- Check if bus exists
    SELECT EXISTS(SELECT 1 FROM Buses WHERE bus_id = p_bus_id) INTO bus_exists;
    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Create point geometry
    v_location := fn_create_point(p_lat, p_lon);

    -- Get bus route information
    SELECT route_id INTO v_route_id
    FROM Buses
    WHERE bus_id = p_bus_id;

    -- Get route geometry and calculate progress
    SELECT route_geom INTO v_route_geom
    FROM Routes
    WHERE id = v_route_id;

    -- Calculate route progress if route has geometry
    IF v_route_geom IS NOT NULL THEN
        v_route_progress := ST_LineLocatePoint(v_route_geom, v_location);
    ELSE
        v_route_progress := 0.0;
    END IF;

    -- Update bus location with tracking information
    UPDATE Buses
    SET current_location = v_location,
        route_progress = v_route_progress,
        last_updated = NOW()
    WHERE bus_id = p_bus_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    RAISE NOTICE 'Updated fn_update_bus_location() to maintain route_progress and last_updated';
END $$;

-- ============================================================================
-- STEP 4: UPDATE fn_assign_bus_to_route() TO RESET TRACKING
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== STEP 4: Updating fn_assign_bus_to_route() function ===';
END $$;

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

    -- Assign bus to route and reset tracking information
    UPDATE Buses
    SET route_id = p_route_id,
        current_location = NULL,    -- Force re-initialization
        route_progress = 0.0,        -- Reset to start
        direction = 1,                -- Reset to forward
        last_updated = NOW()
    WHERE bus_id = p_bus_id;

    RAISE NOTICE 'Bus % assigned to route % (position reset for re-initialization)', p_bus_id, p_route_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    RAISE NOTICE 'Updated fn_assign_bus_to_route() to reset tracking on route change';
END $$;

-- ============================================================================
-- STEP 5: VALIDATION
-- ============================================================================

DO $$
DECLARE
    v_total_buses INT;
    v_buses_with_progress INT;
    v_buses_ready_for_auto_update INT;
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== STEP 5: Validation ===';

    -- Count total buses
    SELECT COUNT(*) INTO v_total_buses FROM Buses;
    RAISE NOTICE 'Total buses in system: %', v_total_buses;

    -- Count buses with calculated route_progress
    SELECT COUNT(*) INTO v_buses_with_progress
    FROM Buses
    WHERE route_progress IS NOT NULL;
    RAISE NOTICE 'Buses with route_progress: %', v_buses_with_progress;

    -- Count buses ready for auto-update (Active with location and progress)
    SELECT COUNT(*) INTO v_buses_ready_for_auto_update
    FROM Buses
    WHERE status = 'Active'
      AND current_location IS NOT NULL
      AND route_progress IS NOT NULL;
    RAISE NOTICE 'Buses ready for auto-update: %', v_buses_ready_for_auto_update;

    -- Check column existence
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'buses'
        AND column_name IN ('route_progress', 'direction', 'last_updated')
        GROUP BY table_name
        HAVING COUNT(*) = 3
    ) THEN
        RAISE NOTICE 'All new columns exist';
    ELSE
        RAISE EXCEPTION 'Migration incomplete - not all columns were added';
    END IF;
END $$;

-- ============================================================================
-- STEP 6: SUMMARY AND NEXT STEPS
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=== MIGRATION COMPLETE ===';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Run: SELECT fn_initialize_bus_positions();';
    RAISE NOTICE '   This will set initial positions for buses with NULL locations';
    RAISE NOTICE '';
    RAISE NOTICE '2. Test auto-update manually:';
    RAISE NOTICE '   SELECT * FROM fn_update_bus_positions_auto(10.0, 30);';
    RAISE NOTICE '';
    RAISE NOTICE '3. Verify bus positions:';
    RAISE NOTICE '   SELECT bus_id, plate_number, route_progress, direction, last_updated';
    RAISE NOTICE '   FROM Buses WHERE status = ''Active'';';
    RAISE NOTICE '';
    RAISE NOTICE '4. If everything looks good, enable the cron job:';
    RAISE NOTICE '   \i /mnt/d/killer/killer/projects/manBus/database/main/cron_jobs.sql';
END $$;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to check migration success)
-- ============================================================================

-- View all buses with new tracking information
-- SELECT
--     bus_id,
--     plate_number,
--     name,
--     status,
--     route_progress,
--     direction,
--     last_updated,
--     CASE
--         WHEN current_location IS NOT NULL THEN 'Has location'
--         ELSE 'Needs initialization'
--     END AS location_status
-- FROM Buses
-- ORDER BY bus_id;

-- Check buses that need initialization
-- SELECT bus_id, plate_number, name, status
-- FROM Buses
-- WHERE current_location IS NULL OR route_progress IS NULL;

-- Test the updated functions
-- SELECT fn_update_bus_location(1, 21.0285, 105.8542);
-- SELECT fn_assign_bus_to_route(1, 2);

-- ============================================================================
-- ROLLBACK SCRIPT (Use if you need to undo this migration)
-- ============================================================================

-- WARNING: This will remove the new columns and restore old function versions
-- Only use if absolutely necessary!

/*
-- Remove new columns
ALTER TABLE Buses DROP COLUMN IF EXISTS route_progress;
ALTER TABLE Buses DROP COLUMN IF EXISTS direction;
ALTER TABLE Buses DROP COLUMN IF EXISTS last_updated;

-- Restore old fn_update_bus_location (without tracking)
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
    SELECT EXISTS(SELECT 1 FROM Buses WHERE bus_id = p_bus_id) INTO bus_exists;
    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    v_location := fn_create_point(p_lat, p_lon);

    UPDATE Buses
    SET current_location = v_location
    WHERE bus_id = p_bus_id;

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Restore old fn_assign_bus_to_route (without reset)
CREATE OR REPLACE FUNCTION fn_assign_bus_to_route(
    p_bus_id INT,
    p_route_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    bus_exists BOOLEAN;
    route_exists BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM Buses WHERE bus_id = p_bus_id) INTO bus_exists;
    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    SELECT EXISTS(SELECT 1 FROM Routes WHERE id = p_route_id) INTO route_exists;
    IF NOT route_exists THEN
        RAISE EXCEPTION 'Route with ID % does not exist', p_route_id;
    END IF;

    UPDATE Buses
    SET route_id = p_route_id
    WHERE bus_id = p_bus_id;

    RAISE NOTICE 'Bus % assigned to route %', p_bus_id, p_route_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
