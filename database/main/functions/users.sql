-- ============================================================================
-- USERS.SQL - User Management Functions
-- ============================================================================
-- Description: Functions for user CRUD operations, authentication, and profile management
-- Dependencies: Users table, utilities.sql (validation functions)
-- ============================================================================

-- ============================================================================
-- USER CREATION
-- ============================================================================

-- Function: fn_create_user
-- Description: Creates a new user with validation and auto-generated fields
-- Parameters:
--   p_name: User's full name
--   p_phone: Phone number (11 digits)
--   p_email: Email address
--   p_username: Username (optional)
--   p_password: Plain text password to be hashed
--   p_role: User role (default 'User')
-- Returns: INT - New user ID
-- Usage: SELECT fn_create_user('John Doe', '08412345678', 'john@example.com', 'johndoe', 'password123', 'User');
DROP FUNCTION IF EXISTS fn_create_user;
CREATE OR REPLACE FUNCTION fn_create_user(
    p_name VARCHAR(100),
    p_phone VARCHAR(11),
    p_email VARCHAR(255),
    p_username VARCHAR(50) DEFAULT NULL,
    p_password TEXT DEFAULT NULL,
    p_role roles DEFAULT 'User'
)
RETURNS INT AS $$
DECLARE
    new_user_id INT;
    v_public_id VARCHAR(100);
    v_password_hash VARCHAR(100);
BEGIN
    -- Validate required fields
    IF p_name IS NULL OR LENGTH(TRIM(p_name)) = 0 THEN
        RAISE EXCEPTION 'Name cannot be empty';
    END IF;

    IF p_email IS NULL OR LENGTH(TRIM(p_email)) = 0 THEN
        RAISE EXCEPTION 'Email cannot be empty';
    END IF;

    -- Validate email format
    IF NOT fn_validate_email(p_email) THEN
        RAISE EXCEPTION 'Invalid email format: %', p_email;
    END IF;

    -- Validate phone format
    IF NOT fn_validate_phone(p_phone) THEN
        RAISE EXCEPTION 'Invalid phone format. Must be 11 digits: %', p_phone;
    END IF;

    -- Generate public_id
    v_public_id := fn_generate_uuid();

    -- Hash password if provided
    IF p_password IS NOT NULL THEN
        v_password_hash := crypt(p_password, gen_salt('bf'));
    END IF;

    -- Insert user
    INSERT INTO Users (
        name,
        phone,
        email,
        username,
        password_hash,
        role,
        public_id,
        registered_on,
        is_deleted
    ) VALUES (
        TRIM(p_name),
        p_phone,
        LOWER(TRIM(p_email)),
        LOWER(TRIM(p_username)),
        v_password_hash,
        p_role,
        v_public_id,
        NOW(),
        FALSE
    )
    RETURNING id INTO new_user_id;

    RAISE NOTICE 'User created successfully with ID: %', new_user_id;
    RETURN new_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Email, username, or phone already exists';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- USER AUTHENTICATION
-- ============================================================================

-- Function: fn_verify_user_password
-- Description: Verifies a user's password
-- Parameters:
--   p_email: User's email or username
--   p_password: Plain text password to verify
-- Returns: INT - User ID if successful, NULL if failed
-- Usage: SELECT fn_verify_user_password('john@example.com', 'password123');
DROP FUNCTION IF EXISTS fn_verify_user_password;
CREATE OR REPLACE FUNCTION fn_verify_user_password(
    p_email TEXT,
    p_password TEXT
)
RETURNS INT AS $$
DECLARE
    v_user_id INT;
    v_password_hash VARCHAR(100);
BEGIN
    IF p_email IS NULL OR p_password IS NULL THEN
        RETURN NULL;
    END IF;

    -- Get user by email or username
    SELECT id, password_hash
    INTO v_user_id, v_password_hash
    FROM Users
    WHERE (LOWER(email) = LOWER(p_email) OR LOWER(username) = LOWER(p_email))
        AND is_deleted = FALSE
        AND password_hash IS NOT NULL;

    -- Check if user exists
    IF v_user_id IS NULL THEN
        RETURN NULL;
    END IF;

    -- Verify password
    IF v_password_hash = crypt(p_password, v_password_hash) THEN
        RETURN v_user_id;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- USER UPDATE
-- ============================================================================

