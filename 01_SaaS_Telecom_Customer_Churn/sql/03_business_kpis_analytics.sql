-- ====================================================================
-- PROJECT: SaaS / Telecom Customer Churn & Retention Analytics
-- SCRIPT: 03_business_kpis_analytics.sql
-- DESCRIPTION: Advanced SQL Business Intelligence Queries & Strategic Analytics
-- AUTHOR: Jefferson
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Executive KPI Dashboard Summary
-- --------------------------------------------------------------------
SELECT 
    COUNT(f.customer_id) AS total_customers,
    SUM(CASE WHEN f.churn_status = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    SUM(CASE WHEN f.churn_status = 'No' THEN 1 ELSE 0 END) AS active_customers,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(f.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(f.monthly_charges), 2) AS total_mrr,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN f.monthly_charges ELSE 0 END), 2) AS mrr_lost_to_churn,
    ROUND(AVG(f.monthly_charges), 2) AS arpu,
    ROUND(AVG(f.tenure_months), 1) AS avg_tenure_months
FROM fact_subscriptions f;


-- --------------------------------------------------------------------
-- QUERY 2: Churn & Financial Exposure by Contract Type
-- --------------------------------------------------------------------
SELECT 
    c.contract_type,
    COUNT(f.customer_id) AS total_accounts,
    SUM(CASE WHEN f.churn_status = 'Yes' THEN 1 ELSE 0 END) AS churned_accounts,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(f.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(SUM(f.monthly_charges), 2) AS total_mrr,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN f.monthly_charges ELSE 0 END), 2) AS churned_mrr,
    ROUND(AVG(f.tenure_months), 1) AS avg_tenure_months
FROM fact_subscriptions f
JOIN dim_contracts c ON f.contract_key = c.contract_key
GROUP BY c.contract_type
ORDER BY churn_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 3: The "Security & Support Shield" Analysis
-- Evaluating how Tech Support & Online Security mitigate churn
-- --------------------------------------------------------------------
SELECT 
    s.internet_service,
    s.tech_support,
    s.online_security,
    COUNT(f.customer_id) AS subscriber_count,
    ROUND(SUM(CASE WHEN f.churn_status = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(f.customer_id) * 100, 2) AS churn_rate_pct,
    ROUND(AVG(f.monthly_charges), 2) AS avg_monthly_bill
FROM fact_subscriptions f
JOIN dim_services s ON f.service_key = s.service_key
WHERE s.internet_service <> 'No'
GROUP BY s.internet_service, s.tech_support, s.online_security
ORDER BY s.internet_service, churn_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 4: Customer Spending Quartiles & ARPU Tiering (Window Function NTILE)
-- --------------------------------------------------------------------
WITH customer_spending_quartiles AS (
    SELECT 
        customer_id,
        monthly_charges,
        total_charges,
        tenure_months,
        churn_status,
        NTILE(4) OVER (ORDER BY monthly_charges DESC) AS spending_quartile
    FROM fact_subscriptions
)
SELECT 
    CASE spending_quartile
        WHEN 1 THEN 'Tier 1 - Highest Spenders (Top 25%)'
        WHEN 2 THEN 'Tier 2 - Upper Middle (25-50%)'
        WHEN 3 THEN 'Tier 3 - Lower Middle (50-75%)'
        WHEN 4 THEN 'Tier 4 - Budget Tier (Bottom 25%)'
    END AS spending_tier,
    COUNT(*) AS total_customers,
    ROUND(MIN(monthly_charges), 2) AS min_monthly_charge,
    ROUND(MAX(monthly_charges), 2) AS max_monthly_charge,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charge,
    ROUND(SUM(CASE WHEN churn_status = 'Yes' THEN 1.0 ELSE 0 END) / COUNT(*) * 100, 2) AS churn_rate_pct
FROM customer_spending_quartiles
GROUP BY spending_quartile
ORDER BY spending_quartile;


-- --------------------------------------------------------------------
-- QUERY 5: Top 15 High-Risk Accounts Prioritized for Retention Outreach
-- Uses DENSE_RANK() by Expected MRR Loss (Probability * Monthly Charges)
-- --------------------------------------------------------------------
WITH prioritized_accounts AS (
    SELECT 
        f.customer_id,
        c.contract_type,
        f.tenure_months,
        f.monthly_charges,
        f.support_tickets,
        f.churn_probability,
        f.churn_risk_tier,
        f.expected_mrr_loss,
        DENSE_RANK() OVER (ORDER BY f.expected_mrr_loss DESC, f.churn_probability DESC) AS outreach_priority_rank
    FROM fact_subscriptions f
    JOIN dim_contracts c ON f.contract_key = c.contract_key
    WHERE f.churn_status = 'No' -- Focus on active accounts at risk of leaving
      AND f.churn_risk_tier = 'High Risk'
)
SELECT 
    outreach_priority_rank,
    customer_id,
    contract_type,
    tenure_months,
    support_tickets,
    monthly_charges,
    churn_probability,
    expected_mrr_loss
FROM prioritized_accounts
WHERE outreach_priority_rank <= 15
ORDER BY outreach_priority_rank;


-- --------------------------------------------------------------------
-- QUERY 6: Evaluating Predictive Model Accuracy directly in SQL
-- Confusion Matrix & Error Classification
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN churn_status = 'Yes' AND predicted_churn = 1 THEN 'True Positive (Correctly Predicted Churn)'
        WHEN churn_status = 'No'  AND predicted_churn = 0 THEN 'True Negative (Correctly Predicted Retained)'
        WHEN churn_status = 'No'  AND predicted_churn = 1 THEN 'False Positive (False Alarm)'
        WHEN churn_status = 'Yes' AND predicted_churn = 0 THEN 'False Negative (Missed Churn)'
    END AS classification_category,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fact_subscriptions), 2) AS pct_of_total_population,
    ROUND(SUM(monthly_charges), 2) AS financial_volume_impact
FROM fact_subscriptions
GROUP BY 
    CASE 
        WHEN churn_status = 'Yes' AND predicted_churn = 1 THEN 'True Positive (Correctly Predicted Churn)'
        WHEN churn_status = 'No'  AND predicted_churn = 0 THEN 'True Negative (Correctly Predicted Retained)'
        WHEN churn_status = 'No'  AND predicted_churn = 1 THEN 'False Positive (False Alarm)'
        WHEN churn_status = 'Yes' AND predicted_churn = 0 THEN 'False Negative (Missed Churn)'
    END
ORDER BY customer_count DESC;
