# 📐 Power BI DAX Measures Documentation

This document contains all production DAX measures developed for the **Financial Fraud Early Detection Operations Dashboard**.

---

## 1. Transaction Volume & Base Counts

### `Total Transactions`
```dax
Total Transactions = COUNTROWS('fact_transactions')
```
* **Format:** Whole Number (`#,##0`)

### `Fraud Transactions`
```dax
Fraud Transactions = 
CALCULATE(
    [Total Transactions],
    'fact_transactions'[is_fraud] = 1
)
```
* **Format:** Whole Number (`#,##0`)

### `Legitimate Transactions`
```dax
Legitimate Transactions = 
CALCULATE(
    [Total Transactions],
    'fact_transactions'[is_fraud] = 0
)
```

---

## 2. Rates & Key Performance Indicators (KPIs)

### `Fraud Rate %`
```dax
Fraud Rate % = 
DIVIDE([Fraud Transactions], [Total Transactions], 0)
```
* **Format:** Percentage (`0.00%`)

### `Fraud Rate (Basis Points)`
```dax
Fraud Rate (bps) = 
[Fraud Rate %] * 10000
```
* **Format:** Decimal Number (`0.0 bps`)

### `Fraud Volume Rate %`
```dax
Fraud Volume Rate % = 
DIVIDE([Fraud Dollar Volume], [Gross Transaction Volume], 0)
```
* **Format:** Percentage (`0.00%`)

---

## 3. Financial Exposure & Prevented Losses

### `Gross Transaction Volume`
```dax
Gross Transaction Volume = 
SUM('fact_transactions'[transaction_amount])
```
* **Format:** Currency (`$#,##0`)

### `Fraud Dollar Volume`
```dax
Fraud Dollar Volume = 
CALCULATE(
    [Gross Transaction Volume],
    'fact_transactions'[is_fraud] = 1
)
```
* **Format:** Currency (`$#,##0`)

### `Prevented Fraud Volume (ML Caught)`
```dax
Prevented Fraud Volume = 
CALCULATE(
    [Gross Transaction Volume],
    'fact_transactions'[predicted_fraud] = 1,
    'fact_transactions'[is_fraud] = 1
)
```
* **Format:** Currency (`$#,##0`)

### `Average Ticket Size`
```dax
Average Ticket Size = 
DIVIDE([Gross Transaction Volume], [Total Transactions], 0)
```
* **Format:** Currency (`$#,##0.00`)

---

## 4. Predictive Machine Learning Risk Measures

### `High Risk Transactions`
```dax
High Risk Transactions = 
CALCULATE(
    [Total Transactions],
    'fact_transactions'[fraud_risk_tier] = "High Risk"
) + 0
```
* **Format:** Whole Number (`#,##0`)

### `Expected Fraud Loss`
```dax
Expected Fraud Loss = 
SUMX(
    'fact_transactions',
    'fact_transactions'[transaction_amount] * 'fact_transactions'[fraud_probability]
)
```
* **Format:** Currency (`$#,##0`)

### `Average Fraud Probability`
```dax
Average Fraud Probability = 
AVERAGE('fact_transactions'[fraud_probability])
```
* **Format:** Percentage (`0.0%`)

### `False Positive Count`
```dax
False Positive Count = 
CALCULATE(
    [Total Transactions],
    'fact_transactions'[predicted_fraud] = 1,
    'fact_transactions'[is_fraud] = 0
) + 0
```
