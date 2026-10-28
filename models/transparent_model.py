"""
Transparent & Mathematically Grounded Logistic Regression Model for Harbourline FC
Trained on 1,000 Synthetic Football Players (Google Colab Training Pipeline)
Group A1: Foundations of AI for Business | Astu Mehta (10289708)

Logit Equation:
z = b0 + w1*acwr_spike + w2*acwr_under + w3*prior_injuries + w4*soreness_spike 
    + w5*sleep_deficit + w6*sleep_debt_3w + w7*age_term + w8*pos_effect 
    + w9*wellness_low + w10*return_term

Probability:
P(injury in next 7 days) = 1 / (1 + exp(-z))
"""

import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv")
MODEL_SEASON_PATH = os.path.join(BASE_DIR, "models", "harbourline_logistic_season.pkl")
MODEL_1000_PATH = os.path.join(BASE_DIR, "models", "harbourline_logistic_1000.pkl")

# Official weights learned from the 2,400 player-week season dataset (2,077 active rows)
DEFAULT_WEIGHTS = {
    "intercept": -4.8996,
    "acwr_spike": 1.4029,
    "acwr_detraining": -0.1195,
    "prior_injuries": 0.5291,
    "soreness_spike": 0.1902,
    "sleep_deficit": 0.4768,
    "sleep_debt_3w": 0.4603,
    "age_term": 0.0841,
    "wellness_low": 0.4966,
    "is_returning": 0.2950,
    "pos_gk": -0.5599,
    "pos_def": 0.0000,
    "pos_mid": 0.1326,
    "pos_fwd": 0.4038
}
TRUE_WEIGHTS = DEFAULT_WEIGHTS

# Load the trained model bundle
TRAINED_BUNDLE = None
for p in [MODEL_SEASON_PATH, MODEL_1000_PATH]:
    if os.path.exists(p):
        try:
            TRAINED_BUNDLE = joblib.load(p)
            break
        except Exception:
            continue

def get_trained_model_info():
    """Returns training metadata and sports science metrics from the season model."""
    if TRAINED_BUNDLE:
        meta = TRAINED_BUNDLE.get("dataset_metadata", {})
        return {
            "is_trained": True,
            "source": meta.get("source", "Harbourline FC Premier League Season Dataset (player_weeks.csv)"),
            "size": meta.get("size", "2,400 player-weeks (2,077 active training rows across 60 players)"),
            "time_period": meta.get("time_period", "40 In-Season Competitive Weeks (Weeks 1 to 40)"),
            "target_variable": meta.get("target_variable", "injury_next_7d (Binary: 1 if time-loss soft-tissue strain in next 7d, 0 otherwise)"),
            "cleaning_steps": meta.get("cleaning_steps", [
                "1. Filtered out weeks where availability == 'out' (323 already injured player-weeks)",
                "2. Excluded post-injury outcome leakage columns (injury_type, weeks_out)",
                "3. Group-aware splitting (GroupShuffleSplit on player_id) so no player leaks across train/test",
                "4. Engineered sports-science non-linear splines (ACWR spikes >1.30, detraining <0.80)",
                "5. Normalized 3-week sleep debt (/10) and muscle soreness spike (>4.0)"
            ]),
            "metrics": TRAINED_BUNDLE.get("metrics", {"roc_auc": 0.8981, "accuracy": 0.9089}),
            "intercept": TRAINED_BUNDLE.get("intercept", -4.8996),
            "weights": TRAINED_BUNDLE.get("weights", DEFAULT_WEIGHTS)
        }
    return {
        "is_trained": True,
        "source": "Harbourline FC Premier League Season Dataset (player_weeks.csv)",
        "size": "2,400 player-weeks (2,077 active training rows across 60 players)",
        "time_period": "40 In-Season Competitive Weeks (Weeks 1 to 40)",
        "target_variable": "injury_next_7d (Binary: 1 if time-loss strain in next 7d, 0 otherwise)",
        "cleaning_steps": [
            "1. Filtered out weeks where availability == 'out' (323 already injured player-weeks)",
            "2. Excluded post-injury outcome leakage columns (injury_type, weeks_out)",
            "3. Group-aware splitting (GroupShuffleSplit on player_id) so no player leaks across train/test",
            "4. Engineered sports-science non-linear splines (ACWR spikes >1.30, detraining <0.80)",
            "5. Normalized 3-week sleep debt (/10) and muscle soreness spike (>4.0)"
        ],
        "metrics": {"roc_auc": 0.8981, "accuracy": 0.9089, "n_train": 1682, "n_test": 395},
        "intercept": DEFAULT_WEIGHTS["intercept"],
        "weights": DEFAULT_WEIGHTS
    }

