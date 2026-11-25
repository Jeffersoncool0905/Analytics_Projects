# 📐 Tableau Calculated Fields & LOD Expressions

This reference guide contains the exact formulas needed for your team to build the calculated fields and Level of Detail (LOD) expressions in Tableau Desktop.

---

## 1. Core Metrics & Aggregations

### `Fraud Rate %`
```tableau
SUM([Is Fraud]) / COUNT([Transaction Id])
```
* **Format:** Percentage (`0.0%`)

### `Total Fraud Losses ($)`
```tableau
SUM(IF [Is Fraud] = 1 THEN [Transaction Amount] ELSE 0 END)
```
* **Format:** Currency (`$#,##0`)

### `Prevented Fraud Volume ($)`
```tableau
SUM(IF [Predicted Fraud] = 1 AND [Is Fraud] = 1 THEN [Transaction Amount] ELSE 0 END)
```
* **Format:** Currency (`$#,##0`)

### `Average Ticket Size`
```tableau
AVG([Transaction Amount])
```
* **Format:** Currency (`$#,##0.00`)

---

## 2. Advanced Level of Detail (LOD) Expressions

### `Customer Distinct Merchant Countries (Multi-Country Velocity)`
```tableau
{ FIXED [Customer Id] : COUNTD([Merchant Country]) }
```
* **Description:** Identifies customers whose cards are transacting across multiple distinct foreign jurisdictions.

### `Customer Baseline Average Ticket Size (Fixed Anchor)`
```tableau
{ FIXED [Customer Id] : AVG([Transaction Amount]) }
```
* **Description:** Locks the customer's average ticket size regardless of dashboard filtering.

### `Merchant Fraud Intensity Rate`
```tableau
{ FIXED [Merchant Name] : SUM([Is Fraud]) } / { FIXED [Merchant Name] : COUNT([Transaction Id]) }
```
* **Description:** Computes the inherent fraud rate per individual merchant to flag compromised payment gateways.

---

## 3. Conditional Risk & Classification Flags

### `Velocity Alert Flag`
```tableau
IF [Trans Count Last 1H] >= 3 THEN
    "High Velocity Spike (>= 3 / hr)"
ELSE
    "Standard Velocity"
END
```

### `Impossible Travel Distance Flag`
```tableau
IF [Distance Km] >= 800 AND [Card Entry Mode] = "Swipe / Magstripe" THEN
    "ALERT: Impossible Travel"
ELSEIF [Distance Km] >= 800 THEN
    "Long-Distance Online"
ELSE
    "Local Transaction"
END
```

### `Confusion Matrix Category`
```tableau
IF [Is Fraud] = 1 AND [Predicted Fraud] = 1 THEN
    "True Positive (Fraud Caught)"
ELSEIF [Is Fraud] = 0 AND [Predicted Fraud] = 0 THEN
    "True Negative (Legitimate Approved)"
ELSEIF [Is Fraud] = 0 AND [Predicted Fraud] = 1 THEN
    "False Positive (Customer Friction)"
ELSE
    "False Negative (Missed Chargeback)"
END
```
