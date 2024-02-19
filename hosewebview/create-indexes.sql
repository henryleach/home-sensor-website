-- Create indexes on the long tables
CREATE INDEX IF NOT EXISTS idx_temperature_timestamp
ON temperature(timestamp_utc);

CREATE INDEX IF NOT EXISTS idx_meteotemps_timestamp
ON meteoTemps(timestamp_utc);

-- CREATE INDEX IF NOT EXISTS idx_gasuse_timestamp
-- ON gasUse(timestamp_utc);