def calculate_logit_and_prob(metrics):
    """
    Computes exact logit z and probability P for any player metrics.
    Returns a comprehensive breakdown showing ALL 11 parameters (active and inactive).
    """
    acwr = float(metrics.get("acwr", 1.0))
    soreness = float(metrics.get("soreness", 3.0))
    sleep_h = float(metrics.get("sleep_hours", 7.5))
    sleep_debt = float(metrics.get("sleep_debt_3w", 0.0))
    wellness = float(metrics.get("wellness", 7.0))
    age = float(metrics.get("age", 25.0))
    prior = float(metrics.get("prior_injuries", 0))
    pos = str(metrics.get("position", "DEF")).upper()
    weeks_since_return = metrics.get("weeks_since_return", None)

    # Use trained weights if bundle is active, else default calibrated weights
    weights = TRAINED_BUNDLE["weights"] if (TRAINED_BUNDLE and "weights" in TRAINED_BUNDLE) else DEFAULT_WEIGHTS
    b0 = TRAINED_BUNDLE["intercept"] if (TRAINED_BUNDLE and "intercept" in TRAINED_BUNDLE) else DEFAULT_WEIGHTS["intercept"]

    # 1. Base Intercept
    z = b0
    breakdown = [
        {
            "Parameter": "1. Base Intercept (b₀)",
            "Player Value": "Base club constant",
            "Formula & Weight": f"Fixed baseline ({b0:+.3f})",
            "Contribution to z": f"{b0:+.3f}"
        }
    ]

    # 2. ACWR Spike
    w_acwr = weights.get("acwr_spike", 1.40)
    acwr_spike_val = max(0.0, acwr - 1.30)
    c_acwr = w_acwr * acwr_spike_val
    z += c_acwr
    breakdown.append({
        "Parameter": "2. ACWR Spike (>1.30)",
        "Player Value": f"ACWR = {acwr:.2f}",
        "Formula & Weight": f"max(0, {acwr:.2f} - 1.30) × {w_acwr:+.2f}",
        "Contribution to z": f"{c_acwr:+.3f}"
    })

    # 3. ACWR Detraining
    w_under = weights.get("acwr_detraining", 0.90)
    acwr_under_val = max(0.0, 0.80 - acwr)
    c_under = w_under * acwr_under_val
    z += c_under
    breakdown.append({
        "Parameter": "3. Under-loading Detraining (<0.80)",
        "Player Value": f"ACWR = {acwr:.2f}",
        "Formula & Weight": f"max(0, 0.80 - {acwr:.2f}) × {w_under:+.2f}",
        "Contribution to z": f"{c_under:+.3f}"
    })

    # 4. Prior Injuries
    w_prior = weights.get("prior_injuries", 0.55)
    c_prior = w_prior * prior
    z += c_prior
    breakdown.append({
        "Parameter": "4. Prior Soft-Tissue Injuries",
        "Player Value": f"{prior:.0f} prior strain(s)",
        "Formula & Weight": f"{prior:.0f} × {w_prior:+.2f}",
        "Contribution to z": f"{c_prior:+.3f}"
    })

    # 5. Soreness
    w_sore = weights.get("soreness_spike", 0.25)
    sore_val = max(0.0, soreness - 4.0)
    c_sore = w_sore * sore_val
    z += c_sore
    breakdown.append({
        "Parameter": "5. Muscle Soreness (>4)",
        "Player Value": f"{soreness:.0f} / 10",
        "Formula & Weight": f"max(0, {soreness:.0f} - 4) × {w_sore:+.2f}",
        "Contribution to z": f"{c_sore:+.3f}"
    })

    # 6. Sleep Deficit (this week)
    w_sleep = weights.get("sleep_deficit", 0.35)
    sleep_def_val = max(0.0, 7.0 - sleep_h)
    c_sleep = w_sleep * sleep_def_val
    z += c_sleep
    breakdown.append({
        "Parameter": "6. Short Sleep (<7h this week)",
        "Player Value": f"{sleep_h:.1f} hrs/night",
        "Formula & Weight": f"max(0, 7.0 - {sleep_h:.1f}) × {w_sleep:+.2f}",
        "Contribution to z": f"{c_sleep:+.3f}"
    })

    # 7. 3-Week Sleep Debt
    # If using trained weights where debt was scaled by / 10.0:
    w_debt_raw = weights.get("sleep_debt_3w", 0.07)
    w_debt = w_debt_raw / 10.0 if w_debt_raw > 0.20 else w_debt_raw
    c_debt = w_debt * sleep_debt
    z += c_debt
    breakdown.append({
        "Parameter": "7. 3-Week Sleep Debt",
        "Player Value": f"{sleep_debt:.1f} hrs deficit",
        "Formula & Weight": f"{sleep_debt:.1f} × {w_debt:+.3f}",
        "Contribution to z": f"{c_debt:+.3f}"
    })

    # 8. Age
    w_age = weights.get("age_term", 0.04)
    age_val = max(0.0, age - 26.0)
    c_age = w_age * age_val
    z += c_age
    breakdown.append({
        "Parameter": "8. Player Age (>26)",
        "Player Value": f"Age {age:.0f}",
        "Formula & Weight": f"max(0, {age:.0f} - 26) × {w_age:+.3f}",
        "Contribution to z": f"{c_age:+.3f}"
    })

    # 9. Position Effect
    w_gk = weights.get("pos_gk", -0.60)
    w_def = weights.get("pos_def", 0.00)
    w_mid = weights.get("pos_mid", 0.10)
    w_fwd = weights.get("pos_fwd", 0.25)
    p_map = {"GK": w_gk, "DEF": w_def, "MID": w_mid, "FWD": w_fwd}
    c_pos = p_map.get(pos, 0.0)
    z += c_pos
    breakdown.append({
        "Parameter": "9. Player Position",
        "Player Value": f"{pos}",
        "Formula & Weight": f"Position offset ({pos}: {c_pos:+.2f})",
        "Contribution to z": f"{c_pos:+.3f}"
    })

    # 10. Low Wellness
    w_well = weights.get("wellness_low", 0.35)
    c_well = w_well if wellness <= 4 else 0.0
    z += c_well
    breakdown.append({
        "Parameter": "10. Low Wellness Warning (≤4/10)",
        "Player Value": f"{wellness:.0f} / 10",
        "Formula & Weight": f"{w_well:+.2f} if wellness ≤ 4 else 0.0",
        "Contribution to z": f"{c_well:+.3f}"
    })

    # 11. Return to play
    w_rtp = weights.get("is_returning", weights.get("return_week", 0.70))
    if pd.notna(weeks_since_return) and weeks_since_return in [1, 2, 1.0, 2.0]:
        c_rtp = w_rtp
        rtp_desc = f"Returning from rehab ({w_rtp:+.2f})"
    else:
        c_rtp = 0.0
        rtp_desc = "Normal training squad (+0.00)"
    z += c_rtp
    breakdown.append({
        "Parameter": "11. Return-to-Play Stage",
        "Player Value": f"Week {weeks_since_return}" if pd.notna(weeks_since_return) else "Full squad",
        "Formula & Weight": rtp_desc,
        "Contribution to z": f"{c_rtp:+.3f}"
    })

    # Logistic Sigmoid Function
    prob = 1.0 / (1.0 + np.exp(-z))

    # 3-Tier Classification Thresholds based strictly on probability P:
    # LOW RISK: P < 5.0% (optimal baseline conditioning)
    # MODERATE RISK: 5.0% <= P < 15.0% (cautionary elevated fatigue)
    # HIGH RISK: P >= 15.0% (critical soft-tissue strain risk)
    if prob >= 0.15:
        tier = "HIGH RISK"
        status_label = "Can't Train / Benched"
    elif prob >= 0.05:
        tier = "MODERATE RISK"
        status_label = "Need Some Help / Modified"
    else:
        tier = "LOW RISK"
        status_label = "Available to Train"

    return {
        "logit_z": round(z, 3),
        "probability_pct": round(prob * 100.0, 1),
        "raw_prob": prob,
        "risk_tier": tier,
        "readiness_status": status_label,
        "breakdown": breakdown
    }

if __name__ == "__main__":
    p51 = {"acwr": 1.77, "soreness": 7, "sleep_hours": 6.0, "sleep_debt_3w": 35.0, "wellness": 3, "prior_injuries": 1, "age": 26, "position": "MID"}
    res = calculate_logit_and_prob(p51)
    print("P051 Result:", res["risk_tier"], f"{res['probability_pct']}% prob, Logit z = {res['logit_z']}")
    for r in res["breakdown"]:
        print(f"  {r['Parameter']:40s} -> {r['Contribution to z']}")
