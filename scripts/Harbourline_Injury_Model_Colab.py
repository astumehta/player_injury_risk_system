# ==============================================================================
# ⚽ HARBOURLINE FC — OFFICIAL INJURY LOGISTIC REGRESSION MODEL
# Foundations of AI for Business | Group Project 4 (Healthcare) | Group A1
# Astu Mehta (10289708) | 2,400 Player-Week Official Season Pipeline
# ==============================================================================
# 📋 DATASET SPECIFICATIONS:
#   • Source: Harbourline FC Premier League Performance Analytics & GPS Catapult tracking
#   • Size: 2,400 player-weeks (60 players: Squad A & B, across 40 competitive weeks)
#   • Active Training Size: 2,077 player-weeks (323 already injured 'out' weeks excluded)
#   • Time Period: Full 40-week competitive season (Weeks 1 to 40)
#   • Target Variable: injury_next_7d (Binary: 1 if time-loss strain in next 7d, 0 otherwise)
#   • Total Observed Injuries: 94 injuries across 37 players (4.53% active incidence rate)
#   • Cleaning & Preprocessing:
#       1. Filtered out weeks where availability == 'out' (already injured, no new risk)
#       2. Excluded post-injury outcome columns (injury_type, weeks_out)
#       3. GroupShuffleSplit on player_id (48 train players / 12 test players)
#       4. Non-linear workload terms: ACWR spike (>1.30) & ACWR detraining (<0.80)
#       5. Scaled 3-week sleep debt (/10) and soreness threshold (>4.0)
# ==============================================================================

import os
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score, classification_report

print("=" * 72)
print("⚽ HARBOURLINE FC — OFFICIAL INJURY LOGISTIC REGRESSION PIPELINE")
print("Foundations of AI for Business | Astu Mehta (10289708)")
print("=" * 72)

# ------------------------------------------------------------------------------
# 1. LOAD & INSPECT DATASET
# ------------------------------------------------------------------------------
csv_filename = "player_weeks.csv"
if not os.path.exists(csv_filename):
    for fallback in [
        "/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/team_assets/player_weeks.csv",
        "/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/data/harbourline_player_weeks.csv",
        "data/harbourline_player_weeks.csv"
    ]:
        if os.path.exists(fallback):
            csv_filename = fallback
            break

df = pd.read_csv(csv_filename)
print(f"\n📊 Loaded Season Dataset: {len(df)} rows across {df['player_id'].nunique()} players and {df['week'].max()} weeks.")

# ------------------------------------------------------------------------------
# 2. DATA CLEANING & FEATURE ENGINEERING
# ------------------------------------------------------------------------------
df_clean = df[df["availability"] != "out"].copy()
n_injuries = int(df_clean["injury_next_7d"].sum())
print(f"🧹 Active Training Cohort: {len(df_clean)} player-weeks (dropped {(df['availability'] == 'out').sum()} 'out' rows).")
print(f"🎯 Target Variable (injury_next_7d): {n_injuries} injuries observed ({n_injuries/len(df_clean)*100:.2f}% active incidence).")

def build_features(d):
    X = pd.DataFrame(index=d.index)
    X["acwr_spike"] = np.maximum(0.0, d["acwr"] - 1.30)
    X["acwr_detraining"] = np.maximum(0.0, 0.80 - d["acwr"])
    X["prior_injuries"] = d["prior_injuries"].astype(float)
    X["soreness_spike"] = np.maximum(0.0, d["soreness"] - 4.0).astype(float)
    X["sleep_deficit"] = np.maximum(0.0, 7.0 - d["sleep_hours"]).astype(float)
    
    if "sleep_debt_3w" in d.columns:
        X["sleep_debt_3w"] = (d["sleep_debt_3w"] / 10.0).astype(float)
    else:
        sleep_diff = np.maximum(0.0, 8.0 - d["sleep_hours"])
        X["sleep_debt_3w"] = (sleep_diff * 7.0) / 10.0
        
    X["age_term"] = np.maximum(0.0, d["age"] - 26).astype(float)
    X["wellness_low"] = (d["wellness"] <= 4).astype(float)
    X["is_returning"] = (d["availability"] == "modified").astype(float)
    X["pos_gk"] = (d["position"] == "GK").astype(float)
    X["pos_mid"] = (d["position"] == "MID").astype(float)
    X["pos_fwd"] = (d["position"] == "FWD").astype(float)
    return X