-- Function: fn_update_user_profile
-- Description: Updates user profile information
-- Parameters:
--   p_user_id: User ID to update
--   p_name: New name (NULL to keep current)
--   p_phone: New phone (NULL to keep current)
--   p_email: New email (NULL to keep current)
--   p_username: New username (NULL to keep current)
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_update_user_profile(1, 'Jane Doe', NULL, NULL, NULL);
DROP FUNCTION IF EXISTS fn_update_user_profile;
CREATE OR REPLACE FUNCTION fn_update_user_profile(
    p_user_id INT,
    p_name VARCHAR(100) DEFAULT NULL,
    p_phone VARCHAR(11) DEFAULT NULL,
    p_email VARCHAR(255) DEFAULT NULL,
    p_username VARCHAR(50) DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    user_exists BOOLEAN;
BEGIN
    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ) INTO user_exists;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Validate email if provided
    IF p_email IS NOT NULL AND NOT fn_validate_email(p_email) THEN
        RAISE EXCEPTION 'Invalid email format: %', p_email;
    END IF;

    -- Validate phone if provided
    IF p_phone IS NOT NULL AND NOT fn_validate_phone(p_phone) THEN
        RAISE EXCEPTION 'Invalid phone format. Must be 11 digits: %', p_phone;
    END IF;

    -- Update user
    UPDATE Users
    SET
        name = COALESCE(TRIM(p_name), name),
        phone = COALESCE(p_phone, phone),
        email = COALESCE(LOWER(TRIM(p_email)), email),
        username = COALESCE(LOWER(TRIM(p_username)), username),
        updated_at = NOW()
    WHERE id = p_user_id;

    RAISE NOTICE 'User % updated successfully', p_user_id;
    RETURN TRUE;
EXCEPTION
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Email, username, or phone already exists';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PASSWORD MANAGEMENT
-- ============================================================================

-- Function: fn_change_user_password
-- Description: Changes a user's password
-- Parameters:
--   p_user_id: User ID
--   p_new_password: New plain text password
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_change_user_password(1, 'newpassword123');
DROP FUNCTION IF EXISTS fn_change_user_password;
CREATE OR REPLACE FUNCTION fn_change_user_password(
    p_user_id INT,
    p_new_password TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    user_exists BOOLEAN;
    v_password_hash VARCHAR(100);
BEGIN
    IF p_new_password IS NULL OR LENGTH(p_new_password) < 6 THEN
        RAISE EXCEPTION 'Password must be at least 6 characters';
    END IF;

    -- Check if user exists and is not deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = FALSE
    ) INTO user_exists;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist or is deleted', p_user_id;
    END IF;

    -- Hash new password
    v_password_hash := crypt(p_new_password, gen_salt('bf'));

    -- Update password
    UPDATE Users
    SET
        password_hash = v_password_hash,
        updated_at = NOW()
    WHERE id = p_user_id;

    RAISE NOTICE 'Password changed successfully for user %', p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SOFT DELETE
-- ============================================================================

-- Function: fn_soft_delete_user
-- Description: Soft deletes a user (sets is_deleted flag)
-- Parameters:
--   p_user_id: User ID to delete
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_soft_delete_user(1);
DROP FUNCTION IF EXISTS fn_soft_delete_user;
CREATE OR REPLACE FUNCTION fn_soft_delete_user(p_user_id INT)
RETURNS BOOLEAN AS $$
DECLARE
    user_exists BOOLEAN;
    already_deleted BOOLEAN;
BEGIN
    -- Check if user exists
    SELECT
        EXISTS(SELECT 1 FROM Users WHERE id = p_user_id),
        EXISTS(SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = TRUE)
    INTO user_exists, already_deleted;

    IF NOT user_exists THEN
        RAISE EXCEPTION 'User with ID % does not exist', p_user_id;
    END IF;

    IF already_deleted THEN
        RAISE NOTICE 'User % is already deleted', p_user_id;
        RETURN FALSE;
    END IF;

    -- Soft delete user
    UPDATE Users
    SET
        is_deleted = TRUE,
        deleted_at = NOW(),
        updated_at = NOW()
    WHERE id = p_user_id;

    RAISE NOTICE 'User % soft deleted successfully', p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RESTORE USER
-- ============================================================================

-- Function: fn_restore_user
-- Description: Restores a soft-deleted user
-- Parameters:
--   p_user_id: User ID to restore
-- Returns: BOOLEAN - TRUE if successful
-- Usage: SELECT fn_restore_user(1);
DROP FUNCTION IF EXISTS fn_restore_user;
CREATE OR REPLACE FUNCTION fn_restore_user(p_user_id INT)
RETURNS BOOLEAN AS $$
DECLARE
    user_deleted BOOLEAN;
