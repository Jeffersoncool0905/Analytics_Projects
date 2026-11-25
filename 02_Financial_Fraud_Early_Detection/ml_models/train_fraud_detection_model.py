"""
Train Machine Learning Fraud Detection & Risk Scoring Pipeline.
Author: Jefferson & Analytics Team
Evaluates:
- Imbalanced Learning (Balanced Random Forest)
- Precision-Recall AUC (PR-AUC) & ROC-AUC
- Exports:
  1. ml_models/fraud_model.joblib
  2. ml_models/feature_importance.csv
  3. data/processed/transactions_clean.csv
  4. data/processed/transactions_with_fraud_scores.csv
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score, confusion_matrix

# 1. Load Data
raw_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/data/raw/transactions_raw.csv"
df = pd.read_csv(raw_path)

# Save clean version
clean_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/data/processed/transactions_clean.csv"
df.to_csv(clean_path, index=False)
print(f"Clean transactions saved to: {clean_path}")

# 2. Features & Target
target = "is_fraud"
y = df[target]

numeric_features = [
    "transaction_amount",
    "customer_avg_ticket",
    "amount_to_avg_ratio",
    "distance_km",
    "trans_count_last_1h"
]

categorical_features = [
    "card_type",
    "merchant_category",
    "card_entry_mode",
    "device_type",
    "is_foreign_transaction"
]

X = df[numeric_features + categorical_features]

# 3. Train-Test Split (Stratified 80/20)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

# 4. Pipeline Setup
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), categorical_features)
    ]
)

rf_classifier = RandomForestClassifier(
    n_estimators=150,
    max_depth=9,
    min_samples_split=8,
    class_weight="balanced", # Handles fraud class imbalance
    random_state=42,
    n_jobs=-1
)

model_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", rf_classifier)
])

# 5. Fit Model
model_pipeline.fit(X_train, y_train)

# 6. Evaluate
y_prob = model_pipeline.predict_proba(X_test)[:, 1]
# Use risk-adjusted threshold: 0.40 catches more fraud while keeping false positives reasonable
y_pred = (y_prob >= 0.40).astype(int)

print("=== FRAUD CLASSIFICATION PERFORMANCE ===")
print(classification_report(y_test, y_pred, digits=4))
roc_auc = roc_auc_score(y_test, y_prob)
pr_auc = average_precision_score(y_test, y_prob)
print(f"ROC-AUC Score: {roc_auc:.4f}")
print(f"PR-AUC (Precision-Recall AUC): {pr_auc:.4f}")
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 7. Feature Importances
cat_names = model_pipeline.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_features)
all_feat_names = numeric_features + list(cat_names)
importances = model_pipeline.named_steps["classifier"].feature_importances_

feat_df = pd.DataFrame({
    "feature": all_feat_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

feat_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/ml_models/feature_importance.csv"
feat_df.to_csv(feat_path, index=False)
print(f"\nFeature importances saved to: {feat_path}")
print("Top 8 Fraud Predictors:\n", feat_df.head(8))

# 8. Save Serialized Model
model_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/ml_models/fraud_model.joblib"
joblib.dump(model_pipeline, model_path)
print(f"Model saved to: {model_path}")

# 9. Score Full Dataset for SQL, Power BI, and Tableau
all_probs = model_pipeline.predict_proba(X)[:, 1]
df["fraud_probability"] = np.round(all_probs, 4)
df["predicted_fraud"] = (all_probs >= 0.40).astype(int)

def assign_fraud_tier(prob):
    if prob >= 0.50:
        return "High Risk"
    elif prob >= 0.20:
        return "Medium Risk"
    else:
        return "Low Risk"

df["fraud_risk_tier"] = df["fraud_probability"].apply(assign_fraud_tier)
df["expected_fraud_loss"] = np.round(df["transaction_amount"] * df["fraud_probability"], 2)

scored_path = "Sales and Inventory/02_Financial_Fraud_Early_Detection/data/processed/transactions_with_fraud_scores.csv"
df.to_csv(scored_path, index=False)
print(f"Scored transactions saved to: {scored_path}")
