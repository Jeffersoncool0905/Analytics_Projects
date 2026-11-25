# 📊 Power BI Dashboard Build Specification

Follow these layout instructions to build the 3-page interactive **Financial Fraud Early Detection Operations Dashboard** in Power BI Desktop.

---

## 🎨 Theme & Palette
* **Primary / Header:** Midnight Charcoal (`#1B2631`)
* **Alert / Fraud:** Deep Crimson (`#922B21` / `#C0392B`)
* **Legitimate / Safe:** Mint Emerald (`#27AE60`)
* **Warning / Medium Risk:** Amber Gold (`#F39C12`)
* **Canvas Background:** Pure / Off-White (`#F8F9F9`)

---

## 📄 Page 1: Fraud Operations Command Center

### Layout Structure
1. **Top Header Banner:**
   * Text: `Financial & E-Commerce Fraud Operations Center`
   * Slicers: `card_type`, `card_entry_mode`, `fraud_risk_tier`
2. **KPI Cards Row:**
   * Card 1: `[Total Transactions]` (`10,000`)
   * Card 2: `[Gross Transaction Volume]` (`$1.55M`)
   * Card 3: `[Fraud Transactions]` (`333`)
   * Card 4: `[Fraud Rate (bps)]` (`333.0 bps` or `3.33%`)
   * Card 5: `[Prevented Fraud Volume]` (`$476K+`)
   * Card 6: `[Average Ticket Size]` (`$155.41`)
3. **Visual 1 (Clustered Bar Chart - Left):**
   * Y-Axis: `dim_merchants[merchant_category]`
   * X-Axis: `[Fraud Dollar Volume]`, `[Gross Transaction Volume]`
   * *Demonstrates Luxury Goods and E-Commerce taking the brunt of fraud volume.*
4. **Visual 2 (Donut Chart - Middle):**
   * Legend: `dim_cards[card_entry_mode]`
   * Values: `[Fraud Transactions]`
   * *Proves Online / CNP (Card-Not-Present) and Magstripe represent >85% of fraud incidents.*
5. **Visual 3 (Line Chart - Right):**
   * X-Axis: `fact_transactions[trans_timestamp]` (Day/Week hierarchy)
   * Y-Axis: `[Fraud Rate %]`

---

## 📄 Page 2: Attack Vector Diagnostics & Impossible Travel

1. **Top Header Banner:**
   * Text: `Attack Vector Breakdown & Geospatial Anomalies`
2. **Visual 1 (Treemap - Left):**
   * Group: `fact_transactions[fraud_scenario]` (Luxury Spike, Impossible Travel, Account Takeover, Card Testing)
   * Values: `[Fraud Dollar Volume]`
3. **Visual 2 (Scatter Plot - Top Right):**
   * X-Axis: `fact_transactions[distance_km]`
   * Y-Axis: `fact_transactions[transaction_amount]`
   * Legend: `fact_transactions[fraud_risk_tier]`
   * Size: `fact_transactions[amount_to_avg_ratio]`
4. **Visual 3 (Stacked Bar Chart - Bottom Right):**
   * Y-Axis: `dim_devices[device_type]`
   * X-Axis: `[Fraud Transactions]`
   * Legend: `fact_transactions[is_foreign_transaction]`

---

## 📄 Page 3: Real-Time Alert Queue & Analyst Triage

1. **Top Header Banner:**
   * Text: `High-Risk Transaction Triage & Outbound Review Queue`
2. **Metric Summary Cards:**
   * Card 1: `[High Risk Transactions]`
   * Card 2: `[Expected Fraud Loss]`
   * Card 3: `[False Positive Count]`
3. **Actionable Table Visual (Full Width):**
   * Columns:
     * `transaction_id`
     * `trans_timestamp`
     * `customer_id`
     * `merchant_name`
     * `merchant_category`
     * `card_entry_mode`
     * `transaction_amount`
     * `fraud_probability` (formatted as %)
     * `fraud_risk_tier` (High Risk tagged)
     * `expected_fraud_loss`
   * Visual Filter: `fraud_risk_tier` = `High Risk`
   * Sort: `expected_fraud_loss` Descending
