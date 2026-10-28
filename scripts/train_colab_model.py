"""
Harbourline FC — Logistic Regression Model Training Script
Trained on 1,000 Synthetic Football Players (Google Colab Training Pipeline)
Group A1: Foundations of AI for Business | Astu Mehta (10289708)

Pipeline:
1. Load 1,000-player dataset (training_players_1000.csv)
2. Sports-science feature engineering matching protocol.md
3. Train scikit-learn LogisticRegression classifier
4. Evaluate with ROC-AUC, Accuracy, Precision, Recall & Confusion Matrix
5. Save trained model to models/harbourline_logistic_1000.pkl
6. Apply model to Harbourline FC's 60 Senior Squad players
"""

import os
import joblib
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CSV = os.path.join(BASE_DIR, "data", "training_players_1000.csv")
SQUAD_CSV = os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv")
MODEL_PKL = os.path.join(BASE_DIR, "models", "harbourline_logistic_1000.pkl")

FEATURE_COLS = [
    "acwr_spike",
    "acwr_detraining",
    "prior_injuries",
    "soreness_spike",
    "sleep_deficit",
    "sleep_debt_3w",
    "age_term",
    "wellness_low",
    "is_returning",
    "pos_gk",
    "pos_mid",
    "pos_fwd"
]

def engineer_features(df):
    """Transforms raw player numbers into sports science logit terms."""
    acwr = df["acwr"].astype(float)
    soreness = df["soreness"].astype(float)
    sleep_h = df["sleep_hours"].astype(float)
    sleep_debt = df["sleep_debt_3w"].astype(float)
    age = df["age"].astype(float)
    wellness = df["wellness"].astype(float)
    pos = df["position"].astype(str).str.upper()
    prior = df["prior_injuries"].astype(float)
    
    # is_returning check
    if "is_returning" in df.columns:
        is_ret = df["is_returning"].fillna(0).astype(float)
    elif "weeks_since_return" in df.columns:
        is_ret = df["weeks_since_return"].apply(lambda w: 1.0 if pd.notna(w) and w in [1, 2, 1.0, 2.0] else 0.0)
    else:
        is_ret = pd.Series(0.0, index=df.index)

    X = pd.DataFrame({
        "acwr_spike": np.maximum(0.0, acwr - 1.30),
        "acwr_detraining": np.maximum(0.0, 0.80 - acwr),
        "prior_injuries": prior,
        "soreness_spike": np.maximum(0.0, soreness - 4.0),
        "sleep_deficit": np.maximum(0.0, 7.0 - sleep_h),
        "sleep_debt_3w": sleep_debt / 10.0,  # Scaled to tens of hours for numerical stability
        "age_term": np.maximum(0.0, age - 26.0),
        "wellness_low": (wellness <= 4.0).astype(float),
        "is_returning": is_ret,
        "pos_gk": (pos == "GK").astype(float),
        "pos_mid": (pos == "MID").astype(float),
        "pos_fwd": (pos == "FWD").astype(float)
    }, index=df.index)
    return X

def train_and_export_model():
    print("=" * 70)
    print("HARBOURLINE FC — LOGISTIC REGRESSION TRAINING PIPELINE")
    print("Trained on 1,000 Synthetic Professional Football Players")
    print("=" * 70)

    # 1. Load Data
    df = pd.read_csv(DATA_CSV)
    print(f"\n📁 Loaded training dataset: {len(df)} player records from {DATA_CSV}")
    print(f"   • Total Players: {len(df)}")
    print(f"   • Target (Injury in next 7d): {df['injury_next_7d'].sum()} positive ({df['injury_next_7d'].mean()*100:.1f}%)")

    # 2. Engineer Features
    X = engineer_features(df)
    y = df["injury_next_7d"].values

    # 3. Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"   • Train set: {len(X_train)} samples | Test set: {len(X_test)} samples")

    # 4. Train Logistic Regression
    clf = LogisticRegression(solver="lbfgs", max_iter=1000, C=1.0, random_state=42)
    clf.fit(X_train, y_train)

    # 5. Evaluate on Test Set
    test_probs = clf.predict_proba(X_test)[:, 1]
    test_preds = (test_probs >= 0.15).astype(int)  # 15% High risk threshold
    auc = roc_auc_score(y_test, test_probs)
    acc = accuracy_score(y_test, test_preds)

    print("\n📊 MODEL EVALUATION ON 20% HELD-OUT TEST SET:")
    print(f"   • ROC-AUC Score: {auc:.4f} (High discriminative capacity)")
    print(f"   • Accuracy:      {acc*100:.1f}%")
    print(f"   • Intercept b₀:  {clf.intercept_[0]:.4f}")

    print("\n📈 LEARNED MODEL WEIGHTS (SPORTS SCIENCE INTERPRETATION):")
    coef_dict = dict(zip(FEATURE_COLS, clf.coef_[0]))
    for feat, w in coef_dict.items():
        odds_ratio = np.exp(w)
        print(f"   • {feat:18s} | Weight: {w:+.4f} | Odds Ratio: {odds_ratio:.3f}x")

    # 6. Save Model Bundle
    model_bundle = {
        "model": clf,
        "feature_names": FEATURE_COLS,
        "intercept": float(clf.intercept_[0]),
        "weights": {k: float(v) for k, v in coef_dict.items()},
        "metrics": {
            "roc_auc": float(auc),
            "accuracy": float(acc),
            "n_train": len(X_train),
            "n_test": len(X_test)
        }
    }
    os.makedirs(os.path.dirname(MODEL_PKL), exist_ok=True)
    joblib.dump(model_bundle, MODEL_PKL)
    print(f"\n💾 Model successfully exported to: {MODEL_PKL}")

    # 7. Apply to Harbourline FC 60 Senior Squad Players
    if os.path.exists(SQUAD_CSV):
        squad_df = pd.read_csv(SQUAD_CSV)
        latest_squad = squad_df.sort_values("week").groupby("player_id").last().reset_index()
        X_squad = engineer_features(latest_squad)
        squad_probs = clf.predict_proba(X_squad)[:, 1]

        # Classify using Club Rulebook Thresholds:
        # LOW: P < 5.0%, MODERATE: 5.0% <= P < 15.0%, HIGH: P >= 15.0%
        tiers = []
        for p in squad_probs:
            if p >= 0.15:
                tiers.append("🔴 HIGH RISK (Can't Train / Benched)")
            elif p >= 0.05:
                tiers.append("🟡 MODERATE RISK (Need Some Help)")
            else:
                tiers.append("🟢 LOW RISK (Available to Train)")

        latest_squad["predicted_prob_pct"] = np.round(squad_probs * 100.0, 1)
        latest_squad["risk_tier"] = tiers

        print("\n⚽ VERIFICATION ON 60 HARBOURLINE FC SQUAD PLAYERS:")
        tier_counts = latest_squad["risk_tier"].value_counts()
        for t, count in tier_counts.items():
            print(f"   • {t:40s}: {count} players")

        print("\nSample Squad Predictions:")
        sample_cols = ["player_id", "position", "acwr", "soreness", "sleep_hours", "predicted_prob_pct", "risk_tier"]
        print(latest_squad[latest_squad["player_id"].isin(["P001", "P004", "P046", "P051"])][sample_cols].to_string(index=False))

    return model_bundle

if __name__ == "__main__":
    train_and_export_model()
