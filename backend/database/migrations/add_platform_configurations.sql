-- Migration to add platform_configurations table
-- Run this to add the new table for platform configuration storage

CREATE TABLE IF NOT EXISTS platform_configurations (
    config_id VARCHAR PRIMARY KEY,
    org_id VARCHAR NOT NULL,
    platform VARCHAR NOT NULL,
    configuration JSONB NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_tested_at TIMESTAMP,
    last_test_status VARCHAR,
    last_test_error TEXT,
    configured_at TIMESTAMP NOT NULL DEFAULT NOW(),
    configured_by VARCHAR,
    updated_at TIMESTAMP DEFAULT NOW(),
    rate_limit_info JSONB DEFAULT '{}',
    quota_usage JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS ix_platform_configurations_org_id ON platform_configurations(org_id);
CREATE INDEX IF NOT EXISTS ix_platform_configurations_platform ON platform_configurations(platform);
CREATE INDEX IF NOT EXISTS ix_platform_configurations_org_platform ON platform_configurations(org_id, platform);

-- Ensure one configuration per platform per organization
-- Check if constraint already exists before adding it
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'uq_platform_config_org_platform' 
        AND table_name = 'platform_configurations'
    ) THEN
        ALTER TABLE platform_configurations ADD CONSTRAINT uq_platform_config_org_platform UNIQUE (org_id, platform);
    END IF;
END $$;

-- Add comments
COMMENT ON TABLE platform_configurations IS 'Stores encrypted platform credentials and configuration for each organization';
COMMENT ON COLUMN platform_configurations.configuration IS 'Encrypted JSON object containing platform-specific credentials and settings';
COMMENT ON COLUMN platform_configurations.last_test_status IS 'Result of last connection test: success, failed, partial';
