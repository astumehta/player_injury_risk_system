"""
Risk Model Inference & Explainability Module
AI-Assisted Player Health and Injury Risk System
- Loads trained model bundle
- Computes predicted injury probability
- Classifies Low vs High risk based on recall-tuned threshold
- Extracts Top 3 Risk Drivers per player
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = "/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/models/model.pkl"

class PlayerRiskEngine:
    def __init__(self, model_path=MODEL_PATH):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run models/train.py first.")
        self.bundle = joblib.load(model_path)
        self.scaler = self.bundle["scaler"]
        self.model = self.bundle["model"]
        self.threshold = self.bundle["threshold_15pct"]
        self.feature_cols = self.bundle["feature_cols"]
        self.feature_labels = self.bundle["feature_labels"]

    def predict(self, feature_dict):
        """
        Takes a dictionary of player metrics and returns:
        - risk_category: "High Risk" or "Low Risk"
        - risk_score: float 0.0 - 100.0%
        - acwr_baseline_flag: bool (ACWR > 1.5)
        - top_drivers: list of top 3 factors driving the risk
        """
        # Ensure all columns exist with defaults
        row = []
        for col in self.feature_cols:
            val = feature_dict.get(col, 0.0)
            row.append(float(val))
            
        df_row = pd.DataFrame([row], columns=self.feature_cols)
        scaled_row = self.scaler.transform(df_row)
        
        prob = float(self.model.predict_proba(scaled_row)[0, 1])
        is_high_risk = prob >= self.threshold
        
        # Explainability: feature contribution = scaled_value * coefficient
        coefs = self.model.coef_[0]
        contributions = []
        for col, scaled_val, c in zip(self.feature_cols, scaled_row[0], coefs):
            impact = float(scaled_val * c)
            raw_val = feature_dict.get(col, 0.0)
            contributions.append({
                "feature": col,
                "label": self.feature_labels.get(col, col),
                "raw_value": raw_val,
                "impact": impact
            })
            
        # Top 3 drivers that push the risk upward (impact > 0)
        sorted_drivers = sorted(contributions, key=lambda x: x["impact"], reverse=True)
        top_3 = sorted_drivers[:3]
        
        acwr_val = float(feature_dict.get("acwr", 1.0))
        baseline_flag = acwr_val > 1.50
        
        return {
            "risk_category": "High Risk" if is_high_risk else "Low Risk",
            "risk_score_pct": round(prob * 100.0, 1),
            "threshold_pct": round(self.threshold * 100.0, 1),
            "baseline_acwr_flag": baseline_flag,
            "top_drivers": top_3,
            "raw_features": feature_dict
        }

# Singleton instance
_engine_instance = None

def get_risk_engine():
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = PlayerRiskEngine()
    return _engine_instance