BEGIN
    -- Check if user is deleted
    SELECT EXISTS(
        SELECT 1 FROM Users WHERE id = p_user_id AND is_deleted = TRUE
    ) INTO user_deleted;

    IF NOT user_deleted THEN
        RAISE NOTICE 'User % is not deleted or does not exist', p_user_id;
        RETURN FALSE;
    END IF;

    -- Restore user
    UPDATE Users
    SET
        is_deleted = FALSE,
        deleted_at = NULL,
        updated_at = NOW()
    WHERE id = p_user_id;

    RAISE NOTICE 'User % restored successfully', p_user_id;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- USER QUERIES
-- ============================================================================

-- Function: fn_get_active_users
-- Description: Returns all active (non-deleted) users
-- Returns: TABLE with user information
-- Usage: SELECT * FROM fn_get_active_users();
DROP FUNCTION IF EXISTS fn_get_active_users;
CREATE OR REPLACE FUNCTION fn_get_active_users()
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    role roles,
    registered_on TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.name,
        u.phone,
        u.email,
        u.username,
        u.role,
        u.registered_on
    FROM Users u
    WHERE u.is_deleted = FALSE
    ORDER BY u.registered_on DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- USER SEARCH
-- ============================================================================

-- Function: fn_search_users
-- Description: Searches users by name, email, username, or phone
-- Parameters:
--   search_term: Search string (case-insensitive)
-- Returns: TABLE with matching user information
-- Usage: SELECT * FROM fn_search_users('john');
DROP FUNCTION IF EXISTS fn_search_users;
CREATE OR REPLACE FUNCTION fn_search_users(search_term TEXT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    role roles,
    registered_on TIMESTAMP
) AS $$
BEGIN
    IF search_term IS NULL OR LENGTH(TRIM(search_term)) = 0 THEN
        RAISE EXCEPTION 'Search term cannot be empty';
    END IF;

    RETURN QUERY
    SELECT
        u.id,
        u.name,
        u.phone,
        u.email,
        u.username,
        u.role,
        u.registered_on
    FROM Users u
    WHERE u.is_deleted = FALSE
        AND (
            u.name ILIKE '%' || search_term || '%'
            OR u.email ILIKE '%' || search_term || '%'
            OR u.username ILIKE '%' || search_term || '%'
            OR u.phone LIKE '%' || search_term || '%'
        )
    ORDER BY u.registered_on DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET USER BY PUBLIC ID
-- ============================================================================

-- Function: fn_get_user_by_public_id
-- Description: Retrieves a user by their public_id
-- Parameters:
--   p_public_id: User's public ID
-- Returns: TABLE with user information
-- Usage: SELECT * FROM fn_get_user_by_public_id('abc123...');
DROP FUNCTION IF EXISTS fn_get_user_by_public_id;
CREATE OR REPLACE FUNCTION fn_get_user_by_public_id(p_public_id VARCHAR(100))
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    role roles,
    registered_on TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.name,
        u.phone,
        u.email,
        u.username,
        u.role,
        u.registered_on
    FROM Users u
    WHERE u.public_id = p_public_id
        AND u.is_deleted = FALSE;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET USER BY ID
-- ============================================================================
-- Function: fn_get_user_by_id
-- Description: Retrieves a user by their internal ID
-- Parameters:
--   p_user_id: User's internal ID
-- Returns: TABLE with user information
-- Usage: SELECT fn_get_user_by_id(1);
DROP FUNCTION IF EXISTS fn_get_user_by_id;
CREATE OR REPLACE FUNCTION fn_get_user_by_id(p_user_id INT)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    public_id VARCHAR(100),
    role roles
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        users.id,
        users.name,
        users.phone,
        users.email,
        users.username,
        users.public_id,
        users.role
    FROM users
    WHERE users.id = p_user_id;
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- GET USER COUNT
-- ============================================================================

-- Function: fn_get_user_count
-- Description: Returns count of active users
-- Returns: INT - Number of active users
-- Usage: SELECT fn_get_user_count();
DROP FUNCTION IF EXISTS fn_get_user_count;
CREATE OR REPLACE FUNCTION fn_get_user_count()
RETURNS INT AS $$
DECLARE
    user_count INT;
