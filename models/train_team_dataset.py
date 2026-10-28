"""
Train Logistic Regression Model on Harbourline FC synthetic season dataset (Group A1).
Adheres to DATA_README.md:
- Excludes weeks where availability == 'out'
- Computes 3-week sleep debt: sum(max(0.0, 7.5 - s) * 7 for s in sleeps[-3:])
- Features: acwr, acwr_spike (>1.3), acwr_under (<0.8), prior_injuries, soreness, sleep_hours, sleep_short (<7), sleep_debt_3w, age, wellness_low (<=4), is_returning (weeks_since_return in [1, 2]), position dummies
- Evaluates AUC and Recall at top 15% threshold (~16% of weeks flagged)
- Saves model bundle for instant, explainable inference
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, recall_score, precision_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "team_assets", "player_weeks.csv")
ORACLE_PATH = os.path.join(BASE_DIR, "team_assets", "oracle_probabilities.csv")

def prepare_features(df):
    # Sort to compute rolling sleep debt accurately per player
    df = df.sort_values(by=["player_id", "week"]).copy()
    
    # Calculate 3-week rolling sleep debt
    sleep_debts = []
    player_sleep_history = {}
    
    for idx, row in df.iterrows():
        pid = row["player_id"]
        sh = row["sleep_hours"]
        if pid not in player_sleep_history:
            player_sleep_history[pid] = []
        player_sleep_history[pid].append(sh)
        recent_sleeps = player_sleep_history[pid][-3:]
        debt = sum(max(0.0, 7.5 - s) * 7.0 for s in recent_sleeps)
        sleep_debts.append(round(debt, 1))
        
    df["sleep_debt_3w"] = sleep_debts
    
    # Feature engineering as specified in DATA_README.md Section 4
    df["acwr_above_13"] = np.maximum(0.0, df["acwr"] - 1.3)
    df["acwr_below_08"] = np.maximum(0.0, 0.8 - df["acwr"])
    df["sleep_below_7"] = np.maximum(0.0, 7.0 - df["sleep_hours"])
    df["wellness_low"] = (df["wellness"] <= 4).astype(float)
    df["soreness_above_4"] = np.maximum(0.0, df["soreness"] - 4.0)
    df["is_returning"] = df["weeks_since_return"].isin([1, 2]).astype(float)
    df["is_fwd"] = (df["position"] == "FWD").astype(float)
    df["is_mid"] = (df["position"] == "MID").astype(float)
    df["is_gk"] = (df["position"] == "GK").astype(float)
    
    return df

def train():
    df_raw = pd.read_csv(CSV_PATH)
    df = prepare_features(df_raw)
    
    # Drop rows where player is already injured (availability == 'out')
    trainable_df = df[df["availability"] != "out"].copy()
    
    feature_cols = [
        "acwr",
        "acwr_above_13",
        "acwr_below_08",
        "prior_injuries",
        "soreness",
        "soreness_above_4",
        "sleep_hours",
        "sleep_below_7",
        "sleep_debt_3w",
        "age",
        "wellness",
        "wellness_low",
        "is_returning",
        "is_fwd",
        "is_mid",
        "is_gk"
    ]
    
    feature_labels = {
        "acwr": "Acute:Chronic Workload Ratio (ACWR)",
        "acwr_above_13": "ACWR Spike (>1.30)",
        "acwr_below_08": "Under-training / Detraining (ACWR <0.80)",
        "prior_injuries": "Prior Soft-Tissue Injuries",
        "soreness": "Muscle Soreness (1-10)",
        "soreness_above_4": "Elevated Soreness (>4)",
        "sleep_hours": "Average Sleep Duration (Hours)",
        "sleep_below_7": "Short Sleep (<7h)",
        "sleep_debt_3w": "3-Week Accumulated Sleep Debt (Hours)",
        "age": "Player Age",
        "wellness": "Subjective Wellness (1-10)",
        "wellness_low": "Low Wellness Warning (≤4)",
        "is_returning": "Recent Return-to-Play Stage",
        "is_fwd": "Position: Forward",
        "is_mid": "Position: Midfielder",
        "is_gk": "Position: Goalkeeper"
    }
    
    # Split by player: 42 train players, 18 test players (DATA_README.md)
    unique_pids = trainable_df["player_id"].unique()
    train_pids = unique_pids[:42]
    test_pids = unique_pids[42:]
    
    train_mask = trainable_df["player_id"].isin(train_pids)
    test_mask = trainable_df["player_id"].isin(test_pids)
    
    X_train = trainable_df.loc[train_mask, feature_cols]
    y_train = trainable_df.loc[train_mask, "injury_next_7d"].astype(int)
    
    X_test = trainable_df.loc[test_mask, feature_cols]
    y_test = trainable_df.loc[test_mask, "injury_next_7d"].astype(int)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LogisticRegression(class_weight="balanced", random_state=42, solver="liblinear", C=0.2, max_iter=500)
    model.fit(X_train_scaled, y_train)
    
    # Predict probabilities
    y_probs_train = model.predict_proba(X_train_scaled)[:, 1]
    y_probs_test = model.predict_proba(X_test_scaled)[:, 1]
    
    # Threshold for top 15% risk flags (~85th percentile of probabilities)
    threshold = float(np.percentile(y_probs_train, 85))
    y_preds_test = (y_probs_test >= threshold).astype(int)
    
    auc = float(roc_auc_score(y_test, y_probs_test))
    rec = float(recall_score(y_test, y_preds_test))
    prec = float(precision_score(y_test, y_preds_test))
    
    # Baseline ACWR > 1.5 comparison
    base_preds_test = (X_test["acwr"] > 1.5).astype(int)
    base_auc = float(roc_auc_score(y_test, X_test["acwr"]))
    base_rec = float(recall_score(y_test, base_preds_test))
    base_prec = float(precision_score(y_test, base_preds_test))
    
    print(f"Model Trained on Harbourline FC dataset.")
    print(f"Logistic Regression: AUC = {auc:.2f}, Recall = {rec:.2f}, Precision = {prec:.2f}, Threshold = {threshold:.3f}")
    print(f"Baseline (ACWR > 1.5): AUC = {base_auc:.2f}, Recall = {base_rec:.2f}, Precision = {base_prec:.2f}")
    
    # Save model bundle
    bundle = {
        "scaler": scaler,
        "model": model,
        "threshold": threshold,
        "feature_cols": feature_cols,
        "feature_labels": feature_labels
    }
    
    model_dir = os.path.join(BASE_DIR, "models")
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(bundle, os.path.join(model_dir, "harbourline_model.pkl"))
    
    # Save updated dataset with rolling sleep debt
    df.to_csv(os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv"), index=False)
    print("Saved harbourline_model.pkl and harbourline_player_weeks.csv")

if __name__ == "__main__":
    train()
