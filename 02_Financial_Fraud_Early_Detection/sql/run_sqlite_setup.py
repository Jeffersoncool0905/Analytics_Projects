"""
Populate SQLite database (fraud_analytics.db) with Star Schema & validate views.
Author: Jefferson & Analytics Team
"""

import sqlite3
import pandas as pd

# Load scored dataset
csv_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/data/processed/transactions_with_fraud_scores.csv"
df = pd.read_csv(csv_path)

db_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/sql/fraud_analytics.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Staging Table
df.to_sql("stg_transactions", conn, if_exists="replace", index=False)
print("Staging table stg_transactions loaded.")

# 2. Populate dim_customers
cursor.execute("DROP TABLE IF EXISTS dim_customers;")
cursor.execute("""
CREATE TABLE dim_customers AS
SELECT 
    customer_id,
    customer_home_country,
    ROUND(AVG(customer_avg_ticket), 2) AS customer_avg_ticket
FROM stg_transactions
GROUP BY customer_id, customer_home_country;
""")

# 3. Populate dim_cards
cursor.execute("DROP TABLE IF EXISTS dim_cards;")
cursor.execute("""
CREATE TABLE dim_cards AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY card_type, card_entry_mode, card_number_masked) AS card_key,
    card_number_masked,
    card_type,
    card_entry_mode
FROM (
    SELECT DISTINCT card_number_masked, card_type, card_entry_mode
    FROM stg_transactions
);
""")

# 4. Populate dim_merchants
cursor.execute("DROP TABLE IF EXISTS dim_merchants;")
cursor.execute("""
CREATE TABLE dim_merchants AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY merchant_category, merchant_name) AS merchant_key,
    merchant_name,
    merchant_category,
    merchant_country
FROM (
    SELECT DISTINCT merchant_name, merchant_category, merchant_country
    FROM stg_transactions
);
""")

# 5. Populate dim_devices
cursor.execute("DROP TABLE IF EXISTS dim_devices;")
cursor.execute("""
CREATE TABLE dim_devices AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY device_type) AS device_key,
    device_type
FROM (
    SELECT DISTINCT device_type
    FROM stg_transactions
);
""")

# 6. Populate fact_transactions
cursor.execute("DROP TABLE IF EXISTS fact_transactions;")
cursor.execute("""
CREATE TABLE fact_transactions AS
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
""")

conn.commit()
print("Star schema created successfully in fraud_analytics.db.")

# Test KPI query
test_df = pd.read_sql("""
SELECT 
    COUNT(*) AS total_txns,
    SUM(is_fraud) AS fraud_cases,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 2) AS fraud_rate_pct,
    ROUND(SUM(transaction_amount), 2) AS total_volume,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN transaction_amount ELSE 0 END), 2) AS fraud_volume
FROM fact_transactions;
""", conn)
print("\n=== SQL FRAUD KPI SUMMARY ===")
print(test_df)

conn.close()
