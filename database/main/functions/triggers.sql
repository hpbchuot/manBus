-- ============================================================================
-- TRIGGERS.SQL - Database Triggers
-- ============================================================================
-- Description: Automatic triggers for timestamp management, validation, and
--              business logic enforcement
-- Dependencies: tables.sql, functions/utilities.sql
-- ============================================================================

-- ============================================================================
-- TIMESTAMP TRIGGERS
-- ============================================================================

-- Generic trigger function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION trg_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to Users table
DROP TRIGGER IF EXISTS trg_users_update_timestamp ON Users;
CREATE TRIGGER trg_users_update_timestamp
    BEFORE UPDATE ON Users
    FOR EACH ROW
    EXECUTE FUNCTION trg_update_timestamp();

-- Apply to Routes table
DROP TRIGGER IF EXISTS trg_routes_update_timestamp ON Routes;
CREATE TRIGGER trg_routes_update_timestamp
    BEFORE UPDATE ON Routes
    FOR EACH ROW
    EXECUTE FUNCTION trg_update_timestamp();

-- Apply to Feedback table
DROP TRIGGER IF EXISTS trg_feedback_update_timestamp ON Feedback;
CREATE TRIGGER trg_feedback_update_timestamp
    BEFORE UPDATE ON Feedback
    FOR EACH ROW
    EXECUTE FUNCTION trg_update_timestamp();

-- ============================================================================
-- USER TRIGGERS
-- ============================================================================

-- Auto-generate public_id for new users
CREATE OR REPLACE FUNCTION trg_users_generate_public_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.public_id IS NULL THEN
        NEW.public_id = fn_generate_uuid();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_before_insert_public_id ON Users;
CREATE TRIGGER trg_users_before_insert_public_id
    BEFORE INSERT ON Users
    FOR EACH ROW
    EXECUTE FUNCTION trg_users_generate_public_id();

-- Prevent modification of deleted users (except restore)
CREATE OR REPLACE FUNCTION trg_users_prevent_deleted_modification()
RETURNS TRIGGER AS $$
BEGIN
    -- Allow restoration (is_deleted changing from TRUE to FALSE)
    IF OLD.is_deleted = TRUE AND NEW.is_deleted = FALSE THEN
        RETURN NEW;
    END IF;

    -- Prevent other modifications to deleted users
    IF OLD.is_deleted = TRUE AND NEW.is_deleted = TRUE THEN
        RAISE EXCEPTION 'Cannot modify deleted user. Restore user first.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_prevent_deleted_modification ON Users;
CREATE TRIGGER trg_users_prevent_deleted_modification
    BEFORE UPDATE ON Users
    FOR EACH ROW
    EXECUTE FUNCTION trg_users_prevent_deleted_modification();

-- ============================================================================
-- BUS TRIGGERS
-- ============================================================================

-- Validate bus status values
CREATE OR REPLACE FUNCTION trg_buses_validate_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status NOT IN ('Active', 'Inactive', 'Maintenance', 'Retired') THEN
        RAISE EXCEPTION 'Invalid bus status: %. Must be one of: Active, Inactive, Maintenance, Retired', NEW.status;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_buses_validate_status ON Buses;
CREATE TRIGGER trg_buses_validate_status
    BEFORE INSERT OR UPDATE ON Buses
    FOR EACH ROW
    EXECUTE FUNCTION trg_buses_validate_status();

-- Validate bus location coordinates
CREATE OR REPLACE FUNCTION trg_buses_validate_location()
RETURNS TRIGGER AS $$
DECLARE
    lat DOUBLE PRECISION;
    lon DOUBLE PRECISION;
BEGIN
    IF NEW.current_location IS NOT NULL THEN
        lat := ST_Y(NEW.current_location);
        lon := ST_X(NEW.current_location);

        IF NOT fn_validate_coordinates(lat, lon) THEN
            RAISE EXCEPTION 'Invalid bus location coordinates: lat=%, lon=%', lat, lon;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_buses_validate_location ON Buses;
CREATE TRIGGER trg_buses_validate_location
    BEFORE INSERT OR UPDATE ON Buses
    FOR EACH ROW
    EXECUTE FUNCTION trg_buses_validate_location();

-- ============================================================================
-- DRIVER TRIGGERS
-- ============================================================================

