"""
Model Training and Evaluation Pipeline
AI-Assisted Player Health and Injury Risk System
Matches Midterm Report specs:
- Evaluates Baseline rule (ACWR > 1.5) vs Logistic Regression and Gradient Boosting
- Prioritizes Recall to minimize costly missed soft-tissue injuries
- Top 3 risk drivers explanation based on standardized coefficients
- Error-cost analysis comparing financial impact of missed vs false alarm
"""

import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_score, recall_score, roc_auc_score, confusion_matrix

def train_and_evaluate():
    data_path = "/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/data/synthetic_season.csv"
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing {data_path}")
        
    df = pd.read_csv(data_path)
    
    # 60 players total: 42 train players (1680 weeks), 18 test players (720 weeks)
    unique_players = df["player_id"].unique()
    train_player_ids = unique_players[:42]
    test_player_ids = unique_players[42:]
    
    feature_cols = [
        "acwr",
        "acute_load",
        "chronic_load",
        "sleep_hours",
        "soreness",
        "wellness_score",
        "prior_injuries",
        "age",
        "match_minutes",
        "load_trend_3w",
        "sleep_debt_3w",
        "avg_soreness_3w"
    ]
    
    feature_labels = {
        "acwr": "Acute:Chronic Workload Ratio (ACWR)",
        "acute_load": "Acute Workload (AU)",
        "chronic_load": "Chronic Baseline Load (AU)",
        "sleep_hours": "Sleep Duration (Hours)",
        "soreness": "Muscle Soreness Rating",
        "wellness_score": "Composite Wellness Score",
        "prior_injuries": "Prior Soft-Tissue Injuries",
        "age": "Player Age",
        "match_minutes": "Match Minutes Played",
        "load_trend_3w": "3-Week Load Trend (%)",
        "sleep_debt_3w": "3-Week Cumulative Sleep Debt (Hours)",
        "avg_soreness_3w": "3-Week Average Soreness"
    }
    
    train_df = df[df["player_id"].isin(train_player_ids)]
    test_df = df[df["player_id"].isin(test_player_ids)]
    
    X_train = train_df[feature_cols]
    y_train = train_df["injury_next_7_days"]
    X_test = test_df[feature_cols]
    y_test = test_df["injury_next_7_days"]
    
    total_test_injuries = int(y_test.sum())
    
    # Cost parameters (Midterm report: missed injury saves starter 3 to 6 weeks, wages lakhs per week)
    # Missed injury: ₹600,000 (wages + points lost); False alarm: ₹5,000 (extra 30min physio screening)
    COST_FN = 600000 
    COST_FP = 5000
    
    # 1. Baseline: ACWR > 1.5
    y_pred_baseline = (test_df["acwr"] > 1.5).astype(int)
    baseline_flags = int(y_pred_baseline.sum())
    baseline_tp = int(((y_pred_baseline == 1) & (y_test == 1)).sum())
    baseline_missed = int(total_test_injuries - baseline_tp)
    baseline_prec = float(precision_score(y_test, y_pred_baseline, zero_division=0))
    baseline_rec = float(recall_score(y_test, y_pred_baseline, zero_division=0))
    baseline_auc = float(roc_auc_score(y_test, test_df["acwr"]))
    baseline_cost = (baseline_missed * COST_FN) + ((baseline_flags - baseline_tp) * COST_FP)
    
    # 2. Logistic Regression Pipeline
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    log_reg = LogisticRegression(class_weight="balanced", random_state=42, solver="liblinear", C=0.5)
    log_reg.fit(X_train_scaled, y_train)
    
    X_test_scaled = scaler.transform(X_test)
    y_prob_lr = log_reg.predict_proba(X_test_scaled)[:, 1]
    lr_auc = float(roc_auc_score(y_test, y_prob_lr))
    
    # Top 15% cutoff (flags ~108 player-weeks out of 720, giving ~4.6 players per squad/week)
    threshold_15pct = float(np.percentile(y_prob_lr, 85))
    y_pred_lr_15 = (y_prob_lr >= threshold_15pct).astype(int)
    lr15_flags = int(y_pred_lr_15.sum())
    lr15_tp = int(((y_pred_lr_15 == 1) & (y_test == 1)).sum())
    lr15_missed = int(total_test_injuries - lr15_tp)
    lr15_prec = float(precision_score(y_test, y_pred_lr_15, zero_division=0))
    lr15_rec = float(recall_score(y_test, y_pred_lr_15, zero_division=0))
    lr15_cost = (lr15_missed * COST_FN) + ((lr15_flags - lr15_tp) * COST_FP)
    
    # Top 60 flags cutoff (matching baseline flag volume)
    threshold_60 = float(np.sort(y_prob_lr)[-60])
    y_pred_lr_60 = (y_prob_lr >= threshold_60).astype(int)
    lr60_flags = int(y_pred_lr_60.sum())
    lr60_tp = int(((y_pred_lr_60 == 1) & (y_test == 1)).sum())
    lr60_missed = int(total_test_injuries - lr60_tp)
    lr60_prec = float(precision_score(y_test, y_pred_lr_60, zero_division=0))
    lr60_rec = float(recall_score(y_test, y_pred_lr_60, zero_division=0))
    lr60_cost = (lr60_missed * COST_FN) + ((lr60_flags - lr60_tp) * COST_FP)
    
    # 3. Gradient Boosting Classifier (for comparison)
    gb = GradientBoostingClassifier(n_estimators=80, max_depth=3, random_state=42)
    gb.fit(X_train, y_train)
    y_prob_gb = gb.predict_proba(X_test)[:, 1]
    gb_auc = float(roc_auc_score(y_test, y_prob_gb))
    threshold_gb15 = float(np.percentile(y_prob_gb, 85))
    y_pred_gb_15 = (y_prob_gb >= threshold_gb15).astype(int)
    gb_flags = int(y_pred_gb_15.sum())
    gb_tp = int(((y_pred_gb_15 == 1) & (y_test == 1)).sum())
    gb_missed = int(total_test_injuries - gb_tp)
    gb_prec = float(precision_score(y_test, y_pred_gb_15, zero_division=0))
    gb_rec = float(recall_score(y_test, y_pred_gb_15, zero_division=0))
    gb_cost = (gb_missed * COST_FN) + ((gb_flags - gb_tp) * COST_FP)
    
    # Extract feature coefficients for driver attribution
    coefs = log_reg.coef_[0]
    feature_importance = [
        {
            "feature": col,
            "label": feature_labels[col],
            "coefficient": round(float(c), 4),
            "abs_impact": round(float(abs(c)), 4)
        }
        for col, c in zip(feature_cols, coefs)
    ]
    feature_importance = sorted(feature_importance, key=lambda x: x["abs_impact"], reverse=True)
    
    metrics = {
        "test_size_weeks": len(test_df),
        "test_players": len(test_player_ids),
        "total_test_injuries": total_test_injuries,
        "models": {
            "baseline": {
                "name": "Baseline: ACWR > 1.5",
                "precision": round(baseline_prec, 2),
                "recall": round(baseline_rec, 2),
                "flags": baseline_flags,
                "missed": baseline_missed,
                "auc": round(baseline_auc, 2),
                "estimated_financial_loss_inr": baseline_cost
            },
            "logistic_regression_top_15pct": {
                "name": "Logistic Regression (Top 15% Recall Tuned)",
                "precision": round(lr15_prec, 2),
                "recall": round(lr15_rec, 2),
                "flags": lr15_flags,
                "missed": lr15_missed,
                "auc": round(lr_auc, 2),
                "threshold": round(threshold_15pct, 4),
                "estimated_financial_loss_inr": lr15_cost
            },
            "logistic_regression_top_60": {
                "name": "Logistic Regression (Top 60 Flags Fixed)",
                "precision": round(lr60_prec, 2),
                "recall": round(lr60_rec, 2),
                "flags": lr60_flags,
                "missed": lr60_missed,
                "auc": round(lr_auc, 2),
                "threshold": round(threshold_60, 4),
                "estimated_financial_loss_inr": lr60_cost
            },
            "gradient_boosting": {
                "name": "Gradient Boosting (Top 15%)",
                "precision": round(gb_prec, 2),
                "recall": round(gb_rec, 2),
                "flags": gb_flags,
                "missed": gb_missed,
                "auc": round(gb_auc, 2),
                "estimated_financial_loss_inr": gb_cost
            }
        },
        "feature_importance": feature_importance,
        "top_drivers": [f["label"] for f in feature_importance[:4]],
        "cost_assumptions": {
            "missed_injury_cost_inr": COST_FN,
            "false_alarm_physio_cost_inr": COST_FP
        }
    }
    
    # Save artifacts
    os.makedirs("/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/models", exist_ok=True)
    
    # Save scikit-learn pipeline
    model_bundle = {
        "scaler": scaler,
        "model": log_reg,
        "threshold_15pct": threshold_15pct,
        "feature_cols": feature_cols,
        "feature_labels": feature_labels
    }
    joblib.dump(model_bundle, "/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/models/model.pkl")
    
    with open("/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("Model training complete.")
    print("Evaluation Summary:")
    for k, v in metrics["models"].items():
        print(f"- {v['name']}: Prec={v['precision']}, Rec={v['recall']}, AUC={v['auc']}, Flags={v['flags']}, Missed={v['missed']}, Est Loss=₹{v['estimated_financial_loss_inr']:,}")
    print("\nTop Risk Drivers:")
    for d in metrics["feature_importance"][:4]:
        print(f"- {d['label']} (coef={d['coefficient']})")
        
    return metrics

if __name__ == "__main__":
    train_and_evaluate()
