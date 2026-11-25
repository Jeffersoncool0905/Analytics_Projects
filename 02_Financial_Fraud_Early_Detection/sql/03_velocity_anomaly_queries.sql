-- ====================================================================
-- PROJECT: Financial & E-Commerce Fraud Early Detection Analysis
-- SCRIPT: 03_velocity_anomaly_queries.sql
-- DESCRIPTION: Real-Time Velocity, Geospatial Impossible Travel, and Behavioral Spikes
-- AUTHOR: Jefferson & Analytics Team
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: "Impossible Travel" Geolocation Anomaly Detection
-- Detects card swipes separated by distances requiring supersonic flight (> 800 km/h)
-- --------------------------------------------------------------------
WITH consecutive_swipes AS (
    SELECT 
        f.transaction_id,
        f.customer_id,
        f.trans_timestamp,
        m.merchant_name,
        m.merchant_country,
        f.distance_km,
        f.transaction_amount,
        f.is_fraud,
        LAG(f.trans_timestamp) OVER (PARTITION BY f.customer_id ORDER BY f.trans_timestamp) AS prev_trans_timestamp,
        LAG(f.distance_km) OVER (PARTITION BY f.customer_id ORDER BY f.trans_timestamp) AS prev_distance_km,
        LAG(m.merchant_country) OVER (PARTITION BY f.customer_id ORDER BY f.trans_timestamp) AS prev_country
    FROM fact_transactions f
    JOIN dim_merchants m ON f.merchant_key = m.merchant_key
),
speed_calculations AS (
    SELECT 
        transaction_id,
        customer_id,
        trans_timestamp,
        prev_trans_timestamp,
        merchant_name,
        merchant_country,
        prev_country,
        transaction_amount,
        is_fraud,
        -- Absolute difference in distance
        ABS(distance_km - COALESCE(prev_distance_km, distance_km)) AS delta_distance_km,
        -- Elapsed hours
        (JULIANDAY(trans_timestamp) - JULIANDAY(prev_trans_timestamp)) * 24.0 AS elapsed_hours
    FROM consecutive_swipes
    WHERE prev_trans_timestamp IS NOT NULL
)
SELECT 
    transaction_id,
    customer_id,
    trans_timestamp,
    prev_country || ' -> ' || merchant_country AS geographic_hop,
    ROUND(delta_distance_km, 1) AS distance_traveled_km,
    ROUND(elapsed_hours, 2) AS elapsed_hours,
    ROUND(delta_distance_km / NULLIF(elapsed_hours, 0), 1) AS required_speed_kmh,
    transaction_amount,
    CASE WHEN (delta_distance_km / NULLIF(elapsed_hours, 0)) > 800.0 THEN 'ALERT: Impossible Travel Anomaly' ELSE 'Normal Speed' END AS velocity_alert,
    is_fraud
FROM speed_calculations
WHERE (delta_distance_km / NULLIF(elapsed_hours, 0)) > 800.0
ORDER BY required_speed_kmh DESC;


-- --------------------------------------------------------------------
-- QUERY 2: Card Testing Velocity Spikes
-- Detects 3+ transactions on the same card within a rolling 60-minute window
-- --------------------------------------------------------------------
SELECT 
    f.customer_id,
    c.card_number_masked,
    f.trans_timestamp,
    m.merchant_name,
    m.merchant_category,
    f.transaction_amount,
    f.trans_count_last_1h,
    f.fraud_scenario,
    f.is_fraud
FROM fact_transactions f
JOIN dim_cards c ON f.card_key = c.card_key
JOIN dim_merchants m ON f.merchant_key = m.merchant_key
WHERE f.trans_count_last_1h >= 3
ORDER BY f.customer_id, f.trans_timestamp;


-- --------------------------------------------------------------------
-- QUERY 3: Sudden High-Value Spending Outliers
-- Compares transaction ticket size against customer 30-day baseline average
-- --------------------------------------------------------------------
SELECT 
    f.transaction_id,
    f.customer_id,
    f.trans_timestamp,
    m.merchant_name,
    m.merchant_category,
    f.transaction_amount,
    cust.customer_avg_ticket,
    f.amount_to_avg_ratio,
    f.fraud_probability,
    f.fraud_risk_tier
FROM fact_transactions f
JOIN dim_customers cust ON f.customer_id = cust.customer_id
JOIN dim_merchants m ON f.merchant_key = m.merchant_key
WHERE f.amount_to_avg_ratio >= 4.0
ORDER BY f.amount_to_avg_ratio DESC;