BEGIN
    SELECT COUNT(*)
    INTO user_count
    FROM Users
    WHERE is_deleted = FALSE;

    RETURN user_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- GET ALL USERS (ADMIN ONLY - CURSOR-BASED PAGINATION)
-- ============================================================================

-- Function: fn_get_all_users
-- Description: Returns all users with cursor-based pagination (admin only)
--              Includes soft-deleted users for admin oversight
-- Parameters:
--   p_cursor: Cursor for pagination (user ID, NULL for first page)
--   p_limit: Number of records per page (default 20, max 100)
--   p_role_filter: Optional role filter (NULL for all roles)
--   p_include_deleted: Include soft-deleted users (default TRUE for admin)
-- Returns: TABLE with user information only (no pagination metadata in rows)
-- Usage:
--   -- First page:
--   SELECT * FROM fn_get_all_users(NULL, 20, NULL, TRUE);
--   -- Next page (using last user ID as cursor):
--   SELECT * FROM fn_get_all_users(20, 20, NULL, TRUE);
--   -- Filter by role:
--   SELECT * FROM fn_get_all_users(NULL, 20, 'Driver', TRUE);
DROP FUNCTION IF EXISTS fn_get_all_users;
CREATE OR REPLACE FUNCTION fn_get_all_users(
    p_cursor INT DEFAULT NULL,
    p_limit INT DEFAULT 20,
    p_role_filter roles DEFAULT NULL,
    p_include_deleted BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    public_id VARCHAR(100),
    role roles,
    registered_on TIMESTAMP,
    is_deleted BOOLEAN,
    deleted_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
DECLARE
    v_limit INT;
BEGIN
    -- Validate and cap limit
    IF p_limit IS NULL OR p_limit <= 0 THEN
        v_limit := 20;
    ELSIF p_limit > 100 THEN
        v_limit := 100;
    ELSE
        v_limit := p_limit;
    END IF;

    -- Return user records with cursor-based pagination
    RETURN QUERY
    SELECT
        u.id,
        u.name,
        u.phone,
        u.email,
        u.username,
        u.public_id,
        u.role,
        u.registered_on,
        u.is_deleted,
        u.deleted_at,
        u.updated_at
    FROM Users u
    WHERE
        -- Cursor-based pagination
        (p_cursor IS NULL OR u.id > p_cursor)
        -- Role filter
        AND (p_role_filter IS NULL OR u.role = p_role_filter)
        -- Deleted filter
        AND (p_include_deleted = TRUE OR u.is_deleted = FALSE)
    ORDER BY u.id ASC
    LIMIT v_limit;
END;
$$ LANGUAGE plpgsql STABLE;


-- ===========================================================================
-- fn_get_user_by_email
-- ===========================================================================
-- Function: fn_get_user_by_email
-- Description: Retrieves a user by their email address
-- Parameters:
--   p_email: User's email address
-- Returns: TABLE with user information
-- Usage: SELECT * FROM fn_get_user_by_email('user@example.com');
DROP FUNCTION IF EXISTS fn_get_user_by_email;
CREATE OR REPLACE FUNCTION fn_get_user_by_email(p_email VARCHAR(255))
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    public_id VARCHAR(100),
    role roles
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        users.id,
        users.name,
        users.phone,
        users.email,
        users.username,
        users.public_id,
        users.role
    FROM users
    WHERE LOWER(users.email) = LOWER(p_email)
        AND users.is_deleted = FALSE;
END;
$$ LANGUAGE plpgsql STABLE;

-- ===========================================================================
-- fn_get_user_by_username
-- ===========================================================================
-- Function: fn_get_user_by_username
-- Description: Retrieves a user by their username
-- Parameters:
--   p_username: User's username
-- Returns: TABLE with user information
-- Usage: SELECT * FROM fn_get_user_by_username('johndoe');
DROP FUNCTION IF EXISTS fn_get_user_by_username;
CREATE OR REPLACE FUNCTION fn_get_user_by_username(p_username VARCHAR(50))
RETURNS TABLE (
    id INT,
    name VARCHAR(100),
    phone VARCHAR(11),
    email VARCHAR(255),
    username VARCHAR(50),
    public_id VARCHAR(100),
    role roles
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        users.id,
        users.name,
        users.phone,
        users.email,
        users.username,
        users.public_id,
        users.role
    FROM users
    WHERE LOWER(users.username) = LOWER(p_username)
        AND users.is_deleted = FALSE;
END;
$$ LANGUAGE plpgsql STABLE;