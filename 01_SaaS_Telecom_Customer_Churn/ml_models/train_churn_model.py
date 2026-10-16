"""
Train Churn Prediction & Risk Scoring Model (Scikit-Learn).
Author: Jefferson
Exports:
1. ml_models/churn_model.joblib: Serialized ML Pipeline
2. ml_models/feature_importance.csv: Top factors driving churn
3. data/processed/telecom_customer_churn_with_predictions.csv: Full dataset with ML scores
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix

# 1. Load Clean Data
data_path = "01_SaaS_Telecom_Customer_Churn/data/processed/telecom_customer_churn_clean.csv"
df = pd.read_csv(data_path)

# 2. Define Features & Target
target = "churn_status"
y = (df[target] == "Yes").astype(int)

numeric_features = [
    "tenure_months",
    "monthly_charges",
    "total_charges",
    "support_tickets",
    "monthly_usage_gb"
]

categorical_features = [
    "contract_type",
    "internet_service",
    "tech_support",
    "online_security",
    "online_backup",
    "device_protection",
    "payment_method",
    "paperless_billing",
    "senior_citizen",
    "partner",
    "dependents"
]

X = df[numeric_features + categorical_features]

# 3. Train / Test Split
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
    max_depth=8,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1
)

model_pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", rf_classifier)
])

# 5. Model Training
model_pipeline.fit(X_train, y_train)

# 6. Evaluation
y_pred = model_pipeline.predict(X_test)
y_prob = model_pipeline.predict_proba(X_test)[:, 1]

print("=== MODEL PERFORMANCE REPORT ===")
print(classification_report(y_test, y_pred, digits=4))
roc_auc = roc_auc_score(y_test, y_prob)
print(f"ROC-AUC Score: {roc_auc:.4f}")
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))

# 7. Feature Importance Extraction
encoded_cat_names = model_pipeline.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_features)
all_feature_names = numeric_features + list(encoded_cat_names)
importances = model_pipeline.named_steps["classifier"].feature_importances_

feature_imp_df = pd.DataFrame({
    "feature": all_feature_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

feat_imp_path = "01_SaaS_Telecom_Customer_Churn/ml_models/feature_importance.csv"
feature_imp_df.to_csv(feat_imp_path, index=False)
print(f"Feature importances saved to: {feat_imp_path}")
print("\nTop 8 Churn Drivers:\n", feature_imp_df.head(8))

# 8. Save Serialized Model
model_save_path = "01_SaaS_Telecom_Customer_Churn/ml_models/churn_model.joblib"
joblib.dump(model_pipeline, model_save_path)
print(f"Serialized model saved to: {model_save_path}")

# 9. Score the Full Dataset for SQL & Power BI
all_probs = model_pipeline.predict_proba(X)[:, 1]
df["churn_probability"] = np.round(all_probs, 4)
df["predicted_churn"] = (all_probs >= 0.50).astype(int)

def assign_risk_tier(prob):
    if prob >= 0.65:
        return "High Risk"
    elif prob >= 0.35:
        return "Medium Risk"
    else:
        return "Low Risk"

df["churn_risk_tier"] = df["churn_probability"].apply(assign_risk_tier)

scored_csv_path = "01_SaaS_Telecom_Customer_Churn/data/processed/telecom_customer_churn_with_predictions.csv"
df.to_csv(scored_csv_path, index=False)
print(f"Scored dataset with predictions saved to: {scored_csv_path}")
