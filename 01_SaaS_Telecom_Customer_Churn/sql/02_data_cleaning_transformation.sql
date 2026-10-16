-- ====================================================================
-- PROJECT: SaaS / Telecom Customer Churn & Retention Analytics
-- SCRIPT: 02_data_cleaning_transformation.sql
-- DESCRIPTION: Data Cleaning, Standardization, and Star Schema Population
-- AUTHOR: Jefferson
-- ====================================================================

-- 1. Data Quality Checks & Data Profiling
-- Check for NULLs or duplicate customer IDs
SELECT 
    customer_id, 
    COUNT(*) AS record_count
FROM stg_customer_churn
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for missing values in critical billing fields
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN monthly_charges IS NULL THEN 1 ELSE 0 END) AS missing_monthly_charges,
    SUM(CASE WHEN total_charges IS NULL THEN 1 ELSE 0 END) AS missing_total_charges,
    SUM(CASE WHEN tenure_months IS NULL THEN 1 ELSE 0 END) AS missing_tenure
FROM stg_customer_churn;

-- 2. Populate Dimension: dim_customers
INSERT INTO dim_customers (
    customer_id,
    signup_date,
    gender,
    is_senior_citizen,
    has_partner,
    has_dependents
)
SELECT 
    TRIM(customer_id) AS customer_id,
    signup_date,
    TRIM(gender) AS gender,
    CASE WHEN senior_citizen = 1 THEN TRUE ELSE FALSE END AS is_senior_citizen,
    CASE WHEN LOWER(TRIM(partner)) = 'yes' THEN TRUE ELSE FALSE END AS has_partner,
    CASE WHEN LOWER(TRIM(dependents)) = 'yes' THEN TRUE ELSE FALSE END AS has_dependents
FROM stg_customer_churn;

-- 3. Populate Dimension: dim_contracts (Distinct combinations)
INSERT INTO dim_contracts (
    contract_key,
    contract_type,
    paperless_billing,
    payment_method
)
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
) c_sub;

-- 4. Populate Dimension: dim_services (Distinct service bundles)
INSERT INTO dim_services (
    service_key,
    phone_service,
    multiple_lines,
    internet_service,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies
)
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
) s_sub;

-- 5. Populate Fact Table: fact_subscriptions
INSERT INTO fact_subscriptions (
    subscription_id,
    customer_id,
    contract_key,
    service_key,
    tenure_months,
    tenure_bracket,
    monthly_charges,
    total_charges,
    support_tickets,
    monthly_usage_gb,
    churn_status,
    churn_reason,
    churn_probability,
    predicted_churn,
    churn_risk_tier,
    expected_mrr_loss
)
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
    -- Expected MRR Loss = Monthly Charges * Predicted Churn Probability
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
