-- ====================================================================
-- PROJECT: Financial & E-Commerce Fraud Early Detection Analysis
-- SCRIPT: 02_data_cleaning_transformation.sql
-- DESCRIPTION: Data Cleansing, Normalization & ETL into Star Schema
-- AUTHOR: Jefferson & Analytics Team
-- ====================================================================

-- 1. Data Integrity & Profiling
SELECT 
    COUNT(*) AS total_ingested_rows,
    SUM(CASE WHEN transaction_amount <= 0 THEN 1 ELSE 0 END) AS invalid_amounts,
    SUM(CASE WHEN trans_timestamp IS NULL THEN 1 ELSE 0 END) AS missing_timestamps,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) AS missing_customer_ids
FROM stg_transactions;

-- 2. Populate Dimension: dim_customers
INSERT INTO dim_customers (customer_id, customer_home_country, customer_avg_ticket)
SELECT 
    customer_id,
    customer_home_country,
    ROUND(AVG(customer_avg_ticket), 2) AS customer_avg_ticket
FROM stg_transactions
GROUP BY customer_id, customer_home_country;

-- 3. Populate Dimension: dim_cards
INSERT INTO dim_cards (card_key, card_number_masked, card_type, card_entry_mode)
SELECT 
    ROW_NUMBER() OVER (ORDER BY card_type, card_entry_mode, card_number_masked) AS card_key,
    card_number_masked,
    card_type,
    card_entry_mode
FROM (
    SELECT DISTINCT card_number_masked, card_type, card_entry_mode
    FROM stg_transactions
) sub_cards;

-- 4. Populate Dimension: dim_merchants
INSERT INTO dim_merchants (merchant_key, merchant_name, merchant_category, merchant_country)
SELECT 
    ROW_NUMBER() OVER (ORDER BY merchant_category, merchant_name) AS merchant_key,
    merchant_name,
    merchant_category,
    merchant_country
FROM (
    SELECT DISTINCT merchant_name, merchant_category, merchant_country
    FROM stg_transactions
) sub_merchants;

-- 5. Populate Dimension: dim_devices
INSERT INTO dim_devices (device_key, device_type)
SELECT 
    ROW_NUMBER() OVER (ORDER BY device_type) AS device_key,
    device_type
FROM (
    SELECT DISTINCT device_type
    FROM stg_transactions
) sub_devices;

-- 6. Populate Fact Table: fact_transactions
INSERT INTO fact_transactions (
    transaction_id,
    trans_timestamp,
    customer_id,
    card_key,
    merchant_key,
    device_key,
    transaction_amount,
    amount_to_avg_ratio,
    distance_km,
    trans_count_last_1h,
    is_foreign_transaction,
    is_fraud,
    fraud_scenario,
    fraud_probability,
    predicted_fraud,
    fraud_risk_tier,
    expected_fraud_loss
)
SELECT 
    s.transaction_id,
    s.trans_timestamp,
    s.customer_id,
    c.card_key,
    m.merchant_key,
    d.device_key,
    s.transaction_amount,
    s.amount_to_avg_ratio,
    s.distance_km,
    s.trans_count_last_1h,
    s.is_foreign_transaction,
    s.is_fraud,
    s.fraud_scenario,
    s.fraud_probability,
    s.predicted_fraud,
    s.fraud_risk_tier,
    s.expected_fraud_loss
FROM stg_transactions s
JOIN dim_cards c 
    ON s.card_number_masked = c.card_number_masked
   AND s.card_type = c.card_type
   AND s.card_entry_mode = c.card_entry_mode
JOIN dim_merchants m 
    ON s.merchant_name = m.merchant_name
   AND s.merchant_category = m.merchant_category
   AND s.merchant_country = m.merchant_country
JOIN dim_devices d 
    ON s.device_type = d.device_type;
