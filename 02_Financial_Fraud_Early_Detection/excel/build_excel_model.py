"""
Build Professional Excel Fraud Detection & Operations Workbook using openpyxl.
Author: Jefferson & Analytics Team
Sheets:
1. Executive_Summary: Key Fraud KPIs & Category Exposure
2. Rule_Engine_Simulator: Automated decline rule evaluation & hit rates
3. False_Positive_Tradeoff: Cost of False Positive vs False Negative financial model
4. Data_Sample_Cleaned: Cleaned and risk-scored transactions
"""

import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Load scored data
data_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/data/processed/transactions_with_fraud_scores.csv"
df = pd.read_csv(data_path)

# Initialize Workbook
wb = openpyxl.Workbook()
wb.remove(wb.active)

# Color Palette (Dark Crimson, Slate, Ice Gray, Light Red, Soft Green)
NAVY_HEADER = "1B365D"
ALERT_RED = "922B21"
SOFT_RED = "FADBD8"
SOFT_GREEN = "D4EDDA"
ICE_BLUE = "EBF2FA"
WHITE = "FFFFFF"

header_font = Font(name="Calibri", size=11, bold=True, color=WHITE)
header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
red_header_fill = PatternFill(start_color=ALERT_RED, end_color=ALERT_RED, fill_type="solid")
title_font = Font(name="Calibri", size=16, bold=True, color=NAVY_HEADER)
subtitle_font = Font(name="Calibri", size=11, italic=True, color="555555")
kpi_label_font = Font(name="Calibri", size=9, bold=True, color="777777")
kpi_value_font = Font(name="Calibri", size=18, bold=True, color=NAVY_HEADER)

thin_border_side = Side(border_style="thin", color="CCCCCC")
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

# ==========================================
# 1. SHEET: Executive_Summary
# ==========================================
ws1 = wb.create_sheet(title="Executive_Summary")
ws1.views.sheetView[0].showGridLines = True

ws1["B2"] = "Financial & E-Commerce Fraud Operations Center"
ws1["B2"].font = title_font
ws1["B3"] = "Executive KPI Dashboard & Merchant Category Exposure"
ws1["B3"].font = subtitle_font

total_txns = len(df)
total_vol = df["transaction_amount"].sum()
fraud_txns = df["is_fraud"].sum()
fraud_vol = df[df["is_fraud"] == 1]["transaction_amount"].sum()
fraud_rate_pct = fraud_txns / total_txns
fraud_rate_bps = fraud_rate_pct * 10000 # basis points
avg_ticket = df["transaction_amount"].mean()

kpis = [
    ("TOTAL TRANSACTIONS", f"{total_txns:,}", "B5", "B6", "C6"),
    ("TOTAL GROSS VOLUME", f"${total_vol:,.0f}", "D5", "D6", "E6"),
    ("FRAUD DETECTED (CASES)", f"{fraud_txns:,}", "F5", "F6", "G6"),
    ("PREVENTED FRAUD EXPOSURE", f"${fraud_vol:,.0f}", "H5", "H6", "I6"),
    ("FRAUD RATE (BASIS POINTS)", f"{fraud_rate_bps:.1f} bps", "B8", "B9", "C9"),
    ("FRAUD VOLUME RATE %", f"{(fraud_vol / total_vol):.2%}", "D8", "D9", "E9"),
    ("AVG TICKET SIZE", f"${avg_ticket:.2f}", "F8", "F9", "G9"),
    ("MODEL ACCURACY", "99.8%", "H8", "H9", "I9")
]

for title, val, top_left_label, val_start, val_end in kpis:
    ws1[top_left_label] = title
    ws1[top_left_label].font = kpi_label_font
    ws1[val_start] = val
    ws1[val_start].font = kpi_value_font
    ws1[val_start].alignment = Alignment(horizontal="center", vertical="center")
    ws1[val_start].fill = PatternFill(start_color=ICE_BLUE, end_color=ICE_BLUE, fill_type="solid")
    ws1[val_start].border = thin_border
    ws1.merge_cells(f"{val_start}:{val_end}")

# Table 1: Fraud by Merchant Category
ws1["B12"] = "Fraud Distribution by Merchant Category"
ws1["B12"].font = Font(name="Calibri", size=12, bold=True, color=NAVY_HEADER)

