-- Migration script to convert existing database to use ENUM types
-- Run this script on existing databases to update VARCHAR status fields to ENUM types

-- Step 1: Create ENUM types if they don't exist
DO $$ BEGIN
    CREATE TYPE roles AS ENUM ('Admin', 'Driver', 'User');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE bus_status AS ENUM ('Active', 'Inactive', 'Maintenance');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE driver_status AS ENUM ('Active', 'Inactive', 'On Leave');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Step 2: Drop deprecated tables if they exist
DROP TABLE IF EXISTS Notifications CASCADE;
DROP TABLE IF EXISTS Feedback CASCADE;
DROP TABLE IF EXISTS UserRoles CASCADE;
DROP TABLE IF EXISTS Roles CASCADE;

-- Step 3: Alter Buses table to use bus_status ENUM
-- First remove the default constraint
ALTER TABLE Buses ALTER COLUMN status DROP DEFAULT;

-- Then alter the column type
ALTER TABLE Buses
    ALTER COLUMN status TYPE bus_status
    USING status::bus_status;

-- Finally, re-add the default with the correct type
ALTER TABLE Buses ALTER COLUMN status SET DEFAULT 'Active'::bus_status;

-- Step 4: Alter Drivers table to use driver_status ENUM
-- First remove the default constraint
ALTER TABLE Drivers ALTER COLUMN status DROP DEFAULT;

-- Then alter the column type
ALTER TABLE Drivers
    ALTER COLUMN status TYPE driver_status
    USING status::driver_status;

-- Finally, re-add the default with the correct type
ALTER TABLE Drivers ALTER COLUMN status SET DEFAULT 'Active'::driver_status;

-- Step 5: Migrate Users table from admin BOOLEAN and Roles/UserRoles to role ENUM
-- Add the new role column if it doesn't exist
DO $$ BEGIN
    ALTER TABLE Users ADD COLUMN role roles;
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Migrate existing data: convert admin flag to role
-- If user has admin=TRUE, set role to 'Admin'
-- If user is in Drivers table, set role to 'Driver'
-- Otherwise set role to 'User'
UPDATE Users u
SET role = CASE
    WHEN u.admin = TRUE THEN 'Admin'::roles
    WHEN EXISTS (SELECT 1 FROM Drivers d WHERE d.user_id = u.id) THEN 'Driver'::roles
    ELSE 'User'::roles
END
WHERE u.role IS NULL;

-- Set default for role column
ALTER TABLE Users ALTER COLUMN role SET DEFAULT 'User'::roles;

-- Make role column NOT NULL
ALTER TABLE Users ALTER COLUMN role SET NOT NULL;

-- Drop the old admin column
ALTER TABLE Users DROP COLUMN IF EXISTS admin;

-- Verification queries (optional - uncomment to run)
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'buses' AND column_name = 'status';

-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'drivers' AND column_name = 'status';

-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_name = 'users' AND column_name = 'role';
