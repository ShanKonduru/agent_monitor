-- Agent Monitor Framework - PostgreSQL Initialization Script
-- This script sets up the initial database structure and permissions

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create indexes for better performance
-- (Tables will be created by SQLAlchemy migrations)

-- Set up connection pooling optimization
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = '0.9';
ALTER SYSTEM SET wal_buffers = '16MB';

-- Create additional schema for metrics if needed
CREATE SCHEMA IF NOT EXISTS metrics;
GRANT ALL PRIVILEGES ON SCHEMA metrics TO monitor_user;

-- Log successful initialization
INSERT INTO pg_stat_statements_info (info) VALUES ('Agent Monitor PostgreSQL initialized successfully') 
ON CONFLICT DO NOTHING;

-- Show successful initialization message
DO $$
BEGIN
    RAISE NOTICE '🐘 PostgreSQL initialized for Agent Monitor Framework';
    RAISE NOTICE '📊 Database: agent_monitor';
    RAISE NOTICE '👤 User: monitor_user';
    RAISE NOTICE '🔧 Extensions: uuid-ossp, pg_stat_statements';
    RAISE NOTICE '📈 Schema: public, metrics';
END $$;