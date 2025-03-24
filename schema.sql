-- Main table for call records
CREATE TABLE IF NOT EXISTS calls (
    record_id INTEGER PRIMARY KEY,
    call_key TEXT UNIQUE,
    call_date_time DATETIME,
    priority TEXT,
    district TEXT,
    description TEXT,
    call_number TEXT,
    incident_location TEXT,
    location TEXT,
    zip_code TEXT,
    needs_sync INTEGER,
    esri_oid INTEGER
);

-- Geographic information table
CREATE TABLE IF NOT EXISTS geography (
    call_key TEXT PRIMARY KEY,
    neighborhood TEXT,
    police_district TEXT,
    police_post TEXT,
    council_district INTEGER,
    sheriff_districts TEXT,
    community_statistical_areas TEXT,
    census_tracts TEXT,
    FOREIGN KEY (call_key) REFERENCES calls(call_key)
);

-- Create views for common analyses
CREATE VIEW IF NOT EXISTS calls_per_district AS
SELECT district, COUNT(*) as call_count
FROM calls
GROUP BY district
ORDER BY call_count DESC;

CREATE VIEW IF NOT EXISTS calls_by_priority AS
SELECT priority, COUNT(*) as call_count
FROM calls
GROUP BY priority
ORDER BY call_count DESC;

CREATE VIEW IF NOT EXISTS calls_by_description AS
SELECT description, COUNT(*) as call_count
FROM calls
GROUP BY description
ORDER BY call_count DESC;

CREATE VIEW IF NOT EXISTS calls_by_hour AS
SELECT strftime('%H', call_date_time) as hour, COUNT(*) as call_count
FROM calls
GROUP BY hour
ORDER BY hour;
