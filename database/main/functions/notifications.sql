-- ============================================================================
-- NOTIFICATIONS.SQL - Notification System Functions
-- ============================================================================
-- Description: Functions for managing user notifications
-- Dependencies: Notifications, Users tables
-- ============================================================================

-- ============================================================================
-- NOTIFICATION CREATION
-- ============================================================================

-- Function: fn_create_notification
-- Description: Creates a notification for a specific user
-- Parameters:
--   p_user_id: User ID to send notification to
--   p_message: Notification message
--   p_type: Notification type (optional)
--   p_link: Optional link/URL related to notification
-- Returns: INT - New notification ID
-- Usage: SELECT fn_create_notification(1, 'Your bus is arriving', 'bus_arrival', '/buses/1');
CREATE OR REPLACE FUNCTION fn_create_notification(
    p_user_id INT,
    p_message VARCHAR(255),
    p_type VARCHAR(50) DEFAULT NULL,
    p_link VARCHAR(255) DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    new_notification_id INT;
    user_exists BOOLEAN;
BEGIN
    -- Validate message
    IF p_message IS NULL OR LENGTH(TRIM(p_message)) = 0 THEN
        RAISE EXCEPTION 'Message cannot be empty';
    END IF;

    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ) INTO user_exists;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Insert notification
    INSERT INTO Notifications (user_id, message, type, link, read, created_at)
    VALUES (p_user_id, TRIM(p_message), p_type, p_link, FALSE, NOW())
    RETURNING id INTO new_notification_id;

    RAISE NOTICE 'Notification created successfully with ID: %', new_notification_id;
    RETURN new_notification_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MARK NOTIFICATION AS READ
-- ============================================================================

-- Function: fn_mark_notification_read
-- Description: Marks a specific notification as read
-- Parameters:
--   p_notification_id: Notification ID to mark as read
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_mark_notification_read(1);
CREATE OR REPLACE FUNCTION fn_mark_notification_read(p_notification_id INT)
RETURNS BOOLEAN AS $$
DECLARE
    notification_exists BOOLEAN;
    already_read BOOLEAN;
BEGIN
    -- Check if notification exists
    SELECT
        EXISTS(SELECT 1 FROM Notifications WHERE id = p_notification_id),
        EXISTS(SELECT 1 FROM Notifications WHERE id = p_notification_id AND read = TRUE)
    INTO notification_exists, already_read;

    IF NOT notification_exists THEN
        RAISE EXCEPTION 'Notification with ID % does not exist', p_notification_id;
    END IF;

    IF already_read THEN
        RAISE NOTICE 'Notification % is already read', p_notification_id;
        RETURN FALSE;
    END IF;

    -- Mark as read
    UPDATE Notifications
    SET read = TRUE
    WHERE id = p_notification_id;

    RAISE NOTICE 'Notification % marked as read', p_notification_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- MARK ALL NOTIFICATIONS AS READ
-- ============================================================================

-- Function: fn_mark_all_read
-- Description: Marks all unread notifications for a user as read
-- Parameters:
--   p_user_id: User ID
-- Returns: INT - Number of notifications marked as read
-- Usage: SELECT fn_mark_all_read(1);
CREATE OR REPLACE FUNCTION fn_mark_all_read(p_user_id INT)
RETURNS INT AS $$
DECLARE
    updated_count INT;
BEGIN
    UPDATE Notifications
    SET read = TRUE
    WHERE user_id = p_user_id AND read = FALSE;

    GET DIAGNOSTICS updated_count = ROW_COUNT;

    RAISE NOTICE 'Marked % notifications as read for user %', updated_count, p_user_id;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET UNREAD NOTIFICATIONS
-- ============================================================================

