"""
Generate realistic Financial & E-Commerce Fraud Detection Dataset.
Author: Jefferson & Analytics Team
Dataset features: 10,000 financial transactions with velocity, geospatial, device, and behavioral risk patterns.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
n_records = 10000

# 1. Base Entities
n_customers = 1500
customer_ids = [f"CUST-{2000 + i}" for i in range(n_customers)]
card_types = ["Visa", "Mastercard", "Amex", "Discover"]
card_mapping = {
    c_id: {
        "card_number_masked": f"{np.random.choice(['4111', '5200', '3782', '6011'])}-XXXX-XXXX-{np.random.randint(1000, 9999)}",
        "card_type": np.random.choice(card_types, p=[0.48, 0.35, 0.12, 0.05]),
        "customer_home_country": np.random.choice(["USA", "Canada", "UK"], p=[0.75, 0.15, 0.10]),
        "home_lat": np.random.uniform(25.0, 48.0),
        "home_long": np.random.uniform(-120.0, -75.0),
        "avg_ticket": round(np.random.uniform(45.0, 180.0), 2)
    }
    for c_id in customer_ids
}

# Merchant Pool
merchant_categories = [
    "E-Commerce & Digital Goods",
    "Grocery & Supermarket",
    "Gas & Fuel Stations",
    "Dining & Restaurants",
    "Travel & Airlines",
    "Luxury Retail & Jewelry",
    "Gaming & Online Gambling"
]

merchants = [
    ("Amazon.com", "E-Commerce & Digital Goods", "USA"),
    ("Apple Online Store", "E-Commerce & Digital Goods", "USA"),
    ("Walmart Supercenter", "Grocery & Supermarket", "USA"),
    ("Shell Gas Station", "Gas & Fuel Stations", "USA"),
    ("Uber Technologies", "Travel & Airlines", "USA"),
    ("Delta Air Lines", "Travel & Airlines", "USA"),
    ("Steam Games Store", "Gaming & Online Gambling", "USA"),
    ("Tiffany & Co", "Luxury Retail & Jewelry", "USA"),
    ("Starbucks Coffee", "Dining & Restaurants", "USA"),
    ("AliExpress Direct", "E-Commerce & Digital Goods", "China"),
    ("Best Buy Electronics", "E-Commerce & Digital Goods", "USA"),
    ("Target Corp", "Grocery & Supermarket", "USA"),
    ("Marriott Hotels", "Travel & Airlines", "France"),
    ("DraftKings Sportsbook", "Gaming & Online Gambling", "UK"),
    ("Rolex Boutique", "Luxury Retail & Jewelry", "UK")
]

start_time = datetime(2026, 1, 1, 0, 0, 0)

data = []
curr_time = start_time

for i in range(n_records):
    txn_id = f"TXN-{100001 + i}"
    # increment time
    time_jump = np.random.exponential(scale=12.0) # minutes
    curr_time += timedelta(minutes=time_jump)
    
    cust_id = np.random.choice(customer_ids)
    cust_profile = card_mapping[cust_id]
    
    # Pick merchant
    m_name, m_cat, m_country = merchants[np.random.choice(len(merchants))]
    
    # Entry mode
    if m_cat in ["E-Commerce & Digital Goods", "Gaming & Online Gambling"]:
        entry_mode = "Online / E-Commerce (CNP)"
        device = np.random.choice(["Desktop (Windows)", "Desktop (Mac)", "Mobile (iOS)", "Mobile (Android)"])
    else:
        entry_mode = np.random.choice(["Chip (EMV)", "Contactless / NFC", "Swipe / Magstripe"], p=[0.60, 0.35, 0.05])
        device = "POS Terminal"
        
    # Standard transaction amount
    base_amount = max(2.50, np.random.normal(loc=cust_profile["avg_ticket"], scale=cust_profile["avg_ticket"] * 0.4))
    
    # Determine fraud scenario injection (~3.5% total fraud)
    is_fraud = 0
    fraud_scenario = "Normal Transaction"
    
    dice_roll = np.random.rand()
    
    if dice_roll < 0.035:
        is_fraud = 1
        scenario_choice = np.random.choice(["Card Testing Velocity", "Impossible Travel", "High-Value Luxury Spike", "Account Takeover (ATO)"])
        fraud_scenario = scenario_choice
        
        if scenario_choice == "High-Value Luxury Spike":
            luxury_options = [
                ("Tiffany & Co", "Luxury Retail & Jewelry", "USA"),
                ("Rolex Boutique", "Luxury Retail & Jewelry", "UK"),
                ("Best Buy Electronics", "E-Commerce & Digital Goods", "USA")
            ]
            m_name, m_cat, m_country = luxury_options[np.random.choice(len(luxury_options))]
            base_amount = np.random.uniform(1200.0, 4800.0)
            entry_mode = "Online / E-Commerce (CNP)"
            
        elif scenario_choice == "Impossible Travel":
            # Distance far away from home
            m_country = np.random.choice(["Russia", "Nigeria", "Brazil", "China"])
            entry_mode = "Swipe / Magstripe"
            base_amount = np.random.uniform(250.0, 1100.0)
            
        elif scenario_choice == "Card Testing Velocity":
            base_amount = np.random.choice([1.00, 2.00, 4.99, 9.99])
            m_name = "Steam Games Store"
            m_cat = "Gaming & Online Gambling"
            entry_mode = "Online / E-Commerce (CNP)"
            
        elif scenario_choice == "Account Takeover (ATO)":
            device = "Desktop (Windows)"
            m_country = "Nigeria"
            base_amount = np.random.uniform(850.0, 2900.0)
            entry_mode = "Online / E-Commerce (CNP)"

    # Geospatial coords
    if is_fraud and fraud_scenario == "Impossible Travel":
        merchant_lat = np.random.uniform(-30.0, 60.0)
        merchant_long = np.random.uniform(20.0, 110.0)
    else:
        merchant_lat = cust_profile["home_lat"] + np.random.normal(0, 0.25)
        merchant_long = cust_profile["home_long"] + np.random.normal(0, 0.25)
        
    distance_km = round(np.sqrt((merchant_lat - cust_profile["home_lat"])**2 + (merchant_long - cust_profile["home_long"])**2) * 111.0, 2)
    
    data.append({
        "transaction_id": txn_id,
        "trans_timestamp": curr_time.strftime("%Y-%m-%d %H:%M:%S"),
        "customer_id": cust_id,
        "card_number_masked": cust_profile["card_number_masked"],
        "card_type": cust_profile["card_type"],
        "customer_home_country": cust_profile["customer_home_country"],
        "merchant_name": m_name,
        "merchant_category": m_cat,
        "merchant_country": m_country,
        "card_entry_mode": entry_mode,
        "device_type": device,
        "transaction_amount": round(base_amount, 2),
        "customer_avg_ticket": cust_profile["avg_ticket"],
        "amount_to_avg_ratio": round(base_amount / cust_profile["avg_ticket"], 2),
        "distance_km": distance_km,
        "is_foreign_transaction": 1 if m_country != cust_profile["customer_home_country"] else 0,
        "is_fraud": is_fraud,
        "fraud_scenario": fraud_scenario
    })

df = pd.DataFrame(data)

# Sort by timestamp
df["trans_timestamp"] = pd.to_datetime(df["trans_timestamp"])
df = df.sort_values(by="trans_timestamp").reset_index(drop=True)

# Calculate rolling velocity: transactions per card in last 1 hour
df["trans_count_last_1h"] = 1
for cid, group in df.groupby("customer_id"):
    times = group["trans_timestamp"].values
    counts = []
    for t in times:
        c = ((times <= t) & (times >= t - np.timedelta64(1, 'h'))).sum()
        counts.append(c)
    df.loc[group.index, "trans_count_last_1h"] = counts

# Save raw dataset
raw_csv = "Sales and Inventory/02_Financial_Fraud_Early_Detection/data/raw/transactions_raw.csv"
df.to_csv(raw_csv, index=False)
print(f"Generated {len(df)} transactions.")
print(f"Total Fraud Cases: {df['is_fraud'].sum()} ({df['is_fraud'].mean():.2%})")
print(df["fraud_scenario"].value_counts())
