import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
import logging
warnings.filterwarnings('ignore')
logging.getLogger('cmdstanpy').setLevel(logging.WARNING)

def extract_time_features(dates):
    """Extract calendar features from a pandas DatetimeIndex or Series."""
    return pd.DataFrame({
        'dayofweek': dates.dt.dayofweek,
        'month': dates.dt.month,
        'year': dates.dt.year,
        'dayofyear': dates.dt.dayofyear,
        'is_weekend': dates.dt.dayofweek >= 5
    })

def main():
    print("1. Loading and aggregating daily data...")
    df = pd.read_csv('Store_inventory_data.csv')
    
    # Aggregate total sales across the entire chain for this model comparison
    daily_sales = df.groupby('Date')['Units Sold'].sum().reset_index()
    daily_sales['Date'] = pd.to_datetime(daily_sales['Date'])
    daily_sales = daily_sales.sort_values('Date')
    
    # Train-Test Split (Hold out the last 60 days for testing)
    test_days = 60
    train = daily_sales.iloc[:-test_days].copy()
    test = daily_sales.iloc[-test_days:].copy()
    print(f"Training set: {len(train)} days | Test set: {len(test)} days")
    
    results = pd.DataFrame({'Date': test['Date'], 'Actual': test['Units Sold']})
    
    # --- MODEL 1: PROPHET ---
    print("\n2. Training Facebook Prophet...")
    prophet_train = train.rename(columns={'Date': 'ds', 'Units Sold': 'y'})
    m_prophet = Prophet(yearly_seasonality=True, daily_seasonality=False)
    m_prophet.fit(prophet_train)
    
    future = m_prophet.make_future_dataframe(periods=test_days)
    prophet_forecast = m_prophet.predict(future)
    results['Prophet'] = prophet_forecast.iloc[-test_days:]['yhat'].values
    
    # --- MODEL 2: RANDOM FOREST ---
    print("3. Training Random Forest Regressor...")
    X_train = extract_time_features(train['Date'])
    y_train = train['Units Sold']
    X_test = extract_time_features(test['Date'])
    
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    results['Random_Forest'] = rf.predict(X_test)

    # --- MODEL 3: LINEAR REGRESSION ---
    print("4. Training Linear Regression Baseline...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    results['Linear_Regression'] = lr.predict(X_test)
    
    # --- EVALUATION ---
    print("\n=== Model Performance Comparison (Last 60 Days) ===")
    models = ['Prophet', 'Random_Forest', 'Linear_Regression']
    
    for model in models:
        mae = mean_absolute_error(results['Actual'], results[model])
        rmse = np.sqrt(mean_squared_error(results['Actual'], results[model]))
        print(f"{model.replace('_', ' '):<18} - MAE: {mae:>6.2f} | RMSE: {rmse:>6.2f}")
        
    # --- VISUALIZATION ---
    print("\n5. Generating Visualization...")
    plt.figure(figsize=(12, 6))
    plt.plot(results['Date'], results['Actual'], label='Actual Sales', color='black', linewidth=2)
    plt.plot(results['Date'], results['Prophet'], label='Prophet', linestyle='-', alpha=0.8)
    plt.plot(results['Date'], results['Random_Forest'], label='Random Forest', linestyle='--', alpha=0.8)
    plt.plot(results['Date'], results['Linear_Regression'], label='Linear Regression', linestyle=':', alpha=0.8)
    
    plt.title('Demand Forecasting: Model Comparison (Holdout Last 60 Days)')
    plt.xlabel('Date')
    plt.ylabel('Total Units Sold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plot_path = 'model_comparison.png'
    plt.savefig(plot_path)
    print(f"Visualization saved successfully to: {plot_path}")
    
    results.to_csv('predictions_comparison.csv', index=False)

if __name__ == "__main__":
    main()
