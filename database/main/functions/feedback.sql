-- ============================================================================
-- FEEDBACK.SQL - Feedback Management Functions
-- ============================================================================
-- Description: Functions for managing user feedback and complaints about buses
-- Dependencies: Feedback, Users, Buses tables
-- ============================================================================

-- ============================================================================
-- FEEDBACK CREATION
-- ============================================================================

-- Function: fn_create_feedback
-- Description: Creates a new feedback entry
-- Parameters:
--   p_user_id: User ID submitting feedback
--   p_bus_id: Bus ID the feedback is about
--   p_content: Feedback content/message
-- Returns: INT - New feedback ID
-- Usage: SELECT fn_create_feedback(1, 1, 'Bus was overcrowded during rush hour');
CREATE OR REPLACE FUNCTION fn_create_feedback(
    p_user_id INT,
    p_bus_id INT,
    p_content TEXT
)
RETURNS INT AS $$
DECLARE
    new_feedback_id INT;
    user_exists BOOLEAN;
    bus_exists BOOLEAN;
BEGIN
    -- Validate content
    IF p_content IS NULL OR LENGTH(TRIM(p_content)) = 0 THEN
        RAISE EXCEPTION 'Feedback content cannot be empty';
    END IF;

    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ) INTO user_exists;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Check if bus exists
    SELECT EXISTS(
        SELECT 1 FROM Buses WHERE bus_id = p_bus_id
    ) INTO bus_exists;

    IF NOT bus_exists THEN
        RAISE EXCEPTION 'Bus with ID % does not exist', p_bus_id;
    END IF;

    -- Insert feedback
    INSERT INTO Feedback (user_id, bus_id, content, status, created_at, updated_at)
    VALUES (p_user_id, p_bus_id, TRIM(p_content), 'Pending', NOW(), NOW())
    RETURNING id INTO new_feedback_id;

    RAISE NOTICE 'Feedback created successfully with ID: %', new_feedback_id;
    RETURN new_feedback_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FEEDBACK STATUS UPDATE
-- ============================================================================

-- Function: fn_update_feedback_status
-- Description: Updates feedback status with automatic timestamp update
-- Parameters:
--   p_feedback_id: Feedback ID to update
--   p_new_status: New status (Pending, In Review, Resolved, Rejected)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_feedback_status(1, 'In Review');
CREATE OR REPLACE FUNCTION fn_update_feedback_status(
    p_feedback_id INT,
    p_new_status VARCHAR(20)
)
RETURNS BOOLEAN AS $$
DECLARE
    feedback_exists BOOLEAN;
BEGIN
    -- Validate status
    IF p_new_status NOT IN ('Pending', 'In Review', 'Resolved', 'Rejected') THEN
        RAISE EXCEPTION 'Invalid status. Must be one of: Pending, In Review, Resolved, Rejected';
    END IF;

    -- Check if feedback exists
    SELECT EXISTS(
        SELECT 1 FROM Feedback WHERE id = p_feedback_id
    ) INTO feedback_exists;

    IF NOT feedback_exists THEN
        RAISE EXCEPTION 'Feedback with ID % does not exist', p_feedback_id;
    END IF;

    -- Update status and timestamp
    UPDATE Feedback
    SET
        status = p_new_status,
        updated_at = NOW()
    WHERE id = p_feedback_id;

    RAISE NOTICE 'Feedback % status updated to %', p_feedback_id, p_new_status;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET PENDING FEEDBACK
-- ============================================================================

