-- ====================================================================
-- PROJECT: SaaS / Telecom Customer Churn & Retention Analytics
-- SCRIPT: 01_schema_setup.sql
-- DESCRIPTION: DDL Script for Normalized Star Schema & Fact/Dimension Tables
-- AUTHOR: Jefferson
-- COMPATIBILITY: PostgreSQL, MySQL 8+, SQLite, SQL Server
-- ====================================================================

-- 1. Create Staging Table for Raw / Scored Ingestion
DROP TABLE IF EXISTS stg_customer_churn;
CREATE TABLE stg_customer_churn (
    customer_id             VARCHAR(20) PRIMARY KEY,
    signup_date             DATE,
    gender                  VARCHAR(10),
    senior_citizen          INT,
    partner                 VARCHAR(5),
    dependents              VARCHAR(5),
    tenure_months           INT,
    phone_service           VARCHAR(5),
    multiple_lines          VARCHAR(25),
    internet_service        VARCHAR(25),
    online_security         VARCHAR(25),
    online_backup           VARCHAR(25),
    device_protection       VARCHAR(25),
    tech_support            VARCHAR(25),
    streaming_tv            VARCHAR(25),
    streaming_movies        VARCHAR(25),
    contract_type           VARCHAR(25),
    paperless_billing       VARCHAR(5),
    payment_method          VARCHAR(40),
    monthly_charges         DECIMAL(10, 2),
    total_charges           DECIMAL(10, 2),
    support_tickets         INT,
    monthly_usage_gb        DECIMAL(10, 2),
    churn_status            VARCHAR(5),
    churn_reason            VARCHAR(100),
    tenure_bracket          VARCHAR(20),
    churn_probability       DECIMAL(6, 4),
    predicted_churn         INT,
    churn_risk_tier         VARCHAR(20)
);

-- ====================================================================
-- 2. Star Schema Dimension & Fact Tables
-- ====================================================================

-- Dimension: Customer Demographics
DROP TABLE IF EXISTS dim_customers;
CREATE TABLE dim_customers (
    customer_id             VARCHAR(20) PRIMARY KEY,
    signup_date             DATE NOT NULL,
    gender                  VARCHAR(10),
    is_senior_citizen       BOOLEAN,
    has_partner             BOOLEAN,
    has_dependents          BOOLEAN
);

-- Dimension: Subscription Contract & Billing Profile
DROP TABLE IF EXISTS dim_contracts;
CREATE TABLE dim_contracts (
    contract_key            INT PRIMARY KEY,
    contract_type           VARCHAR(25) NOT NULL,
    paperless_billing       VARCHAR(5) NOT NULL,
    payment_method          VARCHAR(40) NOT NULL
);

-- Dimension: Service Subscriptions
DROP TABLE IF EXISTS dim_services;
CREATE TABLE dim_services (
    service_key             INT PRIMARY KEY,
    phone_service           VARCHAR(5),
    multiple_lines          VARCHAR(25),
    internet_service        VARCHAR(25),
    online_security         VARCHAR(25),
    online_backup           VARCHAR(25),
    device_protection       VARCHAR(25),
    tech_support            VARCHAR(25),
    streaming_tv            VARCHAR(25),
    streaming_movies        VARCHAR(25)
);

-- Fact: Customer Subscriptions & Churn Metrics
DROP TABLE IF EXISTS fact_subscriptions;
CREATE TABLE fact_subscriptions (
    subscription_id         INT PRIMARY KEY,
    customer_id             VARCHAR(20) NOT NULL,
    contract_key            INT,
    service_key             INT,
    tenure_months           INT NOT NULL CHECK (tenure_months >= 0),
    tenure_bracket          VARCHAR(20),
    monthly_charges         DECIMAL(10, 2) NOT NULL,
    total_charges           DECIMAL(10, 2) NOT NULL,
    support_tickets         INT DEFAULT 0,
    monthly_usage_gb        DECIMAL(10, 2),
    churn_status            VARCHAR(5) NOT NULL,
    churn_reason            VARCHAR(100),
    churn_probability       DECIMAL(6, 4),
    predicted_churn         INT,
    churn_risk_tier         VARCHAR(20),
    expected_mrr_loss       DECIMAL(10, 2)
);

-- Indexing for high-performance reporting & BI queries
CREATE INDEX idx_fact_customer_id ON fact_subscriptions(customer_id);
CREATE INDEX idx_fact_churn_status ON fact_subscriptions(churn_status);
CREATE INDEX idx_fact_risk_tier ON fact_subscriptions(churn_risk_tier);
CREATE INDEX idx_fact_tenure_bracket ON fact_subscriptions(tenure_bracket);