-- Validate driver status values
CREATE OR REPLACE FUNCTION trg_drivers_validate_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status NOT IN ('Active', 'Inactive', 'Suspended') THEN
        RAISE EXCEPTION 'Invalid driver status: %. Must be one of: Active, Inactive, Suspended', NEW.status;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_drivers_validate_status ON Drivers;
CREATE TRIGGER trg_drivers_validate_status
    BEFORE INSERT OR UPDATE ON Drivers
    FOR EACH ROW
    EXECUTE FUNCTION trg_drivers_validate_status();

-- Prevent assigning deleted users as drivers
CREATE OR REPLACE FUNCTION trg_drivers_check_user_deleted()
RETURNS TRIGGER AS $$
DECLARE
    user_deleted BOOLEAN;
BEGIN
    SELECT is_deleted INTO user_deleted
    FROM Users
    WHERE id = NEW.user_id;

    IF user_deleted THEN
        RAISE EXCEPTION 'Cannot assign deleted user (ID: %) as driver', NEW.user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_drivers_check_user_deleted ON Drivers;
CREATE TRIGGER trg_drivers_check_user_deleted
    BEFORE INSERT OR UPDATE ON Drivers
    FOR EACH ROW
    EXECUTE FUNCTION trg_drivers_check_user_deleted();

-- ============================================================================
-- FEEDBACK TRIGGERS
-- ============================================================================

-- Validate feedback status values
CREATE OR REPLACE FUNCTION trg_feedback_validate_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status NOT IN ('Pending', 'In Review', 'Resolved', 'Rejected') THEN
        RAISE EXCEPTION 'Invalid feedback status: %. Must be one of: Pending, In Review, Resolved, Rejected', NEW.status;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_feedback_validate_status ON Feedback;
CREATE TRIGGER trg_feedback_validate_status
    BEFORE INSERT OR UPDATE ON Feedback
    FOR EACH ROW
    EXECUTE FUNCTION trg_feedback_validate_status();

-- Prevent feedback from deleted users
CREATE OR REPLACE FUNCTION trg_feedback_check_user_deleted()
RETURNS TRIGGER AS $$
DECLARE
    user_deleted BOOLEAN;
BEGIN
    SELECT is_deleted INTO user_deleted
    FROM Users
    WHERE id = NEW.user_id;

    IF user_deleted THEN
        RAISE EXCEPTION 'Cannot create feedback for deleted user (ID: %)', NEW.user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_feedback_check_user_deleted ON Feedback;
CREATE TRIGGER trg_feedback_check_user_deleted
    BEFORE INSERT ON Feedback
    FOR EACH ROW
    EXECUTE FUNCTION trg_feedback_check_user_deleted();

-- ============================================================================
-- ROUTE & STOP TRIGGERS
-- ============================================================================

-- Validate stop location coordinates
CREATE OR REPLACE FUNCTION trg_stops_validate_location()
RETURNS TRIGGER AS $$
DECLARE
    lat DOUBLE PRECISION;
    lon DOUBLE PRECISION;
BEGIN
    lat := ST_Y(NEW.location);
    lon := ST_X(NEW.location);

    IF NOT fn_validate_coordinates(lat, lon) THEN
        RAISE EXCEPTION 'Invalid stop location coordinates: lat=%, lon=%', lat, lon;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stops_validate_location ON Stops;
CREATE TRIGGER trg_stops_validate_location
    BEFORE INSERT OR UPDATE ON Stops
    FOR EACH ROW
    EXECUTE FUNCTION trg_stops_validate_location();

-- Validate route geometry
CREATE OR REPLACE FUNCTION trg_routes_validate_geometry()
RETURNS TRIGGER AS $$
DECLARE
    num_points INT;
BEGIN
    IF NEW.route_geom IS NOT NULL THEN
        num_points := ST_NPoints(NEW.route_geom);

        IF num_points < 2 THEN
            RAISE EXCEPTION 'Route geometry must have at least 2 points, got %', num_points;
        END IF;

        -- Validate that all coordinates are within valid ranges
        IF NOT ST_IsValid(NEW.route_geom) THEN
            RAISE EXCEPTION 'Route geometry is invalid';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_routes_validate_geometry ON Routes;
CREATE TRIGGER trg_routes_validate_geometry
    BEFORE INSERT OR UPDATE ON Routes
    FOR EACH ROW
    EXECUTE FUNCTION trg_routes_validate_geometry();

-- ============================================================================
-- NOTIFICATION TRIGGERS
-- ============================================================================

