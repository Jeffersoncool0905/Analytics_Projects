# 🌟 Power BI Data Model Architecture (Star Schema)

This document defines the Star Schema relational data model designed for the **Financial Fraud Early Detection Operations Dashboard** in Power BI Desktop.

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    dim_customers ||--o{ fact_transactions : "1 to Many (customer_id)"
    dim_cards ||--o{ fact_transactions : "1 to Many (card_key)"
    dim_merchants ||--o{ fact_transactions : "1 to Many (merchant_key)"
    dim_devices ||--o{ fact_transactions : "1 to Many (device_key)"

    dim_customers {
        string customer_id PK
        string customer_home_country
        decimal customer_avg_ticket
    }

    dim_cards {
        int card_key PK
        string card_number_masked
        string card_type
        string card_entry_mode
    }

    dim_merchants {
        int merchant_key PK
        string merchant_name
        string merchant_category
        string merchant_country
    }

    dim_devices {
        int device_key PK
        string device_type
    }

    fact_transactions {
        string transaction_id PK
        datetime trans_timestamp
        string customer_id FK
        int card_key FK
        int merchant_key FK
        int device_key FK
        decimal transaction_amount
        decimal amount_to_avg_ratio
        decimal distance_km
        int trans_count_last_1h
        int is_foreign_transaction
        int is_fraud
        string fraud_scenario
        decimal fraud_probability
        int predicted_fraud
        string fraud_risk_tier
        decimal expected_fraud_loss
    }
```

---

## 2. Cardinality & Cross-Filtering Best Practices
* **Relationship Type:** Strictly `1:*` (One-to-Many).
* **Cross-filter direction:** **Single** (Dimension filters Fact table).
* **Foreign Keys:** Hidden from Report View in `fact_transactions` to avoid accidental end-user aggregations.
* **Calculation Table:** Measures grouped into dedicated folders inside `_AllMeasures`.