X = build_features(df_clean)
y = df_clean["injury_next_7d"].astype(int)
groups = df_clean["player_id"]

# ------------------------------------------------------------------------------
# 3. GROUP-AWARE TRAIN/TEST SPLIT & FITTING
# ------------------------------------------------------------------------------
gss = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)
train_idx, test_idx = next(gss.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

print(f"\n👥 Train/Test Split: {len(X_train)} train rows ({y_train.sum()} inj) | {len(X_test)} test rows ({y_test.sum()} inj across {groups.iloc[test_idx].nunique()} held-out players).")

model = LogisticRegression(solver="liblinear", random_state=42, C=1.0)
model.fit(X_train, y_train)

# ------------------------------------------------------------------------------
# 4. EVALUATION METRICS
# ------------------------------------------------------------------------------
y_prob = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_prob)
acc = accuracy_score(y_test, (y_prob >= 0.15).astype(int))

print("\n" + "=" * 72)
print("🎯 MODEL EVALUATION RESULTS (Held-Out Test Set):")
print(f"   • Test ROC-AUC Score: {auc:.4f} (~{auc*100:.1f}%)")
print(f"   • Test Accuracy:     {acc * 100:.2f}%")
print(f"   • Base Intercept b0: {model.intercept_[0]:.4f}")
print("=" * 72)

# Learned coefficients & odds ratios
coefs = model.coef_[0]
weights_df = pd.DataFrame({
    "Parameter": X.columns.tolist(),
    "Weight (w_i)": np.round(coefs, 4),
    "Odds Ratio": [f"{np.exp(c):.3f}x" for c in coefs]
})
print("\n📐 LEARNED WEIGHTS & ODDS RATIOS:")
print(weights_df.to_string(index=False))

# ------------------------------------------------------------------------------
# 5. LIVE INFERENCE ON 60 SQUAD PLAYERS (WEEK 40)
# ------------------------------------------------------------------------------
print("\n" + "=" * 72)
print("⚽ STEP 5: APPLYING MODEL TO 60 SQUAD PLAYERS AT WEEK 40")
print("=" * 72)

latest_60 = df.sort_values("week").groupby("player_id").last().reset_index()
X_60 = build_features(latest_60)
probs_60 = model.predict_proba(X_60)[:, 1]

tiers, statuses = [], []
for p in probs_60:
    if p >= 0.15:
        tiers.append("🔴 HIGH RISK")
        statuses.append("Can't Train / Benched")
    elif p >= 0.05:
        tiers.append("🟡 MODERATE RISK")
        statuses.append("Need Some Help / Modified")
    else:
        tiers.append("🟢 LOW RISK")
        statuses.append("Available to Train")

latest_60["Risk (%)"] = np.round(probs_60 * 100, 1)
latest_60["Risk Tier"] = tiers
latest_60["Coach Status"] = statuses

print("\n🎯 WEEK 40 ROSTER SUMMARY:")
print(latest_60["Coach Status"].value_counts().to_string())

print("\n🔍 KEY BENCHMARK PLAYERS:")
sample_pids = ["P046", "P001", "P004", "P014", "P051"]
print(latest_60[latest_60["player_id"].isin(sample_pids)][["player_id", "position", "acwr", "soreness", "sleep_hours", "wellness", "Risk (%)", "Risk Tier", "Coach Status"]].to_string(index=False))

# ------------------------------------------------------------------------------
# 6. EXPORT MODEL ARTIFACT (.PKL)
# ------------------------------------------------------------------------------
bundle = {
    "model": model,
    "feature_names": X.columns.tolist(),
    "intercept": float(model.intercept_[0]),
    "weights": dict(zip(X.columns.tolist(), [float(c) for c in coefs])),
    "metrics": {"roc_auc": float(auc), "accuracy": float(acc)}
}
try:
    joblib.dump(bundle, "harbourline_logistic_season.pkl")
    print("\n💾 Model bundle saved to 'harbourline_logistic_season.pkl'")
except Exception as e:
    print(f"\n⚠️ Saved in memory ({e})")

print("🎉 Google Colab training completed successfully!")
