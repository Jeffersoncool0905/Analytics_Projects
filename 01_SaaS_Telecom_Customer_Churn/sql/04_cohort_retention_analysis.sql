-- ====================================================================
-- PROJECT: SaaS / Telecom Customer Churn & Retention Analytics
-- SCRIPT: 04_cohort_retention_analysis.sql
-- DESCRIPTION: Time-Based Cohort Retention Analysis using Advanced SQL CTEs
-- AUTHOR: Jefferson
-- ====================================================================


-- STEP 1: Define Cohort Groups and Active Lifespan Milestones

WITH customer_cohorts AS (
    SELECT 
        c.customer_id,
        c.signup_date,
        -- Extract signup Year-Quarter as cohort identifier
        CONCAT(
            CAST(EXTRACT(YEAR FROM c.signup_date) AS VARCHAR),
            '-Q',
            CAST(EXTRACT(QUARTER FROM c.signup_date) AS VARCHAR)
        ) AS cohort_quarter,
        f.tenure_months,
        f.churn_status,
        f.monthly_charges
    FROM dim_customers c
    JOIN fact_subscriptions f ON c.customer_id = f.customer_id
),


-- STEP 2: Calculate Active Status at Lifespan Milestones (Months 3, 6, 12, 24)

cohort_milestones AS (
    SELECT 
        cohort_quarter,
        customer_id,
        -- All signed-up customers are active at Month 0
        1 AS active_m0,
        -- Active at Month 3: Either still active OR churned after Month 3
        CASE WHEN churn_status = 'No' OR tenure_months >= 3 THEN 1 ELSE 0 END AS active_m3,
        CASE WHEN churn_status = 'No' OR tenure_months >= 6 THEN 1 ELSE 0 END AS active_m6,
        CASE WHEN churn_status = 'No' OR tenure_months >= 12 THEN 1 ELSE 0 END AS active_m12,
        CASE WHEN churn_status = 'No' OR tenure_months >= 24 THEN 1 ELSE 0 END AS active_m24,
        monthly_charges
    FROM customer_cohorts
),


-- STEP 3: Aggregate Cohort Volume and Milestone Retention

cohort_summary AS (
    SELECT 
        cohort_quarter,
        COUNT(customer_id) AS cohort_size,
        SUM(active_m0) AS retained_m0,
        SUM(active_m3) AS retained_m3,
        SUM(active_m6) AS retained_m6,
        SUM(active_m12) AS retained_m12,
        SUM(active_m24) AS retained_m24,
        ROUND(SUM(monthly_charges), 2) AS cohort_initial_mrr
    FROM cohort_milestones
    GROUP BY cohort_quarter
)


-- FINAL OUTPUT: Retention Percentage Matrix by Cohort

SELECT 
    cohort_quarter,
    cohort_size,
    cohort_initial_mrr,
    '100.0%' AS m0_retention_rate,
    CONCAT(CAST(ROUND(retained_m3 * 100.0 / cohort_size, 1) AS VARCHAR), '%') AS m3_retention_rate,
    CONCAT(CAST(ROUND(retained_m6 * 100.0 / cohort_size, 1) AS VARCHAR), '%') AS m6_retention_rate,
    CONCAT(CAST(ROUND(retained_m12 * 100.0 / cohort_size, 1) AS VARCHAR), '%') AS m12_retention_rate,
    CONCAT(CAST(ROUND(retained_m24 * 100.0 / cohort_size, 1) AS VARCHAR), '%') AS m24_retention_rate
FROM cohort_summary
ORDER BY cohort_quarter;
