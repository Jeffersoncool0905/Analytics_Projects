# 📊 Power BI Dashboard Build Specification

Follow these exact steps to build the interactive 3-page **SaaS / Telecom Customer Churn & Retention Dashboard** in Power BI Desktop.

---

## 🎨 Theme & Palette
* **Primary / Header:** Deep Navy Blue (`#1B365D`)
* **Accent / Interactive:** Royal Blue (`#2A5C9A`)
* **Alert / Churn:** Coral Red (`#C0392B`)
* **Success / Retained:** Emerald Green (`#27AE60`)
* **Neutral Background:** Soft Slate Grey (`#F8F9FA`)
* **Card Fill:** Pure White (`#FFFFFF`)

---

## 📄 Page 1: Executive Overview

### Layout Structure
1. **Top Header Banner:**
   * Text: *"SaaS / Telecom Executive Churn & Revenue Intelligence"*
   * Date Filter Slicer: `signup_date` (Between slider)
   * Global Filter Slicers: `contract_type`, `internet_service`, `tenure_bracket`
2. **KPI Cards Row (Top):**
   * Card 1: `[Total Customers]` (e.g. `7,043`)
   * Card 2: `[Active Customers]` (e.g. `5,219`)
   * Card 3: `[Churn Rate %]` (e.g. `25.9%` with conditional formatting: Red if > 25%)
   * Card 4: `[Total MRR]` (e.g. `$495.8K`)
   * Card 5: `[Churned MRR]` (e.g. `$136.3K`)
   * Card 6: `[ARPU]` (e.g. `$70.40`)
3. **Visual 1 (Donut Chart - Left):**
   * Legend: `dim_contracts[contract_type]`
   * Values: `[Churned Customers]`
   * Tooltip: `[Churn Rate %]`, `[Churned MRR]`
4. **Visual 2 (Clustered Bar Chart - Middle):**
   * Y-Axis: `dim_services[internet_service]`
   * X-Axis: `[Total Customers]`, `[Churned Customers]`
   * Data Labels: On
5. **Visual 3 (Line & Clustered Column Chart - Right):**
   * X-Axis: `fact_subscriptions[tenure_bracket]` (Sorted chronologically: 0-12, 13-24, 25-48, 49+)
   * Column Values: `[Total Customers]`
   * Line Value: `[Churn Rate %]` (shows sharp decline as tenure increases)

---

## 📄 Page 2: Churn Drivers & Behavioral Analytics

1. **Top Header Banner:**
   * Text: *"Root-Cause Analysis & Service Adoption Impact"*
2. **Visual 1 (Decomposition Tree - Left Half):**
   * Analyze: `[Churn Rate %]`
   * Explain by: `contract_type`, `internet_service`, `tech_support`, `online_security`, `payment_method`
   * *Demonstrates how non-adoption of tech support on Fiber Optic drives churn to over 40%.*
3. **Visual 2 (Scatter Plot - Top Right):**
   * X-Axis: `fact_subscriptions[tenure_months]`
   * Y-Axis: `fact_subscriptions[monthly_charges]`
   * Legend: `fact_subscriptions[churn_status]` (Red for Yes, Green for No)
   * Size: `fact_subscriptions[support_tickets]`
4. **Visual 3 (Stacked Bar Chart - Bottom Right):**
   * Y-Axis: `dim_contracts[payment_method]`
   * X-Axis: `[Churned MRR]`
   * Detail: `dim_contracts[paperless_billing]`

---

## 📄 Page 3: Predictive Risk & Retention Action Hub

1. **Top Header Banner:**
   * Text: *"Predictive Machine Learning Churn Risk & Outreach Action"*
2. **KPI Gauges & Risk Summary:**
   * Gauge Visual: `[Average Churn Probability]` (Target: 20%)
   * Card: `[High Risk Customers]` (Active accounts scored > 65% probability)
   * Card: `[Expected MRR Loss]` (Risk-weighted dollars at stake)
3. **What-If Scenario Slicer (Middle Left):**
   * Parameter: `Churn Reduction Parameter` (1% to 10%)
   * Output Card: `[Simulated Retained Accounts]`
   * Output Card: `[Simulated Annual Revenue Saved]`
4. **Actionable Table: High-Risk Account Priority List (Right/Bottom):**
   * Columns:
     * `customer_id`
     * `contract_type`
     * `tenure_months`
     * `monthly_charges`
     * `support_tickets`
     * `churn_probability` (Data bar visualization in table)
     * `churn_risk_tier` (Color tag: Red for High Risk)
     * `expected_mrr_loss`
   * Sort: `expected_mrr_loss` Descending
   * *This table provides the Customer Success team with their exact daily call list.*
