-- SentinelAI PostgreSQL Initialization
-- This script runs on first database creation

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS sentinelai;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set search path
ALTER DATABASE sentinelai SET search_path TO sentinelai, public, audit;

-- Create roles if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sentinelai_analyst') THEN
        CREATE ROLE sentinelai_analyst;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sentinelai_admin') THEN
        CREATE ROLE sentinelai_admin;
    END IF;
END
$$;

-- Grant permissions
GRANT USAGE ON SCHEMA sentinelai TO sentinelai_analyst;
GRANT USAGE ON SCHEMA audit TO sentinelai_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sentinelai TO sentinelai_admin;

-- Performance configuration
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '512MB';
ALTER SYSTEM SET effective_cache_size = '1536MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET random_page_cost = '1.1';
ALTER SYSTEM SET effective_io_concurrency = '200';
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = '500';