-- Function: fn_get_pending_feedback
-- Description: Retrieves all pending feedback
-- Returns: TABLE with feedback information
-- Usage: SELECT * FROM fn_get_pending_feedback();
CREATE OR REPLACE FUNCTION fn_get_pending_feedback()
RETURNS TABLE (
    feedback_id INT,
    content TEXT,
    created_at TIMESTAMP,
    user_id INT,
    user_name VARCHAR(100),
    user_email VARCHAR(255),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.content,
        f.created_at,
        f.user_id,
        u.name AS user_name,
        u.email AS user_email,
        f.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        r.name AS route_name
    FROM Feedback f
    INNER JOIN Users u ON f.user_id = u.id
    INNER JOIN Buses b ON f.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE f.status = 'Pending'
    ORDER BY f.created_at ASC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET FEEDBACK BY BUS
-- ============================================================================

-- Function: fn_get_feedback_by_bus
-- Description: Retrieves all feedback for a specific bus
-- Parameters:
--   p_bus_id: Bus ID
--   p_status: Optional status filter (NULL for all)
-- Returns: TABLE with feedback information
-- Usage: SELECT * FROM fn_get_feedback_by_bus(1, NULL);
CREATE OR REPLACE FUNCTION fn_get_feedback_by_bus(
    p_bus_id INT,
    p_status VARCHAR(20) DEFAULT NULL
)
RETURNS TABLE (
    feedback_id INT,
    content TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    user_id INT,
    user_name VARCHAR(100),
    user_email VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.content,
        f.status,
        f.created_at,
        f.updated_at,
        f.user_id,
        u.name AS user_name,
        u.email AS user_email
    FROM Feedback f
    INNER JOIN Users u ON f.user_id = u.id
    WHERE f.bus_id = p_bus_id
        AND (p_status IS NULL OR f.status = p_status)
    ORDER BY f.created_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET FEEDBACK BY USER
-- ============================================================================

-- Function: fn_get_feedback_by_user
-- Description: Retrieves all feedback submitted by a specific user
-- Parameters:
--   p_user_id: User ID
--   p_status: Optional status filter (NULL for all)
-- Returns: TABLE with feedback information
-- Usage: SELECT * FROM fn_get_feedback_by_user(1, NULL);
CREATE OR REPLACE FUNCTION fn_get_feedback_by_user(
    p_user_id INT,
    p_status VARCHAR(20) DEFAULT NULL
)
RETURNS TABLE (
    feedback_id INT,
    content TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.content,
        f.status,
        f.created_at,
        f.updated_at,
        f.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        r.name AS route_name
    FROM Feedback f
    INNER JOIN Buses b ON f.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE f.user_id = p_user_id
        AND (p_status IS NULL OR f.status = p_status)
    ORDER BY f.created_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET FEEDBACK STATS
-- ============================================================================

-- Function: fn_get_feedback_stats
-- Description: Returns feedback statistics
-- Returns: TABLE with feedback counts by status
-- Usage: SELECT * FROM fn_get_feedback_stats();
CREATE OR REPLACE FUNCTION fn_get_feedback_stats()
RETURNS TABLE (
    status VARCHAR(20),
    count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.status,
        COUNT(*) AS count
    FROM Feedback f
    GROUP BY f.status
    ORDER BY
        CASE f.status
            WHEN 'Pending' THEN 1
            WHEN 'In Review' THEN 2
            WHEN 'Resolved' THEN 3
            WHEN 'Rejected' THEN 4
        END;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ALL FEEDBACK
-- ============================================================================

-- Function: fn_get_all_feedback
-- Description: Retrieves all feedback with optional filtering
-- Parameters:
--   p_status: Optional status filter (NULL for all)
--   p_limit: Maximum number of results (default 100)
--   p_offset: Offset for pagination (default 0)
-- Returns: TABLE with feedback information
-- Usage: SELECT * FROM fn_get_all_feedback(NULL, 50, 0);
CREATE OR REPLACE FUNCTION fn_get_all_feedback(
    p_status VARCHAR(20) DEFAULT NULL,
    p_limit INT DEFAULT 100,
    p_offset INT DEFAULT 0
)
RETURNS TABLE (
    feedback_id INT,
    content TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    user_id INT,
    user_name VARCHAR(100),
    user_email VARCHAR(255),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.content,
        f.status,
        f.created_at,
        f.updated_at,
        f.user_id,
        u.name AS user_name,
        u.email AS user_email,
        f.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number,
        r.name AS route_name
    FROM Feedback f
    INNER JOIN Users u ON f.user_id = u.id
    INNER JOIN Buses b ON f.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE p_status IS NULL OR f.status = p_status
    ORDER BY
        CASE
            WHEN f.status = 'Pending' THEN 1
            WHEN f.status = 'In Review' THEN 2
            WHEN f.status = 'Resolved' THEN 3
            WHEN f.status = 'Rejected' THEN 4
        END,
        f.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET FEEDBACK BY ROUTE
-- ============================================================================

-- Function: fn_get_feedback_by_route
-- Description: Retrieves all feedback for buses on a specific route
-- Parameters:
--   p_route_id: Route ID
--   p_status: Optional status filter (NULL for all)
-- Returns: TABLE with feedback information
-- Usage: SELECT * FROM fn_get_feedback_by_route(1, NULL);
CREATE OR REPLACE FUNCTION fn_get_feedback_by_route(
    p_route_id INT,
    p_status VARCHAR(20) DEFAULT NULL
)
RETURNS TABLE (
    feedback_id INT,
    content TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    user_id INT,
    user_name VARCHAR(100),
    bus_id INT,
    bus_name VARCHAR(100),
    bus_plate_number VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.content,
        f.status,
        f.created_at,
        f.updated_at,
        f.user_id,
        u.name AS user_name,
        f.bus_id,
        b.name AS bus_name,
        b.plate_number AS bus_plate_number
    FROM Feedback f
    INNER JOIN Users u ON f.user_id = u.id
    INNER JOIN Buses b ON f.bus_id = b.bus_id
    WHERE b.route_id = p_route_id
        AND (p_status IS NULL OR f.status = p_status)
    ORDER BY f.created_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- UPDATE FEEDBACK CONTENT
-- ============================================================================

-- Function: fn_update_feedback_content
-- Description: Updates feedback content (for user edits)
-- Parameters:
--   p_feedback_id: Feedback ID
--   p_user_id: User ID (for ownership verification)
--   p_new_content: New feedback content
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_feedback_content(1, 1, 'Updated feedback text');
CREATE OR REPLACE FUNCTION fn_update_feedback_content(
    p_feedback_id INT,
    p_user_id INT,
    p_new_content TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    feedback_exists BOOLEAN;
    feedback_status VARCHAR(20);
BEGIN
    -- Validate content
    IF p_new_content IS NULL OR LENGTH(TRIM(p_new_content)) = 0 THEN
        RAISE EXCEPTION 'Feedback content cannot be empty';
    END IF;

    -- Check if feedback exists and belongs to user
    SELECT EXISTS(
        SELECT 1 FROM Feedback WHERE id = p_feedback_id AND user_id = p_user_id
    ), status
    INTO feedback_exists, feedback_status
    FROM Feedback
    WHERE id = p_feedback_id AND user_id = p_user_id;

    IF NOT feedback_exists THEN
        RAISE EXCEPTION 'Feedback with ID % does not exist or does not belong to user %', p_feedback_id, p_user_id;
    END IF;

    -- Only allow editing if feedback is still pending
    IF feedback_status != 'Pending' THEN
        RAISE EXCEPTION 'Cannot edit feedback with status "%". Only pending feedback can be edited.', feedback_status;
    END IF;

    -- Update content
    UPDATE Feedback
    SET
        content = TRIM(p_new_content),
        updated_at = NOW()
    WHERE id = p_feedback_id;

    RAISE NOTICE 'Feedback % content updated', p_feedback_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DELETE FEEDBACK
-- ============================================================================

-- Function: fn_delete_feedback
-- Description: Deletes a feedback entry (admin only or user if pending)
-- Parameters:
--   p_feedback_id: Feedback ID
--   p_user_id: User ID (for ownership verification, NULL for admin)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_delete_feedback(1, 1);
CREATE OR REPLACE FUNCTION fn_delete_feedback(
    p_feedback_id INT,
    p_user_id INT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    deleted_count INT;
    feedback_status VARCHAR(20);
BEGIN
    IF p_user_id IS NOT NULL THEN
        -- User can only delete their own pending feedback
        SELECT status INTO feedback_status
        FROM Feedback
        WHERE id = p_feedback_id AND user_id = p_user_id;

        IF feedback_status IS NULL THEN
            RAISE EXCEPTION 'Feedback with ID % does not exist or does not belong to user %', p_feedback_id, p_user_id;
        END IF;

        IF feedback_status != 'Pending' THEN
            RAISE EXCEPTION 'Cannot delete feedback with status "%". Only pending feedback can be deleted by users.', feedback_status;
        END IF;

        DELETE FROM Feedback
        WHERE id = p_feedback_id AND user_id = p_user_id;
    ELSE
        -- Admin can delete any feedback
        DELETE FROM Feedback
        WHERE id = p_feedback_id;
    END IF;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    IF deleted_count = 0 THEN
        RETURN FALSE;
    END IF;

    RAISE NOTICE 'Feedback % deleted', p_feedback_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET RECENT FEEDBACK
-- ============================================================================

-- Function: fn_get_recent_feedback
-- Description: Gets the most recent feedback entries
-- Parameters:
--   p_days: Number of days to look back (default 7)
--   p_limit: Maximum number of results (default 50)
-- Returns: TABLE with feedback information
-- Usage: SELECT * FROM fn_get_recent_feedback(7, 50);
CREATE OR REPLACE FUNCTION fn_get_recent_feedback(
    p_days INT DEFAULT 7,
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    feedback_id INT,
    content TEXT,
    status VARCHAR(20),
    created_at TIMESTAMP,
    user_name VARCHAR(100),
    bus_plate_number VARCHAR(20),
    route_name VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.content,
        f.status,
        f.created_at,
        u.name AS user_name,
        b.plate_number AS bus_plate_number,
        r.name AS route_name
    FROM Feedback f
    INNER JOIN Users u ON f.user_id = u.id
    INNER JOIN Buses b ON f.bus_id = b.bus_id
    INNER JOIN Routes r ON b.route_id = r.id
    WHERE f.created_at >= NOW() - (p_days || ' days')::INTERVAL
    ORDER BY f.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- Create feedback:
-- SELECT fn_create_feedback(1, 1, 'Bus was overcrowded during rush hour');

-- Update feedback status:
-- SELECT fn_update_feedback_status(1, 'In Review');

-- Get pending feedback:
-- SELECT * FROM fn_get_pending_feedback();

-- Get feedback by bus:
-- SELECT * FROM fn_get_feedback_by_bus(1, NULL);

-- Get feedback by user:
-- SELECT * FROM fn_get_feedback_by_user(1, 'Pending');

-- Get feedback statistics:
-- SELECT * FROM fn_get_feedback_stats();

-- Get all feedback:
-- SELECT * FROM fn_get_all_feedback(NULL, 50, 0);

-- Get feedback by route:
-- SELECT * FROM fn_get_feedback_by_route(1, NULL);

-- Update feedback content:
-- SELECT fn_update_feedback_content(1, 1, 'Updated feedback content');

-- Delete feedback:
-- SELECT fn_delete_feedback(1, 1);

-- Get recent feedback:
-- SELECT * FROM fn_get_recent_feedback(7, 50);
