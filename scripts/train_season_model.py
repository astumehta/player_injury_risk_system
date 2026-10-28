"""
Train Logistic Regression Model on Harbourline FC Official 2,400 Player-Week Dataset
Foundations of AI for Business | Group Project 4 (Healthcare) | Group A1
Author: Astu Mehta (10289708)

Dataset Specifications:
- Source: Harbourline Football Club Premier League Season Tracking (data/harbourline_player_weeks.csv)
- Size: 2,400 player-weeks across 60 professional players (Squad A & B) and 40 in-season weeks
- Time Period: 40 in-season competitive weeks (plus 4 hidden pre-season weeks to seed chronic load)
- Target Variable: injury_next_7d (Binary: 1 if time-loss soft-tissue strain in next 7d, 0 otherwise; 94 injuries observed, 4.53% active incidence)
- Cleaning & Preprocessing:
  1. Filter out availability == 'out' (323 already injured player-weeks with blank label), leaving 2,077 active training player-weeks.
  2. Drop post-injury outcome leakage columns (injury_type, weeks_out).
  3. Feature engineering:
     - ACWR spike term: max(0, ACWR - 1.30)
     - ACWR detraining term: max(0, 0.80 - ACWR)
     - Prior soft-tissue injuries (0 to 5)
     - Muscle soreness spike: max(0, Soreness - 4.0)
     - Weekly sleep deficit: max(0, 7.0 - sleep_hours)
     - 3-week rolling sleep debt (scaled by 10.0)
     - Age term: max(0, Age - 26)
     - Low wellness flag: 1 if wellness <= 4 else 0
     - Return-to-play indicator: 1 if availability == 'modified' else 0
     - Positional one-hot encoding: GK (-0.56), MID (+0.13), FWD (+0.40) with DEF as baseline (0.00)
  4. GroupShuffleSplit on player_id (80% train / 20% test: 48 train players / 12 test players) to ensure no player leaks across train/test sets.
"""

import os
import warnings
warnings.filterwarnings('ignore')

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv")
MODEL_OUT_PATH = os.path.join(BASE_DIR, "models", "harbourline_logistic_season.pkl")
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "harbourline_logistic_1000.pkl")

def train_season_model():
    print("=" * 70)
    print("⚽ HARBOURLINE FC — OFFICIAL LOGISTIC REGRESSION TRAINING PIPELINE")
    print("Foundations of AI for Business | Astu Mehta (10289708)")
    print("=" * 70)

    print(f"\n📖 Loading official season dataset from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    total_rows = len(df)
    n_players = df["player_id"].nunique()
    n_weeks = df["week"].max()

    print(f"📊 Dataset Size: {total_rows} rows across {n_players} players (Squad A & B) and {n_weeks} weeks.")

    # 1. Cleaning: Drop weeks when player is already injured
    df_clean = df[df["availability"] != "out"].copy()
    active_rows = len(df_clean)
    n_injuries = int(df_clean["injury_next_7d"].sum())
    injury_rate = (n_injuries / active_rows) * 100

    print(f"🧹 Active Training Cohort: {active_rows} player-weeks (dropped {total_rows - active_rows} 'out' rows).")
    print(f"🎯 Target Variable (injury_next_7d): {n_injuries} injuries observed ({injury_rate:.2f}% active incidence).")

    # 2. Feature Engineering
    X = pd.DataFrame(index=df_clean.index)
    X["acwr_spike"] = np.maximum(0.0, df_clean["acwr"] - 1.30)
    X["acwr_detraining"] = np.maximum(0.0, 0.80 - df_clean["acwr"])
    X["prior_injuries"] = df_clean["prior_injuries"].astype(float)
    X["soreness_spike"] = np.maximum(0.0, df_clean["soreness"] - 4.0).astype(float)
    X["sleep_deficit"] = np.maximum(0.0, 7.0 - df_clean["sleep_hours"]).astype(float)
    X["sleep_debt_3w"] = (df_clean["sleep_debt_3w"] / 10.0).astype(float)
    X["age_term"] = np.maximum(0.0, df_clean["age"] - 26).astype(float)
    X["wellness_low"] = (df_clean["wellness"] <= 4).astype(float)
    X["is_returning"] = (df_clean["availability"] == "modified").astype(float)
    X["pos_gk"] = (df_clean["position"] == "GK").astype(float)
    X["pos_mid"] = (df_clean["position"] == "MID").astype(float)
    X["pos_fwd"] = (df_clean["position"] == "FWD").astype(float)

    y = df_clean["injury_next_7d"].astype(int)
    groups = df_clean["player_id"]

    # 3. GroupShuffleSplit by player_id
    gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    test_players = groups.iloc[test_idx].nunique()

    print(f"👥 Train/Test Split: {len(X_train)} train rows ({y_train.sum()} inj) | {len(X_test)} test rows ({y_test.sum()} inj across {test_players} held-out players).")

    # 4. Train Model
    clf = LogisticRegression(solver="liblinear", random_state=42, C=1.0)
    clf.fit(X_train, y_train)

    # 5. Evaluate Performance
    y_prob = clf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)
    acc = accuracy_score(y_test, (y_prob >= 0.15).astype(int))

    print("\n" + "=" * 70)
    print("🎯 MODEL EVALUATION RESULTS (Held-Out Test Set):")
    print(f"   • Test ROC-AUC Score: {auc:.4f} (~{auc*100:.1f}%)")
    print(f"   • Test Accuracy:     {acc*100:.2f}%")
    print(f"   • Base Intercept b0: {clf.intercept_[0]:.4f}")
    print("=" * 70)

    weights_dict = {}
    print("\n📐 LEARNED WEIGHTS & SPORTS SCIENCE ODDS RATIOS:")
    for col, coef in zip(X.columns, clf.coef_[0]):
        or_val = np.exp(coef)
        weights_dict[col] = float(coef)
        print(f"   {col:16s}: {coef:+.4f} (Odds Ratio: {or_val:.3f}x)")

    # 6. Save Model Artifacts
    bundle = {
        "model": clf,
        "feature_names": X.columns.tolist(),
        "intercept": float(clf.intercept_[0]),
        "weights": weights_dict,
        "metrics": {
            "roc_auc": float(auc),
            "accuracy": float(acc),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "total_active_samples": active_rows,
            "total_raw_rows": total_rows,
            "total_injuries": n_injuries
        },
        "dataset_metadata": {
            "source": "Harbourline Football Club Season Tracking (player_weeks.csv)",
            "size": f"{total_rows} rows (2,077 active training player-weeks across 60 players)",
            "time_period": "40 In-Season Competitive Weeks (Weeks 1 to 40)",
            "target_variable": "injury_next_7d (Binary: 1 if time-loss strain in next 7d, 0 otherwise)",
            "cleaning_steps": [
                "1. Filtered out weeks where availability == 'out' (323 already injured player-weeks)",
                "2. Excluded post-injury outcome leakage columns (injury_type, weeks_out)",
                "3. Group-aware splitting (GroupShuffleSplit on player_id) so no athlete leaks across train/test",
                "4. Engineered sports-science non-linear splines (ACWR spikes >1.30, detraining <0.80)",
                "5. Normalized 3-week sleep debt (/10) and muscle soreness spike (>4.0)"
            ]
        }
    }
    joblib.dump(bundle, MODEL_OUT_PATH)
    joblib.dump(bundle, DEFAULT_MODEL_PATH)
    print(f"\n💾 Model successfully saved to:")
    print(f"   • {MODEL_OUT_PATH}")
    print(f"   • {DEFAULT_MODEL_PATH}")

if __name__ == "__main__":
    train_season_model()