-- Function: fn_get_unread_notifications
-- Description: Retrieves all unread notifications for a user
-- Parameters:
--   p_user_id: User ID
-- Returns: TABLE with notification information
-- Usage: SELECT * FROM fn_get_unread_notifications(1);
CREATE OR REPLACE FUNCTION fn_get_unread_notifications(p_user_id INT)
RETURNS TABLE (
    notification_id INT,
    message VARCHAR(255),
    type VARCHAR(50),
    link VARCHAR(255),
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.id,
        n.message,
        n.type,
        n.link,
        n.created_at
    FROM Notifications n
    WHERE n.user_id = p_user_id
        AND n.read = FALSE
    ORDER BY n.created_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET RECENT NOTIFICATIONS
-- ============================================================================

-- Function: fn_get_recent_notifications
-- Description: Retrieves recent notifications (read and unread) for a user
-- Parameters:
--   p_user_id: User ID
--   p_limit: Maximum number of notifications to return (default 20)
-- Returns: TABLE with notification information
-- Usage: SELECT * FROM fn_get_recent_notifications(1, 20);
CREATE OR REPLACE FUNCTION fn_get_recent_notifications(
    p_user_id INT,
    p_limit INT DEFAULT 20
)
RETURNS TABLE (
    notification_id INT,
    message VARCHAR(255),
    type VARCHAR(50),
    link VARCHAR(255),
    read BOOLEAN,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.id,
        n.message,
        n.type,
        n.link,
        n.read,
        n.created_at
    FROM Notifications n
    WHERE n.user_id = p_user_id
    ORDER BY n.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- DELETE OLD NOTIFICATIONS
-- ============================================================================

-- Function: fn_delete_old_notifications
-- Description: Deletes notifications older than specified days
-- Parameters:
--   p_days_old: Number of days after which notifications should be deleted
--   p_only_read: If TRUE, only delete read notifications (default TRUE)
-- Returns: INT - Number of notifications deleted
-- Usage: SELECT fn_delete_old_notifications(30, TRUE);
CREATE OR REPLACE FUNCTION fn_delete_old_notifications(
    p_days_old INT DEFAULT 30,
    p_only_read BOOLEAN DEFAULT TRUE
)
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    IF p_days_old < 1 THEN
        RAISE EXCEPTION 'days_old must be at least 1';
    END IF;

    IF p_only_read THEN
        DELETE FROM Notifications
        WHERE created_at < NOW() - (p_days_old || ' days')::INTERVAL
            AND read = TRUE;
    ELSE
        DELETE FROM Notifications
        WHERE created_at < NOW() - (p_days_old || ' days')::INTERVAL;
    END IF;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Deleted % old notifications', deleted_count;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- BROADCAST NOTIFICATION
-- ============================================================================

-- Function: fn_broadcast_notification
-- Description: Sends a notification to all active users
-- Parameters:
--   p_message: Notification message
--   p_type: Notification type (optional)
--   p_link: Optional link/URL related to notification
-- Returns: INT - Number of notifications created
-- Usage: SELECT fn_broadcast_notification('System maintenance scheduled', 'system', '/maintenance');
CREATE OR REPLACE FUNCTION fn_broadcast_notification(
    p_message VARCHAR(255),
    p_type VARCHAR(50) DEFAULT NULL,
    p_link VARCHAR(255) DEFAULT NULL
)
RETURNS INT AS $$
DECLARE
    created_count INT;
BEGIN
    -- Validate message
    IF p_message IS NULL OR LENGTH(TRIM(p_message)) = 0 THEN
        RAISE EXCEPTION 'Message cannot be empty';
    END IF;

    -- Insert notification for all active users
    INSERT INTO Notifications (user_id, message, type, link, read, created_at)
    SELECT
        id,
        TRIM(p_message),
        p_type,
        p_link,
        FALSE,
        NOW()
    FROM Users
    WHERE is_deleted = FALSE;

    GET DIAGNOSTICS created_count = ROW_COUNT;

    RAISE NOTICE 'Broadcast notification sent to % users', created_count;
    RETURN created_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DELETE NOTIFICATION
-- ============================================================================

-- Function: fn_delete_notification
-- Description: Deletes a specific notification
-- Parameters:
--   p_notification_id: Notification ID to delete
--   p_user_id: User ID (for ownership verification)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_delete_notification(1, 1);
CREATE OR REPLACE FUNCTION fn_delete_notification(
    p_notification_id INT,
    p_user_id INT
)
RETURNS BOOLEAN AS $$
DECLARE
    deleted_count INT;
BEGIN
    -- Delete notification only if it belongs to the user
    DELETE FROM Notifications
    WHERE id = p_notification_id AND user_id = p_user_id;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    IF deleted_count = 0 THEN
        RAISE NOTICE 'Notification % not found or does not belong to user %', p_notification_id, p_user_id;
        RETURN FALSE;
    END IF;

    RAISE NOTICE 'Notification % deleted', p_notification_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET UNREAD COUNT
-- ============================================================================

-- Function: fn_get_unread_count
-- Description: Returns count of unread notifications for a user
-- Parameters:
--   p_user_id: User ID
-- Returns: INT - Number of unread notifications
-- Usage: SELECT fn_get_unread_count(1);
CREATE OR REPLACE FUNCTION fn_get_unread_count(p_user_id INT)
RETURNS INT AS $$
DECLARE
    unread_count INT;
BEGIN
    SELECT COUNT(*)
    INTO unread_count
    FROM Notifications
    WHERE user_id = p_user_id AND read = FALSE;

    RETURN unread_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET NOTIFICATIONS BY TYPE
-- ============================================================================

-- Function: fn_get_notifications_by_type
-- Description: Retrieves notifications of a specific type for a user
-- Parameters:
--   p_user_id: User ID
--   p_type: Notification type
--   p_limit: Maximum number of notifications (default 50)
-- Returns: TABLE with notification information
-- Usage: SELECT * FROM fn_get_notifications_by_type(1, 'bus_arrival', 50);
CREATE OR REPLACE FUNCTION fn_get_notifications_by_type(
    p_user_id INT,
    p_type VARCHAR(50),
    p_limit INT DEFAULT 50
)
RETURNS TABLE (
    notification_id INT,
    message VARCHAR(255),
    type VARCHAR(50),
    link VARCHAR(255),
    read BOOLEAN,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        n.id,
        n.message,
        n.type,
        n.link,
        n.read,
        n.created_at
    FROM Notifications n
    WHERE n.user_id = p_user_id
        AND n.type = p_type
    ORDER BY n.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET NOTIFICATION STATS
-- ============================================================================

-- Function: fn_get_notification_stats
-- Description: Returns notification statistics for a user
-- Parameters:
--   p_user_id: User ID
-- Returns: TABLE with notification statistics
-- Usage: SELECT * FROM fn_get_notification_stats(1);
CREATE OR REPLACE FUNCTION fn_get_notification_stats(p_user_id INT)
RETURNS TABLE (
    total_count BIGINT,
    unread_count BIGINT,
    read_count BIGINT,
    notifications_by_type JSON
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_count,
        COUNT(*) FILTER (WHERE read = FALSE) AS unread_count,
        COUNT(*) FILTER (WHERE read = TRUE) AS read_count,
        json_object_agg(
            COALESCE(type, 'null'),
            type_count
        ) AS notifications_by_type
    FROM (
        SELECT
            n.read,
            n.type,
            COUNT(*) AS type_count
        FROM Notifications n
        WHERE n.user_id = p_user_id
        GROUP BY n.type, n.read
    ) type_counts
    GROUP BY TRUE;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- MARK NOTIFICATIONS BY TYPE AS READ
-- ============================================================================

-- Function: fn_mark_type_as_read
-- Description: Marks all unread notifications of a specific type as read
-- Parameters:
--   p_user_id: User ID
--   p_type: Notification type
-- Returns: INT - Number of notifications marked as read
-- Usage: SELECT fn_mark_type_as_read(1, 'bus_arrival');
CREATE OR REPLACE FUNCTION fn_mark_type_as_read(
    p_user_id INT,
    p_type VARCHAR(50)
)
RETURNS INT AS $$
DECLARE
    updated_count INT;
BEGIN
    UPDATE Notifications
    SET read = TRUE
    WHERE user_id = p_user_id
        AND type = p_type
        AND read = FALSE;

    GET DIAGNOSTICS updated_count = ROW_COUNT;

    RAISE NOTICE 'Marked % notifications of type "%" as read for user %', updated_count, p_type, p_user_id;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- Create a notification:
-- SELECT fn_create_notification(1, 'Your bus is arriving in 5 minutes', 'bus_arrival', '/buses/1');

-- Mark notification as read:
-- SELECT fn_mark_notification_read(1);

-- Mark all notifications as read:
-- SELECT fn_mark_all_read(1);

-- Get unread notifications:
-- SELECT * FROM fn_get_unread_notifications(1);

-- Get recent notifications:
-- SELECT * FROM fn_get_recent_notifications(1, 20);

-- Delete old notifications (older than 30 days, only read):
-- SELECT fn_delete_old_notifications(30, TRUE);

-- Broadcast notification to all users:
-- SELECT fn_broadcast_notification('System maintenance scheduled for tonight', 'system', '/maintenance');

-- Delete a notification:
-- SELECT fn_delete_notification(1, 1);

-- Get unread count:
-- SELECT fn_get_unread_count(1);

-- Get notifications by type:
-- SELECT * FROM fn_get_notifications_by_type(1, 'bus_arrival', 50);

-- Get notification statistics:
-- SELECT * FROM fn_get_notification_stats(1);

-- Mark all notifications of a type as read:
-- SELECT fn_mark_type_as_read(1, 'bus_arrival');
