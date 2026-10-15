-- Climate Change Dashboard - SQL Data Model
-- SQL queries for dashboard development and KPI calculations

-- ============================================
-- 1. CREATE BASE TABLES
-- ============================================

-- Main climate data table
CREATE TABLE climate_data (
    year INT PRIMARY KEY,
    global_temp_anomaly DECIMAL(10, 6),
    co2_ppm DECIMAL(10, 2),
    methane_ppb DECIMAL(10, 2),
    sea_level_mm DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Decade dimension table
CREATE TABLE dim_decade (
    decade INT PRIMARY KEY,
    decade_label VARCHAR(20),
    start_year INT,
    end_year INT
);

-- ============================================
-- 2. KEY PERFORMANCE INDICATORS (KPIs)
-- ============================================

-- Current temperature anomaly
CREATE VIEW kpi_current_temperature AS
SELECT 
    year,
    global_temp_anomaly as current_temp_anomaly,
    CONCAT('+', ROUND(global_temp_anomaly, 2), '°C') as formatted_value
FROM climate_data
WHERE year = (SELECT MAX(year) FROM climate_data);

-- Current CO2 level
CREATE VIEW kpi_current_co2 AS
SELECT 
    year,
    co2_ppm as current_co2,
    CONCAT(ROUND(co2_ppm, 1), ' ppm') as formatted_value
FROM climate_data
WHERE year = (SELECT MAX(year) FROM climate_data);

-- Total sea level rise
CREATE VIEW kpi_sea_level_rise AS
SELECT 
    MAX(sea_level_mm) - MIN(sea_level_mm) as total_rise,
    CONCAT(ROUND(MAX(sea_level_mm) - MIN(sea_level_mm), 0), ' mm') as formatted_value
FROM climate_data;

-- Average warming rate (°C per year)
CREATE VIEW kpi_warming_rate AS
SELECT 
    (MAX(global_temp_anomaly) - MIN(global_temp_anomaly)) / 
    (MAX(year) - MIN(year)) as warming_rate_per_year,
    CONCAT('+', ROUND((MAX(global_temp_anomaly) - MIN(global_temp_anomaly)) / 
           (MAX(year) - MIN(year)), 6), '°C/yr') as formatted_value
FROM climate_data;

-- CO2 growth rate (ppm per year)
CREATE VIEW kpi_co2_growth_rate AS
SELECT 
    (MAX(co2_ppm) - MIN(co2_ppm)) / 
    (MAX(year) - MIN(year)) as co2_growth_rate,
    CONCAT(ROUND((MAX(co2_ppm) - MIN(co2_ppm)) / 
           (MAX(year) - MIN(year)), 4), ' ppm/yr') as formatted_value
FROM climate_data;

-- ============================================
-- 3. TREND ANALYSIS QUERIES
-- ============================================

-- Temperature trend with moving averages
CREATE VIEW temperature_trend AS
SELECT 
    year,
    global_temp_anomaly,
    AVG(global_temp_anomaly) OVER (
        ORDER BY year 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) as ma_5year,
    AVG(global_temp_anomaly) OVER (
        ORDER BY year 
        ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
    ) as ma_10year
FROM climate_data
ORDER BY year;

-- CO2 trend with growth rate
CREATE VIEW co2_trend AS
SELECT 
    year,
    co2_ppm,
    co2_ppm - LAG(co2_ppm, 1) OVER (ORDER BY year) as year_over_year_change,
    AVG(co2_ppm) OVER (
        ORDER BY year 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) as ma_5year
FROM climate_data
ORDER BY year;

-- ============================================
-- 4. DECADE AGGREGATIONS
-- ============================================

-- Decade summary statistics
CREATE VIEW decade_summary AS
SELECT 
    FLOOR(year / 10) * 10 as decade,
    COUNT(*) as num_years,
    AVG(global_temp_anomaly) as avg_temp_anomaly,
    AVG(co2_ppm) as avg_co2,
    AVG(methane_ppb) as avg_methane,
    AVG(sea_level_mm) as avg_sea_level,
    MIN(global_temp_anomaly) as min_temp,
    MAX(global_temp_anomaly) as max_temp
FROM climate_data
GROUP BY decade
ORDER BY decade;

-- Decade comparison (change from previous decade)
CREATE VIEW decade_comparison AS
SELECT 
    d1.decade,
    d1.avg_temp_anomaly,
    d1.avg_temp_anomaly - d2.avg_temp_anomaly as temp_change_from_prev,
    d1.avg_co2,
    d1.avg_co2 - d2.avg_co2 as co2_change_from_prev
FROM decade_summary d1
LEFT JOIN decade_summary d2 ON d1.decade = d2.decade + 10
ORDER BY d1.decade;

-- ============================================
-- 5. CORRELATION ANALYSIS
-- ============================================

-- Correlation coefficients (requires statistical functions)
-- Note: Implementation depends on database system

-- Pearson correlation: CO2 vs Temperature
CREATE VIEW correlation_co2_temp AS
SELECT 
    COUNT(*) as n,
    (COUNT(*) * SUM(co2_ppm * global_temp_anomaly) - 
     SUM(co2_ppm) * SUM(global_temp_anomaly)) /
    SQRT((COUNT(*) * SUM(co2_ppm * co2_ppm) - SUM(co2_ppm) * SUM(co2_ppm)) *
         (COUNT(*) * SUM(global_temp_anomaly * global_temp_anomaly) - 
          SUM(global_temp_anomaly) * SUM(global_temp_anomaly))) as correlation_coefficient
FROM climate_data;

-- ============================================
-- 6. TIME SERIES QUERIES
-- ============================================

-- Latest 10 years
CREATE VIEW recent_decade AS
SELECT *
FROM climate_data
WHERE year >= (SELECT MAX(year) - 9 FROM climate_data)
ORDER BY year DESC;

-- Historical periods comparison
CREATE VIEW period_comparison AS
SELECT 
    CASE 
        WHEN year BETWEEN 1924 AND 1949 THEN '1924-1949 (Early)'
        WHEN year BETWEEN 1950 AND 1974 THEN '1950-1974 (Mid)'
        WHEN year BETWEEN 1975 AND 1999 THEN '1975-1999 (Late)'
        WHEN year BETWEEN 2000 AND 2023 THEN '2000-2023 (Recent)'
    END as period,
    COUNT(*) as years,
    AVG(global_temp_anomaly) as avg_temp,
    AVG(co2_ppm) as avg_co2,
    AVG(methane_ppb) as avg_methane,
    AVG(sea_level_mm) as avg_sea_level
FROM climate_data
GROUP BY period
ORDER BY MIN(year);

-- ============================================
-- 7. ANOMALY DETECTION
-- ============================================

-- Identify years with extreme values
CREATE VIEW extreme_years AS
SELECT 
    year,
    global_temp_anomaly,
    co2_ppm,
    CASE 
        WHEN global_temp_anomaly > (
            SELECT AVG(global_temp_anomaly) + 2 * STDDEV(global_temp_anomaly) 
            FROM climate_data
        ) THEN 'Extremely High Temperature'
        WHEN global_temp_anomaly < (
            SELECT AVG(global_temp_anomaly) - 2 * STDDEV(global_temp_anomaly) 
            FROM climate_data
        ) THEN 'Extremely Low Temperature'
        ELSE 'Normal'
    END as temp_category
FROM climate_data
WHERE global_temp_anomaly > (
    SELECT AVG(global_temp_anomaly) + 2 * STDDEV(global_temp_anomaly) 
    FROM climate_data
) OR global_temp_anomaly < (
    SELECT AVG(global_temp_anomaly) - 2 * STDDEV(global_temp_anomaly) 
    FROM climate_data
)
ORDER BY ABS(global_temp_anomaly - (SELECT AVG(global_temp_anomaly) FROM climate_data)) DESC;

-- ============================================
-- 8. DASHBOARD DATA FEEDS
-- ============================================

-- Main dashboard data feed
CREATE VIEW dashboard_main_feed AS
SELECT 
    cd.year,
    cd.global_temp_anomaly,
    cd.co2_ppm,
    cd.methane_ppb,
    cd.sea_level_mm,
    FLOOR(cd.year / 10) * 10 as decade,
    -- Normalized values (0-1 scale)
    (cd.global_temp_anomaly - min_vals.min_temp) / 
        (max_vals.max_temp - min_vals.min_temp) as norm_temp,
    (cd.co2_ppm - min_vals.min_co2) / 
        (max_vals.max_co2 - min_vals.min_co2) as norm_co2,
    (cd.methane_ppb - min_vals.min_methane) / 
        (max_vals.max_methane - min_vals.min_methane) as norm_methane,
    (cd.sea_level_mm - min_vals.min_sea) / 
        (max_vals.max_sea - min_vals.min_sea) as norm_sea_level
FROM climate_data cd
CROSS JOIN (
    SELECT 
        MIN(global_temp_anomaly) as min_temp,
        MIN(co2_ppm) as min_co2,
        MIN(methane_ppb) as min_methane,
        MIN(sea_level_mm) as min_sea
    FROM climate_data
) min_vals
CROSS JOIN (
    SELECT 
        MAX(global_temp_anomaly) as max_temp,
        MAX(co2_ppm) as max_co2,
        MAX(methane_ppb) as max_methane,
        MAX(sea_level_mm) as max_sea
    FROM climate_data
) max_vals
ORDER BY cd.year;

-- ============================================
-- 9. SUMMARY CARD DATA
-- ============================================

-- All KPIs in one query for dashboard cards
CREATE VIEW dashboard_kpis AS
SELECT 
    (SELECT formatted_value FROM kpi_current_temperature) as current_temp,
    (SELECT formatted_value FROM kpi_current_co2) as current_co2,
    (SELECT formatted_value FROM kpi_sea_level_rise) as sea_level_rise,
    (SELECT formatted_value FROM kpi_warming_rate) as warming_rate,
    (SELECT formatted_value FROM kpi_co2_growth_rate) as co2_growth,
    (SELECT MAX(year) FROM climate_data) as latest_year,
    (SELECT COUNT(*) FROM climate_data) as total_years;

-- ============================================
-- 10. DATA QUALITY CHECKS
-- ============================================

-- Check for missing years
CREATE VIEW missing_years AS
WITH RECURSIVE year_series AS (
    SELECT MIN(year) as year FROM climate_data
    UNION ALL
    SELECT year + 1 FROM year_series
    WHERE year < (SELECT MAX(year) FROM climate_data)
)
SELECT ys.year
FROM year_series ys
LEFT JOIN climate_data cd ON ys.year = cd.year
WHERE cd.year IS NULL;

-- Check for NULL values
CREATE VIEW data_quality_check AS
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN global_temp_anomaly IS NULL THEN 1 ELSE 0 END) as null_temp,
    SUM(CASE WHEN co2_ppm IS NULL THEN 1 ELSE 0 END) as null_co2,
    SUM(CASE WHEN methane_ppb IS NULL THEN 1 ELSE 0 END) as null_methane,
    SUM(CASE WHEN sea_level_mm IS NULL THEN 1 ELSE 0 END) as null_sea_level
FROM climate_data;

-- ============================================
-- USAGE EXAMPLES
-- ============================================

-- Query all KPIs
-- SELECT * FROM dashboard_kpis;

-- Get temperature trend
-- SELECT * FROM temperature_trend;

-- Compare decades
-- SELECT * FROM decade_comparison;

-- Get correlation
-- SELECT * FROM correlation_co2_temp;
