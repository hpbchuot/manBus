-- Function: fn_blacklist_token
-- Description: Adds a token to the blacklist (used during logout or token revocation)
-- Parameters:
--   token_value: JWT token string to blacklist
-- Returns: BOOLEAN - TRUE if successful (idempotent)
-- Usage: SELECT fn_blacklist_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');
DROP FUNCTION IF EXISTS fn_blacklist_token;
CREATE OR REPLACE FUNCTION fn_blacklist_token(token_value TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    IF token_value IS NULL OR LENGTH(token_value) = 0 THEN
        RAISE EXCEPTION 'Token value cannot be empty';
    END IF;

    -- Insert token into blacklist (ignore if already exists)
    INSERT INTO BlacklistTokens (token, blacklisted_on)
    VALUES (token_value, NOW())
    ON CONFLICT (token) DO NOTHING;

    RAISE NOTICE 'Token blacklisted successfully';
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function: fn_is_token_blacklisted
-- Description: Checks if a token is in the blacklist
-- Parameters:
--   token_value: JWT token string to check
-- Returns: BOOLEAN - TRUE if blacklisted, FALSE otherwise
-- Usage: SELECT fn_is_token_blacklisted('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');
DROP FUNCTION IF EXISTS fn_is_token_blacklisted;
CREATE OR REPLACE FUNCTION fn_is_token_blacklisted(token_value TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    token_exists BOOLEAN;
BEGIN
    IF token_value IS NULL THEN
        RETURN FALSE;
    END IF;

    SELECT EXISTS(
        SELECT 1
        FROM BlacklistTokens
        WHERE token = token_value
    ) INTO token_exists;

    RETURN token_exists;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- TOKEN CLEANUP
-- ============================================================================

-- Function: fn_cleanup_old_tokens
-- Description: Removes tokens older than specified days from blacklist
-- Parameters:
--   days_old: Number of days after which tokens should be removed
-- Returns: INT - Number of tokens deleted
-- Usage: SELECT fn_cleanup_old_tokens(30); -- Remove tokens older than 30 days
DROP FUNCTION IF EXISTS fn_cleanup_old_tokens;
CREATE OR REPLACE FUNCTION fn_cleanup_old_tokens(days_old INT DEFAULT 30)
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    IF days_old < 1 THEN
        RAISE EXCEPTION 'days_old must be at least 1';
    END IF;

    DELETE FROM BlacklistTokens
    WHERE blacklisted_on < NOW() - (days_old || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Deleted % old tokens', deleted_count;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function: fn_user_has_role
-- Description: Checks if a user has a specific role
-- Parameters:
--   p_user_id: User ID to check
--   p_role_name: Name of the role to check for ('Admin', 'Driver', 'User')
-- Returns: BOOLEAN - TRUE if user has the role, FALSE otherwise
-- Usage: SELECT fn_user_has_role(1, 'Admin');
DROP FUNCTION IF EXISTS fn_user_has_role;
CREATE OR REPLACE FUNCTION fn_user_has_role(p_user_id INT, p_role_name roles)
RETURNS BOOLEAN AS $$
DECLARE
    user_role roles;
BEGIN
    IF p_user_id IS NULL OR p_role_name IS NULL THEN
        RETURN FALSE;
    END IF;

    SELECT role INTO user_role
    FROM Users
    WHERE id = p_user_id
        AND is_deleted = FALSE;

    RETURN user_role = p_role_name;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: fn_set_user_role
-- Description: Sets a user's role
-- Parameters:
--   p_user_id: User ID to update
--   p_role_name: New role ('Admin', 'Driver', 'User')
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_set_user_role(1, 'Driver');
DROP FUNCTION IF EXISTS fn_set_user_role;
CREATE OR REPLACE FUNCTION fn_set_user_role(p_user_id INT, p_role_name roles)
RETURNS BOOLEAN AS $$
DECLARE
    user_exists BOOLEAN;
    current_role roles;
BEGIN
    -- Validate inputs
    IF p_user_id IS NULL OR p_role_name IS NULL THEN
        RAISE EXCEPTION 'User ID and role name cannot be NULL';
    END IF;

    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ), role INTO user_exists, current_role
    FROM Users
    WHERE id = p_user_id AND is_deleted = FALSE;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Check if user already has this role
    IF current_role = p_role_name THEN
        RAISE NOTICE 'User % already has role "%"', p_user_id, p_role_name;
        RETURN FALSE;
    END IF;

    -- Update role
    UPDATE Users
    SET role = p_role_name,
        updated_at = NOW()
    WHERE id = p_user_id;

    RAISE NOTICE 'Role "%" assigned to user %', p_role_name, p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Function: fn_get_user_role
-- Description: Gets a user's role
-- Parameters:
--   p_user_id: User ID
-- Returns: roles - User's role
-- Usage: SELECT fn_get_user_role(1);
DROP FUNCTION IF EXISTS fn_get_user_role;
CREATE OR REPLACE FUNCTION fn_get_user_role(p_user_id INT)
RETURNS roles AS $$
DECLARE
    user_role roles;
BEGIN
    IF p_user_id IS NULL THEN
        RETURN NULL;
    END IF;

    SELECT role INTO user_role
    FROM Users
    WHERE id = p_user_id
        AND is_deleted = FALSE;

    RETURN user_role;
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: fn_is_admin
-- Description: Checks if a user is an admin
-- Parameters:
--   p_user_id: User ID to check
-- Returns: BOOLEAN - TRUE if user is admin
-- Usage: SELECT fn_is_admin(1);
DROP FUNCTION IF EXISTS fn_is_admin;
CREATE OR REPLACE FUNCTION fn_is_admin(p_user_id INT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN fn_user_has_role(p_user_id, 'Admin');
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: fn_is_driver
-- Description: Checks if a user is a driver
-- Parameters:
--   p_user_id: User ID to check
-- Returns: BOOLEAN - TRUE if user is a driver
-- Usage: SELECT fn_is_driver(1);
CREATE OR REPLACE FUNCTION fn_is_driver(p_user_id INT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN fn_user_has_role(p_user_id, 'Driver');
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: fn_get_users_by_role
-- Description: Returns all users with a specific role
-- Parameters:
--   p_role_name: Role to filter by ('Admin', 'Driver', 'User')
-- Returns: TABLE with user information
-- Usage: SELECT * FROM fn_get_users_by_role('Driver', NULL, 50);
DROP FUNCTION IF EXISTS fn_get_users_by_role;
CREATE OR REPLACE FUNCTION fn_get_users_by_role(
    p_role_name roles,
    p_cursor INT DEFAULT NULL,
    p_limit INT DEFAULT 100
)
RETURNS TABLE (
    user_id INT,
    name VARCHAR(100),
    email VARCHAR(255),
    username VARCHAR(50),
    phone VARCHAR(11),
    registered_on TIMESTAMP
) AS $$
BEGIN
    IF p_role_name IS NULL THEN
        RAISE EXCEPTION 'Role name cannot be NULL';
    END IF;

    RETURN QUERY
    SELECT
        u.id,
        u.name,
        u.email,
        u.username,
        u.phone,
        u.registered_on
    FROM Users u
    WHERE u.role = p_role_name
        AND u.is_deleted = FALSE
        AND (p_cursor IS NULL OR u.id > p_cursor)
    
    ORDER BY u.registered_on DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- EXAMPLES AND TESTING
-- ============================================================================

-- Example usage:
-- Blacklist a token:
-- SELECT fn_blacklist_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');

-- Check if token is blacklisted:
-- SELECT fn_is_token_blacklisted('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');

-- Cleanup old tokens (older than 30 days):
-- SELECT fn_cleanup_old_tokens(30);

-- Check if user has role:
-- SELECT fn_user_has_role(1, 'Admin');

-- Set user role:
-- SELECT fn_set_user_role(1, 'Driver');

-- Get user role:
-- SELECT fn_get_user_role(1);

-- Check if user is admin:
-- SELECT fn_is_admin(1);

-- Check if user is driver:
-- SELECT fn_is_driver(1);

-- Get all users with a specific role:
-- SELECT * FROM fn_get_users_by_role('Driver');
