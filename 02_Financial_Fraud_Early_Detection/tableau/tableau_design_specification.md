# 📊 Tableau Workbook Design Specification

This document provides a comprehensive step-by-step guide for your team's Tableau Lead to build the **Financial Fraud Early Detection Interactive Tableau Dashboard**.

---

## 🎨 Theme & Palette
* **Theme:** Tableau Dark or Clean Modern Light
* **Fraud Alert Color:** Red (`#E15759`)
* **Legitimate Transaction Color:** Steel Blue (`#4E79A7`)
* **Warning / Medium Risk:** Yellow / Amber (`#F28E2B`)

---

## 📄 Sheet 1: Geospatial Cross-Border Fraud Burst Map

### Objective
Visualize the geographic relationship between the customer's home origin and the merchant terminal location to identify cross-border attacks and "Impossible Travel" clusters.

### Steps to Build
1. **Connect Data:** Open Tableau Desktop ➔ Connect to **Text File** ➔ Select `transactions_with_fraud_scores.csv`.
2. **Build the Map:**
   * Double-click `Merchant Country` (or assign Geographic Role: Country/Region).
   * Drag `Merchant Country` to **Detail** on the Marks card.
   * Drag `Is Fraud` to **Color** (Set mark color to Red for 1, Grey for 0).
   * Drag `Transaction Amount` to **Size** (proportional bubble sizes).
3. **Add Tooltips:**
   * Include: `Merchant Name`, `Merchant Category`, `Distance Km`, `Fraud Scenario`.
4. **Insight:** Highlights high-dollar fraud clusters originating overseas (e.g., China, Nigeria, UK Luxury outlets) on cards issued in North America.

---

## 📄 Sheet 2: Dual-Axis Transaction Volume & Fraud Velocity Timeline

### Objective
Track transaction volume alongside fraud rate spikes over time to detect synchronized credential-stuffing or card-testing attacks.

### Steps to Build
1. Drag `Trans Timestamp` to **Columns** ➔ Set to continuous **Day** or **Hour** (`DAY(Trans Timestamp)`).
2. Drag `Transaction Id` to **Rows** ➔ Right-click and set measure to **Count (Distinct)** (`CNTD(Transaction Id)`).
3. Drag `Fraud Rate %` (see calculated fields) to **Rows** right next to `CNTD(Transaction Id)`.
4. Right-click the second pill on Rows ➔ select **Dual Axis**.
5. Right-click the secondary axis on the chart ➔ select **Synchronize Axis**.
6. On the Marks Card:
   * Set `CNTD(Transaction Id)` mark type to **Bar** (Light Blue, 40% opacity).
   * Set `Fraud Rate %` mark type to **Line** (Bold Red).
7. **Insight:** Immediately exposes coordinated fraud bursts occurring on specific dates.

---

## 📄 Sheet 3: Behavioral Outlier Matrix (Risk Quadrants)

### Objective
Plot transaction ticket size against customer baseline spending deviation to isolate behavioral outliers.

### Steps to Build
1. Drag `Amount To Avg Ratio` to **Columns**.
2. Drag `Transaction Amount` to **Rows**.
3. Drag `Transaction Id` to **Detail** on the Marks card.
4. Drag `Fraud Risk Tier` to **Color** (High Risk: Red, Medium: Orange, Low: Green).
5. **Add Reference Lines (Analytics Pane):**
   * Drag **Reference Line** onto X-Axis: Constant value = `4.0` (Label: "4x Average Spike Threshold").
   * Drag **Reference Line** onto Y-Axis: Constant value = `$1,000` (Label: "High Ticket Threshold").
6. **Insight:** Quadrant IV (Top Right) isolates high-dollar, high-deviation transactions that represent 80%+ of chargeback volume.

---

## 🖥️ Executive Dashboard Assembly

1. Create a New Dashboard (Size: **Automatic** or **1366 x 768**).
2. Place a Title Banner at the top: `Financial Fraud & Anomaly Detection Center`.
3. Layout:
   * **Top Half:** Sheet 1 (Cross-Border Geospatial Map) + Sheet 2 (Dual-Axis Timeline).
   * **Bottom Half:** Sheet 3 (Behavioral Outlier Matrix) + Filter Panel.
4. **Configure Dashboard Actions:**
   * Go to **Dashboard** menu ➔ **Actions...** ➔ **Add Action** ➔ **Filter**.
   * Set Sheet 1 and Sheet 2 as **Source Sheets** with **Run action on: Select**.
   * Clicking a country on the map dynamically filters the timeline and risk scatter plot!