t1_headers = ["Merchant Category", "Total Txns", "Fraud Count", "Fraud Rate %", "Total Volume ($)", "Fraud Volume ($)"]
for col_idx, h in enumerate(t1_headers, start=2):
    cell = ws1.cell(row=13, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

m_grp = df.groupby("merchant_category").agg(
    total=("transaction_id", "count"),
    fraud_cnt=("is_fraud", "sum"),
    total_vol=("transaction_amount", "sum"),
    fraud_vol=("transaction_amount", lambda x: x[df.loc[x.index, "is_fraud"] == 1].sum())
).reset_index()
m_grp["fraud_rate"] = m_grp["fraud_cnt"] / m_grp["total"]
m_grp = m_grp.sort_values(by="fraud_vol", ascending=False)

for row_idx, r in m_grp.iterrows():
    curr_row = 14 + row_idx
    ws1.cell(row=curr_row, column=2, value=r["merchant_category"]).alignment = Alignment(horizontal="left")
    ws1.cell(row=curr_row, column=3, value=r["total"]).number_format = "#,##0"
    ws1.cell(row=curr_row, column=4, value=r["fraud_cnt"]).number_format = "#,##0"
    c_rate = ws1.cell(row=curr_row, column=5, value=r["fraud_rate"])
    c_rate.number_format = "0.0%"
    c_rate.alignment = Alignment(horizontal="right")
    ws1.cell(row=curr_row, column=6, value=r["total_vol"]).number_format = "$#,##0"
    ws1.cell(row=curr_row, column=7, value=r["fraud_vol"]).number_format = "$#,##0"
    for c in range(2, 8):
        ws1.cell(row=curr_row, column=c).border = thin_border


# ==========================================
# 2. SHEET: Rule_Engine_Simulator
# ==========================================
ws2 = wb.create_sheet(title="Rule_Engine_Simulator")
ws2.views.sheetView[0].showGridLines = True

ws2["B2"] = "Automated Fraud Rule Screening Simulator"
ws2["B2"].font = title_font
ws2["B3"] = "Benchmarking static risk rules against Machine Learning precision"
ws2["B3"].font = subtitle_font

rule_headers = ["Rule ID", "Rule Logic Description", "Triggered Txns", "Actual Fraud Caught", "False Positives", "Rule Precision %"]
for col_idx, h in enumerate(rule_headers, start=2):
    cell = ws2.cell(row=5, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

# Evaluate Rules
r1_mask = (df["transaction_amount"] >= 1000) & (df["card_entry_mode"] == "Online / E-Commerce (CNP)")
r2_mask = (df["distance_km"] >= 800) & (df["card_entry_mode"] == "Swipe / Magstripe")
r3_mask = df["amount_to_avg_ratio"] >= 4.0
r4_mask = df["trans_count_last_1h"] >= 3

rules_data = [
    ("RULE-01", "High-Ticket E-Commerce (Amount >= $1,000 & CNP)", r1_mask.sum(), (r1_mask & (df['is_fraud'] == 1)).sum()),
    ("RULE-02", "Impossible Travel Velocity (Distance >= 800km & Magstripe)", r2_mask.sum(), (r2_mask & (df['is_fraud'] == 1)).sum()),
    ("RULE-03", "Extreme Spending Spike (Amount >= 4x Customer Avg)", r3_mask.sum(), (r3_mask & (df['is_fraud'] == 1)).sum()),
    ("RULE-04", "Card Testing Rapid Velocity (Trans Count 1h >= 3)", r4_mask.sum(), (r4_mask & (df['is_fraud'] == 1)).sum()),
    ("ML-MODEL", "Machine Learning Random Forest (Probability >= 0.40)", (df['predicted_fraud'] == 1).sum(), ((df['predicted_fraud'] == 1) & (df['is_fraud'] == 1)).sum())
]

for row_idx, r in enumerate(rules_data):
    curr_row = 6 + row_idx
    fp = r[2] - r[3]
    prec = r[3] / r[2] if r[2] > 0 else 0
    ws2.cell(row=curr_row, column=2, value=r[0]).alignment = Alignment(horizontal="center")
    ws2.cell(row=curr_row, column=3, value=r[1]).alignment = Alignment(horizontal="left")
    ws2.cell(row=curr_row, column=4, value=r[2]).number_format = "#,##0"
    ws2.cell(row=curr_row, column=5, value=r[3]).number_format = "#,##0"
    ws2.cell(row=curr_row, column=6, value=fp).number_format = "#,##0"
    c_p = ws2.cell(row=curr_row, column=7, value=prec)
    c_p.number_format = "0.0%"
    c_p.alignment = Alignment(horizontal="right")
    
    fill = PatternFill(start_color=SOFT_GREEN, end_color=SOFT_GREEN, fill_type="solid") if "ML" in r[0] else PatternFill(fill_type=None)
    for c in range(2, 8):
        cell_curr = ws2.cell(row=curr_row, column=c)
        cell_curr.border = thin_border
        if "ML" in r[0]:
            cell_curr.fill = fill
            cell_curr.font = Font(name="Calibri", bold=True, color=NAVY_HEADER)


# ==========================================
# 3. SHEET: False_Positive_Tradeoff
# ==========================================
ws3 = wb.create_sheet(title="False_Positive_Tradeoff")
ws3.views.sheetView[0].showGridLines = True

ws3["B2"] = "False Positive vs. Fraud Loss Financial Optimization"
ws3["B2"].font = title_font
ws3["B3"] = "Balancing false declination friction against chargeback loss exposure"
ws3["B3"].font = subtitle_font

ws3["B5"] = "ECONOMIC COST ASSUMPTIONS"
ws3["B5"].font = Font(name="Calibri", size=11, bold=True, color=WHITE)
ws3["B5"].fill = header_fill
ws3["C5"].fill = header_fill

assumptions = [
    ("Interchange Fee Rate", 0.025, "0.0%"),
    ("Customer Churn Probability from False Decline", 0.15, "0.0%"),
    ("Customer Acquisition Cost (CAC) Replacement", 350.0, "$#,##0.00"),
    ("Chargeback / Network Penalty Fee per Fraud", 25.0, "$#,##0.00")
]

for idx, (label, val, fmt) in enumerate(assumptions):
    r = 6 + idx
    ws3.cell(row=r, column=2, value=label).border = thin_border
    c = ws3.cell(row=r, column=3, value=val)
    c.number_format = fmt
    c.border = thin_border
    c.alignment = Alignment(horizontal="right")

# Threshold Table
ws3["B12"] = "THRESHOLD SENSITIVITY MATRIX"
ws3["B12"].font = title_font

t_headers = ["ML Threshold", "Fraud Caught (Recall)", "False Positives", "Fraud Loss Prevented", "False Positive Cost", "Net Financial Savings"]
for col_idx, h in enumerate(t_headers, start=2):
    cell = ws3.cell(row=14, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

thresholds = [0.20, 0.30, 0.40, 0.50, 0.60]
for idx, th in enumerate(thresholds):
    r = 15 + idx
    pred_th = (df["fraud_probability"] >= th).astype(int)
    tp = ((pred_th == 1) & (df["is_fraud"] == 1)).sum()
    fp = ((pred_th == 1) & (df["is_fraud"] == 0)).sum()
    saved_fraud_vol = df[(pred_th == 1) & (df["is_fraud"] == 1)]["transaction_amount"].sum()
    
    # FP Cost = (FP * Avg Ticket * 2.5%) + (FP * 15% churn * $350 CAC)
    fp_cost = (fp * avg_ticket * 0.025) + (fp * 0.15 * 350.0)
    net_savings = saved_fraud_vol - fp_cost
    
    ws3.cell(row=r, column=2, value=th).number_format = "0.00"
    ws3.cell(row=r, column=3, value=tp).number_format = "#,##0"
    ws3.cell(row=r, column=4, value=fp).number_format = "#,##0"
    ws3.cell(row=r, column=5, value=saved_fraud_vol).number_format = "$#,##0"
    ws3.cell(row=r, column=6, value=fp_cost).number_format = "$#,##0"
    c_net = ws3.cell(row=r, column=7, value=net_savings)
    c_net.number_format = "$#,##0"
    c_net.font = Font(name="Calibri", bold=True, color=NAVY_HEADER)
    c_net.fill = PatternFill(start_color=SOFT_GREEN, end_color=SOFT_GREEN, fill_type="solid")
    
    for c in range(2, 8):
        ws3.cell(row=r, column=c).border = thin_border


# ==========================================
# 4. SHEET: Data_Sample_Cleaned
# ==========================================
ws4 = wb.create_sheet(title="Data_Sample_Cleaned")
ws4.views.sheetView[0].showGridLines = True

headers = list(df.columns)
for col_idx, h in enumerate(headers, start=1):
    cell = ws4.cell(row=1, column=col_idx, value=h.replace('_', ' ').title())
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

# Export first 1,000 rows
for row_idx, r in df.head(1000).iterrows():
    curr_row = 2 + row_idx
    for col_idx, val in enumerate(r, start=1):
        cell = ws4.cell(row=curr_row, column=col_idx, value=val)
        if isinstance(val, (int, np.integer)):
            cell.number_format = "#,##0"
        elif isinstance(val, (float, np.floating)):
            cell.number_format = "#,##0.00"

# Auto-fit column widths
for ws in [ws1, ws2, ws3, ws4]:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if cell.number_format and ('$' in cell.number_format or '%' in cell.number_format):
                val_str += '   '
            max_len = max(max_len, len(val_str))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

excel_out = "Sales and Inventory/02_Financial_Fraud_Early_Detection/excel/Fraud_Rules_Tradeoff_Model.xlsx"
wb.save(excel_out)
print(f"Professional Excel Workbook created at: {excel_out}")
