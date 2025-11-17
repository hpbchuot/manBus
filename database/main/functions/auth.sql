-- ============================================================================
-- AUTH.SQL - Authentication and Authorization Functions
-- ============================================================================
-- Description: Functions for JWT token blacklisting and role-based access control
-- Dependencies: BlacklistTokens, Roles, UserRoles tables
-- ============================================================================

-- ============================================================================
-- TOKEN BLACKLIST MANAGEMENT
-- ============================================================================

-- Function: fn_blacklist_token
-- Description: Adds a token to the blacklist (used during logout or token revocation)
-- Parameters:
--   token_value: JWT token string to blacklist
-- Returns: VOID
-- Usage: SELECT fn_blacklist_token('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');
CREATE OR REPLACE FUNCTION fn_blacklist_token(token_value TEXT)
RETURNS VOID AS $$
BEGIN
    IF token_value IS NULL OR LENGTH(token_value) = 0 THEN
        RAISE EXCEPTION 'Token value cannot be empty';
    END IF;

    -- Insert token into blacklist (ignore if already exists)
    INSERT INTO BlacklistTokens (token, blacklisted_on)
    VALUES (token_value, NOW())
    ON CONFLICT (token) DO NOTHING;

    RAISE NOTICE 'Token blacklisted successfully';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TOKEN VALIDATION
-- ============================================================================

-- Function: fn_is_token_blacklisted
-- Description: Checks if a token is in the blacklist
-- Parameters:
--   token_value: JWT token string to check
-- Returns: BOOLEAN - TRUE if blacklisted, FALSE otherwise
-- Usage: SELECT fn_is_token_blacklisted('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');
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

-- ============================================================================
-- ROLE CHECKING
-- ============================================================================

