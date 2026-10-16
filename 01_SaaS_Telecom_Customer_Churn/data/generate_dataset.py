"""
Generate realistic SaaS / Telecom Customer Churn Dataset.
Author: Jefferson
Dataset features: 7,043 customer accounts with subscription, usage, support, and billing details.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
n_records = 7043

# Generate Customer IDs
customer_ids = [f"CUST-{10001 + i}" for i in range(n_records)]

# Demographics
gender = np.random.choice(["Male", "Female"], size=n_records)
senior_citizen = np.random.choice([0, 1], size=n_records, p=[0.84, 0.16])
partner = np.random.choice(["Yes", "No"], size=n_records, p=[0.48, 0.52])
dependents = np.where(partner == "Yes", np.random.choice(["Yes", "No"], size=n_records, p=[0.55, 0.45]), "No")

# Tenure in months (1 to 72)
tenure_months = np.random.exponential(scale=24, size=n_records).astype(int)
tenure_months = np.clip(tenure_months, 1, 72)

# Contract type correlated with tenure
contract_probs = []
for t in tenure_months:
    if t < 12:
        contract_probs.append([0.85, 0.12, 0.03])
    elif t < 36:
        contract_probs.append([0.50, 0.35, 0.15])
    else:
        contract_probs.append([0.20, 0.35, 0.45])

contracts = [np.random.choice(["Month-to-month", "One year", "Two year"], p=p) for p in contract_probs]

# Services
phone_service = np.random.choice(["Yes", "No"], size=n_records, p=[0.90, 0.10])
multiple_lines = []
for ps in phone_service:
    if ps == "No":
        multiple_lines.append("No phone service")
    else:
        multiple_lines.append(np.random.choice(["Yes", "No"], p=[0.42, 0.58]))

internet_service = np.random.choice(["DSL", "Fiber optic", "No"], size=n_records, p=[0.34, 0.44, 0.22])

online_security = []
online_backup = []
device_protection = []
tech_support = []
streaming_tv = []
streaming_movies = []

for is_service in internet_service:
    if is_service == "No":
        online_security.append("No internet service")
        online_backup.append("No internet service")
        device_protection.append("No internet service")
        tech_support.append("No internet service")
        streaming_tv.append("No internet service")
        streaming_movies.append("No internet service")
    else:
        online_security.append(np.random.choice(["Yes", "No"], p=[0.35, 0.65]))
        online_backup.append(np.random.choice(["Yes", "No"], p=[0.44, 0.56]))
        device_protection.append(np.random.choice(["Yes", "No"], p=[0.43, 0.57]))
        tech_support.append(np.random.choice(["Yes", "No"], p=[0.36, 0.64]))
        streaming_tv.append(np.random.choice(["Yes", "No"], p=[0.49, 0.51]))
        streaming_movies.append(np.random.choice(["Yes", "No"], p=[0.50, 0.50]))

# Billing & Charges
paperless_billing = np.random.choice(["Yes", "No"], size=n_records, p=[0.59, 0.41])
payment_method = np.random.choice(
    ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
    size=n_records,
    p=[0.34, 0.22, 0.22, 0.22]
)

monthly_charges = []
for i in range(n_records):
    base = 20.0
    if phone_service[i] == "Yes":
        base += 5.0
    if multiple_lines[i] == "Yes":
        base += 8.0
    if internet_service[i] == "DSL":
        base += 25.0
    elif internet_service[i] == "Fiber optic":
        base += 45.0
    if online_security[i] == "Yes":
        base += 6.0
    if online_backup[i] == "Yes":
        base += 6.0
    if device_protection[i] == "Yes":
        base += 6.0
    if tech_support[i] == "Yes":
        base += 6.0
    if streaming_tv[i] == "Yes":
        base += 10.0
    if streaming_movies[i] == "Yes":
        base += 10.0
    # Add small variance
    base += np.random.uniform(-3.0, 3.0)
    monthly_charges.append(round(base, 2))

total_charges = [round(m * t + np.random.uniform(-5.0, 5.0), 2) for m, t in zip(monthly_charges, tenure_months)]

# Operational / SaaS metrics
support_tickets = np.random.poisson(lam=1.5, size=n_records)
monthly_usage_gb = np.random.normal(loc=180, scale=60, size=n_records).clip(10, 500).round(1)

# Churn logic (realistic correlation with contract, tenure, tech support, price)
churn_probs = []
for i in range(n_records):
    score = 0.02  # base
    if contracts[i] == "Month-to-month":
        score += 0.22
    elif contracts[i] == "Two year":
        score -= 0.08
        
    if internet_service[i] == "Fiber optic":
        score += 0.08
    if tech_support[i] == "No":
        score += 0.06
    if online_security[i] == "No":
        score += 0.04
    if payment_method[i] == "Electronic check":
        score += 0.06
    if tenure_months[i] < 6:
        score += 0.10
    elif tenure_months[i] > 36:
        score -= 0.10
    if support_tickets[i] >= 4:
        score += 0.14
    
    score = np.clip(score, 0.01, 0.85)
    churn_probs.append(score)

churn_status = ["Yes" if np.random.rand() < p else "No" for p in churn_probs]

# Churn Reason for those who churned
churn_reasons_pool = [
    "Competitor had better devices",
    "Competitor offered higher download speeds",
    "Competitor made better overall offer",
    "Attitude of support technician",
    "Price was too high compared to value",
    "Product was no longer needed",
    "Network reliability and frequent downtime",
    "Moved to another location"
]

churn_reasons = []
for ch in churn_status:
    if ch == "Yes":
        churn_reasons.append(np.random.choice(churn_reasons_pool))
    else:
        churn_reasons.append(None)

# Signup dates calculated backward from current reference date (2026-03-01)
reference_date = datetime(2026, 3, 1)
signup_dates = [(reference_date - timedelta(days=int(t * 30.42))).strftime("%Y-%m-%d") for t in tenure_months]

# Construct DataFrame
df = pd.DataFrame({
    "customer_id": customer_ids,
    "signup_date": signup_dates,
    "gender": gender,
    "senior_citizen": senior_citizen,
    "partner": partner,
    "dependents": dependents,
    "tenure_months": tenure_months,
    "phone_service": phone_service,
    "multiple_lines": multiple_lines,
    "internet_service": internet_service,
    "online_security": online_security,
    "online_backup": online_backup,
    "device_protection": device_protection,
    "tech_support": tech_support,
    "streaming_tv": streaming_tv,
    "streaming_movies": streaming_movies,
    "contract_type": contracts,
    "paperless_billing": paperless_billing,
    "payment_method": payment_method,
    "monthly_charges": monthly_charges,
    "total_charges": total_charges,
    "support_tickets": support_tickets,
    "monthly_usage_gb": monthly_usage_gb,
    "churn_status": churn_status,
    "churn_reason": churn_reasons
})

raw_output_path = "01_SaaS_Telecom_Customer_Churn/data/raw/telecom_customer_churn_raw.csv"
df.to_csv(raw_output_path, index=False)
print(f"Dataset generated successfully at: {raw_output_path}")
print(f"Total Rows: {len(df)}")
print(f"Churn Distribution:\n{df['churn_status'].value_counts(normalize=True)}")
