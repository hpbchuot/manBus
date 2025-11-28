-- ============================================================================
-- CRON_JOBS.SQL - Automated Job Scheduling with pg_cron
-- ============================================================================
-- Description: Automated tasks for bus location updates and maintenance
-- Dependencies: pg_cron extension, buses.sql functions
-- ============================================================================

-- ============================================================================
-- ENABLE PG_CRON EXTENSION
-- ============================================================================

-- Enable pg_cron extension (requires superuser privileges)
-- NOTE: Before running this, ensure postgresql.conf contains:
--   shared_preload_libraries = 'pg_cron'
--   cron.database_name = 'manBusDB'
-- Then restart PostgreSQL
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- ============================================================================
-- BUS POSITION AUTO-UPDATE JOB
-- ============================================================================

-- Schedule bus position updates every minute
-- Speed: 20 m/s = 72 km/h for 1-minute intervals (bus moves 1200m per update)
-- Adjust speed based on your update frequency

-- Unschedule existing job if it exists (for re-running this script)
SELECT cron.unschedule('update-bus-positions')
WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'update-bus-positions'
);

-- Schedule the job to run every minute
SELECT cron.schedule(
    'update-bus-positions',                          -- job name
    '* * * * *',                                     -- every minute (standard cron syntax)
    $$SELECT fn_update_bus_positions_auto(20.0, 60);$$  -- 20 m/s, 60 second interval
);

-- ============================================================================
-- ALTERNATIVE: 30-SECOND UPDATES (TWO-JOB APPROACH)
-- ============================================================================

-- Since standard cron syntax doesn't support intervals less than 1 minute,
-- we can create two jobs that run at different times to achieve 30-second updates:
-- - Job 1: Runs at second 0 of each minute (on the minute)
-- - Job 2: Runs at second 30 of each minute (halfway through)

-- To use 30-second updates, uncomment the following and comment out the 1-minute job above:

/*
-- Unschedule existing jobs if they exist
SELECT cron.unschedule('update-bus-positions-even')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'update-bus-positions-even');

SELECT cron.unschedule('update-bus-positions-odd')
WHERE EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'update-bus-positions-odd');

-- Job 1: Runs on even minutes (0, 2, 4, 6, ... seconds within minute)
-- This simulates running at second 0
SELECT cron.schedule(
    'update-bus-positions-even',
    '0-58/2 * * * *',                                -- even minutes: 0, 2, 4, ...
    $$SELECT fn_update_bus_positions_auto(10.0, 30);$$  -- 10 m/s, 30 second interval
);

-- Job 2: Runs on odd minutes (1, 3, 5, 7, ... seconds within minute)
-- This simulates running at second 30
SELECT cron.schedule(
    'update-bus-positions-odd',
    '1-59/2 * * * *',                                -- odd minutes: 1, 3, 5, ...
    $$SELECT fn_update_bus_positions_auto(10.0, 30);$$  -- 10 m/s, 30 second interval
);
*/

-- ============================================================================
-- JOB MANAGEMENT COMMANDS
-- ============================================================================

-- View all scheduled jobs
-- SELECT jobid, jobname, schedule, command, active FROM cron.job;

-- View job execution history (last 20 runs)
-- SELECT job_name, status, return_message, start_time, end_time,
--        (end_time - start_time) AS duration
-- FROM cron.job_run_details
-- WHERE job_name LIKE 'update-bus-positions%'
-- ORDER BY start_time DESC
-- LIMIT 20;

-- Pause a job (without deleting it)
-- UPDATE cron.job SET active = FALSE WHERE jobname = 'update-bus-positions';

-- Resume a paused job
-- UPDATE cron.job SET active = TRUE WHERE jobname = 'update-bus-positions';

-- Delete a job completely
-- SELECT cron.unschedule('update-bus-positions');

-- ============================================================================
-- MONITORING QUERIES
-- ============================================================================

-- Check if jobs are running successfully
-- SELECT
--     jobname,
--     active,
--     schedule,
--     command,
--     (SELECT COUNT(*) FROM cron.job_run_details jrd
--      WHERE jrd.jobid = j.jobid AND jrd.status = 'succeeded') AS success_count,
--     (SELECT COUNT(*) FROM cron.job_run_details jrd
--      WHERE jrd.jobid = j.jobid AND jrd.status = 'failed') AS failure_count,
--     (SELECT MAX(end_time) FROM cron.job_run_details jrd
--      WHERE jrd.jobid = j.jobid) AS last_run
-- FROM cron.job j
-- WHERE jobname LIKE 'update-bus-positions%';

-- View recent failures
-- SELECT job_name, return_message, start_time, end_time
-- FROM cron.job_run_details
-- WHERE status = 'failed' AND job_name LIKE 'update-bus-positions%'
-- ORDER BY start_time DESC
-- LIMIT 10;

-- ============================================================================
-- INITIALIZATION
-- ============================================================================

-- Initialize all bus positions before starting the cron job
-- This ensures all buses have valid positions before auto-updates begin
-- Run this once when setting up the system:
-- SELECT fn_initialize_bus_positions();

-- ============================================================================
-- NOTES
-- ============================================================================

-- 1. Bus Speed Guidelines:
--    - Urban bus: 8-12 m/s (29-43 km/h)
--    - Suburban bus: 12-18 m/s (43-65 km/h)
--    - Highway bus: 18-25 m/s (65-90 km/h)
--
-- 2. Update Frequency:
--    - 30 seconds: More realistic, smoother movement, higher DB load
--    - 60 seconds: Standard, balanced approach, recommended for most cases
--    - 2-5 minutes: Less frequent, suitable for low-traffic systems
--
-- 3. Performance Considerations:
--    - Each update queries and updates all active buses
--    - Monitor database load: SELECT * FROM pg_stat_activity;
--    - Adjust speed and frequency based on your system requirements
--
-- 4. pg_cron Installation:
--    - Debian/Ubuntu: apt install postgresql-<version>-cron
--    - RedHat/CentOS: yum install pg_cron_<version>
--    - Then add to postgresql.conf and restart PostgreSQL
--
-- 5. Permissions:
--    - pg_cron requires superuser to install the extension
--    - Jobs run with the permissions of the database owner
--    - Ensure the database user can execute fn_update_bus_positions_auto()

-- ============================================================================
-- END OF FILE
-- ============================================================================