-- Prevent notifications to deleted users
CREATE OR REPLACE FUNCTION trg_notifications_check_user_deleted()
RETURNS TRIGGER AS $$
DECLARE
    user_deleted BOOLEAN;
BEGIN
    IF NEW.user_id IS NOT NULL THEN
        SELECT is_deleted INTO user_deleted
        FROM Users
        WHERE id = NEW.user_id;

        IF user_deleted THEN
            RAISE EXCEPTION 'Cannot create notification for deleted user (ID: %)', NEW.user_id;
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_notifications_check_user_deleted ON Notifications;
CREATE TRIGGER trg_notifications_check_user_deleted
    BEFORE INSERT ON Notifications
    FOR EACH ROW
    EXECUTE FUNCTION trg_notifications_check_user_deleted();

-- ============================================================================
-- SOFT DELETE CASCADE TRIGGERS
-- ============================================================================

-- When user is soft deleted, cascade to related records
CREATE OR REPLACE FUNCTION trg_users_soft_delete_cascade()
RETURNS TRIGGER AS $$
BEGIN
    -- Only trigger if is_deleted is changing from FALSE to TRUE
    IF OLD.is_deleted = FALSE AND NEW.is_deleted = TRUE THEN
        -- Set driver to inactive if user is a driver
        UPDATE Drivers
        SET status = 'Inactive'
        WHERE user_id = NEW.id AND status = 'Active';

        RAISE NOTICE 'User % soft deleted. Related driver set to Inactive.', NEW.id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_soft_delete_cascade ON Users;
CREATE TRIGGER trg_users_soft_delete_cascade
    AFTER UPDATE ON Users
    FOR EACH ROW
    EXECUTE FUNCTION trg_users_soft_delete_cascade();

-- ============================================================================
-- AUDIT/LOGGING TRIGGERS (Optional - commented out by default)
-- ============================================================================

-- Uncomment these if you want to add audit logging

/*
-- Create audit log table (run this first if enabling audit)
CREATE TABLE IF NOT EXISTS AuditLog (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    record_id INT NOT NULL,
    user_id INT,
    changed_at TIMESTAMP DEFAULT NOW(),
    old_data JSONB,
    new_data JSONB
);

-- Generic audit trigger function
CREATE OR REPLACE FUNCTION trg_audit_log()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO AuditLog (table_name, operation, record_id, changed_at, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, OLD.id, NOW(), row_to_json(OLD)::jsonb);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO AuditLog (table_name, operation, record_id, changed_at, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id, NOW(), row_to_json(OLD)::jsonb, row_to_json(NEW)::jsonb);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO AuditLog (table_name, operation, record_id, changed_at, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id, NOW(), row_to_json(NEW)::jsonb);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to critical tables
CREATE TRIGGER trg_users_audit
    AFTER INSERT OR UPDATE OR DELETE ON Users
    FOR EACH ROW EXECUTE FUNCTION trg_audit_log();

CREATE TRIGGER trg_buses_audit
    AFTER INSERT OR UPDATE OR DELETE ON Buses
    FOR EACH ROW EXECUTE FUNCTION trg_audit_log();

CREATE TRIGGER trg_drivers_audit
    AFTER INSERT OR UPDATE OR DELETE ON Drivers
    FOR EACH ROW EXECUTE FUNCTION trg_audit_log();

CREATE TRIGGER trg_feedback_audit
    AFTER INSERT OR UPDATE OR DELETE ON Feedback
    FOR EACH ROW EXECUTE FUNCTION trg_audit_log();
*/

-- ============================================================================
-- SUMMARY OF TRIGGERS
-- ============================================================================

-- Active Triggers:
-- 1. Auto-update timestamps (Users, Routes, Feedback)
-- 2. Auto-generate public_id for Users
-- 3. Prevent modification of deleted users
-- 4. Validate bus status and location
-- 5. Validate driver status and check user not deleted
-- 6. Validate feedback status and check user not deleted
-- 7. Validate stop and route geometries
-- 8. Prevent notifications to deleted users
-- 9. Soft delete cascade (deactivate driver when user deleted)

-- Optional Triggers (commented out):
-- 1. Audit logging for all critical tables

-- To view all triggers:
-- SELECT trigger_name, event_manipulation, event_object_table
-- FROM information_schema.triggers
-- WHERE trigger_schema = 'public'
-- ORDER BY event_object_table, trigger_name;
