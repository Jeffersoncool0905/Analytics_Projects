

This document outlines the relational data modeling approach applied in Power BI. A **Star Schema** architecture is implemented to ensure fast query performance, simplified DAX calculations, and intuitive report authoring.

---

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    dim_customers ||--o{ fact_subscriptions : "1 to Many (customer_id)"
    dim_contracts ||--o{ fact_subscriptions : "1 to Many (contract_key)"
    dim_services ||--o{ fact_subscriptions : "1 to Many (service_key)"

    dim_customers {
        string customer_id PK
        date signup_date
        string gender
        int is_senior_citizen
        boolean has_partner
        boolean has_dependents
    }

    dim_contracts {
        int contract_key PK
        string contract_type
        string paperless_billing
        string payment_method
    }

    dim_services {
        int service_key PK
        string phone_service
        string multiple_lines
        string internet_service
        string online_security
        string online_backup
        string device_protection
        string tech_support
        string streaming_tv
        string streaming_movies
    }

    fact_subscriptions {
        int subscription_id PK
        string customer_id FK
        int contract_key FK
        int service_key FK
        int tenure_months
        string tenure_bracket
        decimal monthly_charges
        decimal total_charges
        int support_tickets
        decimal monthly_usage_gb
        string churn_status
        string churn_reason
        decimal churn_probability
        int predicted_churn
        string churn_risk_tier
        decimal expected_mrr_loss
    }
```

---

 2. Model Guidelines & Best Practices

1. **Cardinality & Cross-Filtering:**
   * All relationships are strictly `1:*` (One-to-Many).
   * Cross-filter direction is set to **Single** (from dimension to fact table) to avoid circular dependencies and performance degradation.
2. **Key Hiding:**
   * Foreign keys in `fact_subscriptions` (`contract_key`, `service_key`, `customer_id`) are **hidden** in Report View to prevent users from accidentally creating invalid aggregations.
3. **Dedicated Measure Table:**
   * An empty calculation table `_AllMeasures` is created to store all DAX measures in organized folders:
     * `01 Volume & Counts`
     * `02 Rates & Ratios`
     * `03 Revenue & CLV`
     * `04 Predictive Risk`
     * `05 What-If Simulator`
