-- ====================================================================
-- PROJECT: Financial & E-Commerce Fraud Early Detection Analysis
-- SCRIPT: 01_schema_setup.sql
-- DESCRIPTION: Star Schema DDL for Transactions, Merchants, Cards & Devices
-- AUTHOR: Jefferson & Analytics Team
-- COMPATIBILITY: PostgreSQL, MySQL 8+, SQLite, SQL Server
-- ====================================================================

-- 1. Create Staging Table for Ingestion
DROP TABLE IF EXISTS stg_transactions;
CREATE TABLE stg_transactions (
    transaction_id              VARCHAR(25) PRIMARY KEY,
    trans_timestamp             DATETIME NOT NULL,
    customer_id                 VARCHAR(25) NOT NULL,
    card_number_masked          VARCHAR(25) NOT NULL,
    card_type                   VARCHAR(20) NOT NULL,
    customer_home_country       VARCHAR(25) NOT NULL,
    merchant_name               VARCHAR(60) NOT NULL,
    merchant_category           VARCHAR(50) NOT NULL,
    merchant_country            VARCHAR(25) NOT NULL,
    card_entry_mode             VARCHAR(40) NOT NULL,
    device_type                 VARCHAR(30) NOT NULL,
    transaction_amount          DECIMAL(12, 2) NOT NULL,
    customer_avg_ticket         DECIMAL(12, 2) NOT NULL,
    amount_to_avg_ratio         DECIMAL(8, 2) NOT NULL,
    distance_km                 DECIMAL(10, 2) NOT NULL,
    is_foreign_transaction      INT NOT NULL,
    is_fraud                    INT NOT NULL,
    fraud_scenario              VARCHAR(50) NOT NULL,
    trans_count_last_1h         INT NOT NULL,
    fraud_probability           DECIMAL(6, 4) NOT NULL,
    predicted_fraud             INT NOT NULL,
    fraud_risk_tier             VARCHAR(20) NOT NULL,
    expected_fraud_loss         DECIMAL(12, 2) NOT NULL
);

-- ====================================================================
-- 2. Star Schema Dimension & Fact Tables
-- ====================================================================

-- Dimension: Customer Profiles
DROP TABLE IF EXISTS dim_customers;
CREATE TABLE dim_customers (
    customer_id                 VARCHAR(25) PRIMARY KEY,
    customer_home_country       VARCHAR(25) NOT NULL,
    customer_avg_ticket         DECIMAL(12, 2) NOT NULL
);

-- Dimension: Cards & Payment Medium
DROP TABLE IF EXISTS dim_cards;
CREATE TABLE dim_cards (
    card_key                    INT PRIMARY KEY,
    card_number_masked          VARCHAR(25) NOT NULL,
    card_type                   VARCHAR(20) NOT NULL,
    card_entry_mode             VARCHAR(40) NOT NULL
);

-- Dimension: Merchants
DROP TABLE IF EXISTS dim_merchants;
CREATE TABLE dim_merchants (
    merchant_key                INT PRIMARY KEY,
    merchant_name               VARCHAR(60) NOT NULL,
    merchant_category           VARCHAR(50) NOT NULL,
    merchant_country            VARCHAR(25) NOT NULL
);

-- Dimension: Devices
DROP TABLE IF EXISTS dim_devices;
CREATE TABLE dim_devices (
    device_key                  INT PRIMARY KEY,
    device_type                 VARCHAR(30) NOT NULL
);

-- Fact: Financial Transactions
DROP TABLE IF EXISTS fact_transactions;
CREATE TABLE fact_transactions (
    transaction_id              VARCHAR(25) PRIMARY KEY,
    trans_timestamp             DATETIME NOT NULL,
    customer_id                 VARCHAR(25) NOT NULL,
    card_key                    INT NOT NULL,
    merchant_key                INT NOT NULL,
    device_key                  INT NOT NULL,
    transaction_amount          DECIMAL(12, 2) NOT NULL,
    amount_to_avg_ratio         DECIMAL(8, 2) NOT NULL,
    distance_km                 DECIMAL(10, 2) NOT NULL,
    trans_count_last_1h         INT NOT NULL,
    is_foreign_transaction      INT NOT NULL,
    is_fraud                    INT NOT NULL,
    fraud_scenario              VARCHAR(50) NOT NULL,
    fraud_probability           DECIMAL(6, 4) NOT NULL,
    predicted_fraud             INT NOT NULL,
    fraud_risk_tier             VARCHAR(20) NOT NULL,
    expected_fraud_loss         DECIMAL(12, 2) NOT NULL
);

-- Indexing for sub-second risk screening
CREATE INDEX idx_trans_customer ON fact_transactions(customer_id);
CREATE INDEX idx_trans_timestamp ON fact_transactions(trans_timestamp);
CREATE INDEX idx_trans_fraud ON fact_transactions(is_fraud);
CREATE INDEX idx_trans_risk_tier ON fact_transactions(fraud_risk_tier);
