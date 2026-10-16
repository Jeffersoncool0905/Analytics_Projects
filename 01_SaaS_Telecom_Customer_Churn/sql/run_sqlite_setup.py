"""
Load clean & scored churn data into local SQLite database (telecom_churn.db)
Author: Jefferson
Executes the schema and validates key SQL analytical queries.
"""

import sqlite3
import pandas as pd

# Load scored dataset
csv_path = "01_SaaS_Telecom_Customer_Churn/data/processed/telecom_customer_churn_with_predictions.csv"
df = pd.read_csv(csv_path)

db_path = "01_SaaS_Telecom_Customer_Churn/sql/telecom_churn.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Load Staging Table
df.to_sql("stg_customer_churn", conn, if_exists="replace", index=False)
print("Staging table stg_customer_churn created.")

# 2. Populate dim_customers
cursor.execute("""
DROP TABLE IF EXISTS dim_customers;
""")
cursor.execute("""
CREATE TABLE dim_customers AS
SELECT 
    TRIM(customer_id) AS customer_id,
    signup_date,
    TRIM(gender) AS gender,
    CASE WHEN senior_citizen = 1 THEN 1 ELSE 0 END AS is_senior_citizen,
    CASE WHEN LOWER(TRIM(partner)) = 'yes' THEN 1 ELSE 0 END AS has_partner,
    CASE WHEN LOWER(TRIM(dependents)) = 'yes' THEN 1 ELSE 0 END AS has_dependents
FROM stg_customer_churn;
""")

# 3. Populate dim_contracts
cursor.execute("""
DROP TABLE IF EXISTS dim_contracts;
""")
cursor.execute("""
CREATE TABLE dim_contracts AS
SELECT 
    ROW_NUMBER() OVER(ORDER BY contract_type, payment_method, paperless_billing) AS contract_key,
    contract_type,
    paperless_billing,
    payment_method
FROM (
    SELECT DISTINCT 
        TRIM(contract_type) AS contract_type,
        TRIM(paperless_billing) AS paperless_billing,
        TRIM(payment_method) AS payment_method
    FROM stg_customer_churn
);
""")

# 4. Populate dim_services
cursor.execute("""
DROP TABLE IF EXISTS dim_services;
""")
cursor.execute("""
CREATE TABLE dim_services AS
SELECT 
    ROW_NUMBER() OVER(ORDER BY internet_service, phone_service, tech_support) AS service_key,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies
FROM (
    SELECT DISTINCT
        TRIM(phone_service) AS phone_service,
        TRIM(multiple_lines) AS multiple_lines,
        TRIM(internet_service) AS internet_service,
        TRIM(online_security) AS online_security,
        TRIM(online_backup) AS online_backup,
        TRIM(device_protection) AS device_protection,
        TRIM(tech_support) AS tech_support,
        TRIM(streaming_tv) AS streaming_tv,
        TRIM(streaming_movies) AS streaming_movies
    FROM stg_customer_churn
);
""")

# 5. Populate fact_subscriptions
cursor.execute("""
DROP TABLE IF EXISTS fact_subscriptions;
""")
cursor.execute("""
CREATE TABLE fact_subscriptions AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY s.customer_id) AS subscription_id,
    s.customer_id,
    c.contract_key,
    srv.service_key,
    s.tenure_months,
    CASE 
        WHEN s.tenure_months <= 12 THEN '0-12 Months'
        WHEN s.tenure_months <= 24 THEN '13-24 Months'
        WHEN s.tenure_months <= 48 THEN '25-48 Months'
        ELSE '49+ Months'
    END AS tenure_bracket,
    s.monthly_charges,
    COALESCE(s.total_charges, s.monthly_charges * s.tenure_months) AS total_charges,
    COALESCE(s.support_tickets, 0) AS support_tickets,
    COALESCE(s.monthly_usage_gb, 0.0) AS monthly_usage_gb,
    s.churn_status,
    COALESCE(s.churn_reason, 'Active Customer') AS churn_reason,
    s.churn_probability,
    s.predicted_churn,
    s.churn_risk_tier,
    ROUND(s.monthly_charges * s.churn_probability, 2) AS expected_mrr_loss
FROM stg_customer_churn s
JOIN dim_contracts c 
    ON TRIM(s.contract_type) = c.contract_type
   AND TRIM(s.paperless_billing) = c.paperless_billing
   AND TRIM(s.payment_method) = c.payment_method
JOIN dim_services srv
    ON TRIM(s.phone_service) = srv.phone_service
   AND TRIM(s.multiple_lines) = srv.multiple_lines
   AND TRIM(s.internet_service) = srv.internet_service
   AND TRIM(s.online_security) = srv.online_security
   AND TRIM(s.online_backup) = srv.online_backup
   AND TRIM(s.device_protection) = srv.device_protection
   AND TRIM(s.tech_support) = srv.tech_support
   AND TRIM(s.streaming_tv) = srv.streaming_tv
   AND TRIM(s.streaming_movies) = srv.streaming_movies;
""")

conn.commit()
print("Fact and dimension tables populated successfully in telecom_churn.db.")

# Test Query 1: Executive KPIs
kpi_df = pd.read_sql("""
SELECT 
    COUNT(f.customer_id) AS total_customers,
    SUM(CASE WHEN f.churn_status = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    SUM(CASE WHEN f.churn_status = 'No' THEN 1 ELSE 0 END) AS active_customers,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(f.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(f.monthly_charges), 2) AS total_mrr,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN f.monthly_charges ELSE 0 END), 2) AS mrr_lost_to_churn
FROM fact_subscriptions f;
""", conn)

print("\n=== SQL KPI QUERY OUTPUT ===")
print(kpi_df)

conn.close()
