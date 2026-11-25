-- ====================================================================
-- PROJECT: Financial & E-Commerce Fraud Early Detection Analysis
-- SCRIPT: 04_investigation_priority_views.sql
-- DESCRIPTION: Fraud Operations Priority Queue & Confusion Matrix Views
-- AUTHOR: Jefferson & Analytics Team
-- ====================================================================

-- --------------------------------------------------------------------
-- VIEW 1: Daily Fraud Analyst Triage Queue
-- Flags pending transactions prioritized by Expected Fraud Loss
-- --------------------------------------------------------------------
DROP VIEW IF EXISTS v_fraud_investigation_queue;
CREATE VIEW v_fraud_investigation_queue AS
SELECT 
    DENSE_RANK() OVER (ORDER BY f.expected_fraud_loss DESC, f.fraud_probability DESC) AS queue_priority_rank,
    f.transaction_id,
    f.trans_timestamp,
    f.customer_id,
    c.card_type,
    c.card_entry_mode,
    m.merchant_name,
    m.merchant_category,
    f.transaction_amount,
    f.fraud_probability,
    f.fraud_risk_tier,
    f.expected_fraud_loss,
    f.fraud_scenario
FROM fact_transactions f
JOIN dim_cards c ON f.card_key = c.card_key
JOIN dim_merchants m ON f.merchant_key = m.merchant_key
WHERE f.fraud_risk_tier = 'High Risk';

-- Query Top 20 Urgent Cases for Daily Review
SELECT * FROM v_fraud_investigation_queue WHERE queue_priority_rank <= 20;


-- --------------------------------------------------------------------
-- VIEW 2: SQL Confusion Matrix & Financial Cost Evaluation
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN is_fraud = 1 AND predicted_fraud = 1 THEN 'True Positive (Fraud Caught & Prevented)'
        WHEN is_fraud = 0 AND predicted_fraud = 0 THEN 'True Negative (Legitimate Transaction Approved)'
        WHEN is_fraud = 0 AND predicted_fraud = 1 THEN 'False Positive (False Alarm / Customer Friction)'
        WHEN is_fraud = 1 AND predicted_fraud = 0 THEN 'False Negative (Missed Fraud / Chargeback Loss)'
    END AS classification_outcome,
    COUNT(*) AS transaction_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_transactions), 2) AS pct_of_total_volume,
    ROUND(SUM(transaction_amount), 2) AS total_financial_volume
FROM fact_transactions
GROUP BY 
    CASE 
        WHEN is_fraud = 1 AND predicted_fraud = 1 THEN 'True Positive (Fraud Caught & Prevented)'
        WHEN is_fraud = 0 AND predicted_fraud = 0 THEN 'True Negative (Legitimate Transaction Approved)'
        WHEN is_fraud = 0 AND predicted_fraud = 1 THEN 'False Positive (False Alarm / Customer Friction)'
        WHEN is_fraud = 1 AND predicted_fraud = 0 THEN 'False Negative (Missed Fraud / Chargeback Loss)'
    END
ORDER BY transaction_count DESC;


-- --------------------------------------------------------------------
-- VIEW 3: Merchant Category Fraud Concentration & Vulnerability
-- --------------------------------------------------------------------
SELECT 
    m.merchant_category,
    COUNT(f.transaction_id) AS total_transactions,
    SUM(f.is_fraud) AS fraud_cases,
    ROUND(SUM(f.is_fraud) * 100.0 / COUNT(f.transaction_id), 2) AS fraud_rate_pct,
    ROUND(SUM(f.transaction_amount), 2) AS gross_transaction_volume,
    ROUND(SUM(CASE WHEN f.is_fraud = 1 THEN f.transaction_amount ELSE 0 END), 2) AS fraud_dollar_losses
FROM fact_transactions f
JOIN dim_merchants m ON f.merchant_key = m.merchant_key
GROUP BY m.merchant_category
ORDER BY fraud_dollar_losses DESC;
