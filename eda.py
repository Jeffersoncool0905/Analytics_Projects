import pandas as pd
import numpy as np

def run_eda():
    print("Loading dataset...")
    df = pd.read_csv('Store_inventory_data.csv')
    
    print("\n==================================")
    print("      DATASET OVERVIEW            ")
    print("==================================")
    
    print(f"\nTotal Records: {len(df)}")
    
    print("\n--- Date Range ---")
    print(f"Start: {df['Date'].min()} | End: {df['Date'].max()}")
    
    print("\n--- Missing Values ---")
    missing = df.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "No missing values found!")
    
    print("\n--- Top 5 Categories ---")
    print(df['Category'].value_counts().head(5))
    
    print("\n--- Key Statistics ---")
    print(df[['Inventory Level', 'Units Sold', 'Price', 'Discount']].describe().round(2))

if __name__ == "__main__":
    run_eda()