-- Function: fn_user_has_role
-- Description: Checks if a user has a specific role
-- Parameters:
--   p_user_id: User ID to check
--   role_name: Name of the role to check for
-- Returns: BOOLEAN - TRUE if user has the role, FALSE otherwise
-- Usage: SELECT fn_user_has_role(1, 'admin');
CREATE OR REPLACE FUNCTION fn_user_has_role(p_user_id INT, role_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    has_role BOOLEAN;
BEGIN
    IF p_user_id IS NULL OR role_name IS NULL THEN
        RETURN FALSE;
    END IF;

    SELECT EXISTS(
        SELECT 1
        FROM UserRoles ur
        INNER JOIN Roles r ON ur.role_id = r.role_id
        INNER JOIN Users u ON ur.user_id = u.id
        WHERE ur.user_id = p_user_id
            AND r.role_name = role_name
            AND u.is_deleted = FALSE
    ) INTO has_role;

    RETURN has_role;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- ROLE ASSIGNMENT
-- ============================================================================

-- Function: fn_assign_role
-- Description: Assigns a role to a user
-- Parameters:
--   p_user_id: User ID to assign role to
--   role_name: Name of the role to assign
-- Returns: BOOLEAN - TRUE if successful, FALSE if role already assigned
-- Usage: SELECT fn_assign_role(1, 'driver');
CREATE OR REPLACE FUNCTION fn_assign_role(p_user_id INT, role_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_role_id INT;
    user_exists BOOLEAN;
BEGIN
    -- Validate inputs
    IF p_user_id IS NULL OR role_name IS NULL THEN
        RAISE EXCEPTION 'User ID and role name cannot be NULL';
    END IF;

    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ) INTO user_exists;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Get role ID
    SELECT role_id INTO v_role_id
    FROM Roles
    WHERE Roles.role_name = fn_assign_role.role_name;

    IF v_role_id IS NULL THEN
        RAISE EXCEPTION 'Role "%" does not exist', role_name;
    END IF;

    -- Check if user already has this role
    IF fn_user_has_role(p_user_id, role_name) THEN
        RAISE NOTICE 'User % already has role "%"', p_user_id, role_name;
        RETURN FALSE;
    END IF;

    -- Assign role
    INSERT INTO UserRoles (user_id, role_id, assigned_at)
    VALUES (p_user_id, v_role_id, NOW());

    RAISE NOTICE 'Role "%" assigned to user %', role_name, p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- ROLE REVOCATION
-- ============================================================================

-- Function: fn_revoke_role
-- Description: Removes a role from a user
-- Parameters:
--   p_user_id: User ID to revoke role from
--   role_name: Name of the role to revoke
-- Returns: BOOLEAN - TRUE if successful, FALSE if user didn't have the role
-- Usage: SELECT fn_revoke_role(1, 'driver');
CREATE OR REPLACE FUNCTION fn_revoke_role(p_user_id INT, role_name TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    v_role_id INT;
    deleted_count INT;
BEGIN
    -- Validate inputs
    IF p_user_id IS NULL OR role_name IS NULL THEN
        RAISE EXCEPTION 'User ID and role name cannot be NULL';
    END IF;

    -- Get role ID
    SELECT role_id INTO v_role_id
    FROM Roles
    WHERE Roles.role_name = fn_revoke_role.role_name;

    IF v_role_id IS NULL THEN
        RAISE EXCEPTION 'Role "%" does not exist', role_name;
    END IF;

    -- Remove role
    DELETE FROM UserRoles
    WHERE user_id = p_user_id AND role_id = v_role_id;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    IF deleted_count = 0 THEN
        RAISE NOTICE 'User % did not have role "%"', p_user_id, role_name;
        RETURN FALSE;
    END IF;

    RAISE NOTICE 'Role "%" revoked from user %', role_name, p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- GET USER ROLES
-- ============================================================================

-- Function: fn_get_user_roles
-- Description: Returns all roles assigned to a user
-- Parameters:
--   p_user_id: User ID to get roles for
-- Returns: TABLE with role information
-- Usage: SELECT * FROM fn_get_user_roles(1);
CREATE OR REPLACE FUNCTION fn_get_user_roles(p_user_id INT)
RETURNS TABLE (
    role_id INT,
    role_name VARCHAR(100),
    description TEXT,
    assigned_at TIMESTAMP
) AS $$
BEGIN
    IF p_user_id IS NULL THEN
        RAISE EXCEPTION 'User ID cannot be NULL';
    END IF;

    RETURN QUERY
    SELECT
        r.role_id,
        r.role_name,
        r.description,
        ur.assigned_at
    FROM UserRoles ur
    INNER JOIN Roles r ON ur.role_id = r.role_id
    WHERE ur.user_id = p_user_id
    ORDER BY ur.assigned_at DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET USERS BY ROLE
-- ============================================================================

-- Function: fn_get_users_by_role
-- Description: Returns all users with a specific role
-- Parameters:
--   role_name: Name of the role
-- Returns: TABLE with user information
-- Usage: SELECT * FROM fn_get_users_by_role('driver');
CREATE OR REPLACE FUNCTION fn_get_users_by_role(role_name TEXT)
RETURNS TABLE (
    user_id INT,
    name VARCHAR(100),
    email VARCHAR(255),
    username VARCHAR(50),
    assigned_at TIMESTAMP
) AS $$
BEGIN
    IF role_name IS NULL THEN
        RAISE EXCEPTION 'Role name cannot be NULL';
    END IF;

    RETURN QUERY
    SELECT
        u.id,
        u.name,
        u.email,
        u.username,
        ur.assigned_at
    FROM Users u
    INNER JOIN UserRoles ur ON u.id = ur.user_id
    INNER JOIN Roles r ON ur.role_id = r.role_id
    WHERE r.role_name = fn_get_users_by_role.role_name
        AND u.is_deleted = FALSE
    ORDER BY ur.assigned_at DESC;
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
-- SELECT fn_user_has_role(1, 'admin');

-- Assign role to user:
-- SELECT fn_assign_role(1, 'driver');

-- Revoke role from user:
-- SELECT fn_revoke_role(1, 'driver');

-- Get all roles for a user:
-- SELECT * FROM fn_get_user_roles(1);

-- Get all users with a specific role:
-- SELECT * FROM fn_get_users_by_role('driver');
