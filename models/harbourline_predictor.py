"""
Harbourline FC Model Inference and Protocol Matcher
Supports the 3-Step Early-Warning System:
Step 1: Spot the risk (Low / High risk + top 3 drivers)
Step 2: Explain what to do (Cites Harbourline FC protocol clauses from protocol.md)
Step 3: Medical Sign-off Human Checkpoint
"""

import os
import re
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "harbourline_model.pkl")
PROTOCOL_PATH = os.path.join(BASE_DIR, "team_assets", "protocol.md")
CSV_PATH = os.path.join(BASE_DIR, "data", "harbourline_player_weeks.csv")

from models.transparent_model import calculate_logit_and_prob, TRUE_WEIGHTS

class HarbourlineRiskEngine:
    def __init__(self):
        self.protocol_clauses = self._parse_protocol()
        self.true_weights = TRUE_WEIGHTS
        
    def _parse_protocol(self):
        clauses = {}
        if not os.path.exists(PROTOCOL_PATH):
            return clauses
        with open(PROTOCOL_PATH, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Parse clauses with pattern "### [ID] [Title]"
        pattern = r"###\s+([A-Z]+-\d+\.\d+)\s+([^\n]+)\n(.*?)(?=(?:\n###|\n##|\Z))"
        matches = re.findall(pattern, content, re.DOTALL)
        for cid, title, text in matches:
            clean_text = " ".join(text.strip().split())
            clauses[cid.strip()] = {
                "id": cid.strip(),
                "title": title.strip(),
                "text": clean_text
            }
        return clauses

    def predict_risk(self, metrics):
        """
        Uses the transparent logistic regression equation from DATA_README.md.
        Returns:
        - risk_tier: "LOW RISK", "MODERATE RISK", or "HIGH RISK"
        - readiness_status: "Available to Train", "Need Some Help / Modified", "Can't Train / Benched"
        - risk_score_pct: exact probability (0% to 100%)
        - logit_z: raw log-odds score
        - top_3_reasons: plain English sports science reasons
        - math_breakdown: step-by-step term additions
        """
        math_res = calculate_logit_and_prob(metrics)
        acwr = float(metrics.get("acwr", 1.0))
        soreness = float(metrics.get("soreness", 3.0))
        sleep_h = float(metrics.get("sleep_hours", 7.5))
        sleep_debt = float(metrics.get("sleep_debt_3w", 0.0))
        wellness = float(metrics.get("wellness", 7.0))
        prior = float(metrics.get("prior_injuries", 0))
        weeks_since_return = metrics.get("weeks_since_return", None)

        reasons = []
        if acwr > 1.50:
            reasons.append((3.5, f"Acute load spike: ACWR of {acwr:.2f} is in the Red danger zone (>1.50)"))
        elif acwr > 1.30:
            reasons.append((2.0, f"Elevated load: ACWR of {acwr:.2f} is rising faster than chronic baseline (>1.30)"))
        elif acwr < 0.80:
            reasons.append((1.5, f"Under-loading detraining: ACWR of {acwr:.2f} (<0.80) leaves player deconditioned"))

        if sleep_debt >= 10.0:
            reasons.append((2.8, f"Accumulated sleep debt: {sleep_debt:.0f} hours below baseline over 3 weeks"))
        elif sleep_h < 6.0:
            reasons.append((2.5, f"Short sleep: Only {sleep_h:.1f} hours average sleep (<6.0h Red threshold)"))
        elif sleep_h < 6.5:
            reasons.append((1.8, f"Sub-optimal sleep: {sleep_h:.1f} hours average sleep (<6.5h Amber threshold)"))

        if soreness >= 8:
            reasons.append((2.6, f"Severe muscle soreness: {soreness:.0f}/10 reported (Red threshold)"))
        elif soreness >= 7:
            reasons.append((1.9, f"Elevated muscle soreness: {soreness:.0f}/10 reported (Amber threshold)"))
        elif soreness > 4:
            reasons.append((1.2, f"Residual muscle soreness: {soreness:.0f}/10 above baseline"))

        if wellness <= 3:
            reasons.append((2.2, f"Critically low wellness: {wellness:.0f}/10 indicates fatigue or distress"))
        elif wellness == 4:
            reasons.append((1.5, f"Low wellness score: {wellness:.0f}/10 (Amber warning)"))

        if prior >= 2:
            reasons.append((2.1, f"High injury history: {prior:.0f} prior soft-tissue strains in past 2 seasons"))
        elif prior == 1:
            reasons.append((1.1, f"Prior injury history: 1 previous soft-tissue strain on record"))

        if weeks_since_return in [1, 2]:
            w_str = "first" if weeks_since_return == 1 else "second"
            reasons.append((2.4, f"Recent return-to-play: Athlete in {w_str} week back from injury"))

        reasons.sort(key=lambda x: x[0], reverse=True)
        top_3 = [r[1] for r in reasons[:3]]

        default_fillers = [
            f"Workload status: ACWR is {acwr:.2f}",
            f"Sleep profile: {sleep_h:.1f} hrs/night (3-week debt: {sleep_debt:.1f}h)",
            f"Physical recovery: Soreness {soreness:.0f}/10, Wellness {wellness:.0f}/10",
            f"Medical background: {prior:.0f} prior soft-tissue strains on record"
        ]
        for filler in default_fillers:
            if len(top_3) >= 3:
                break
            if filler not in top_3:
                top_3.append(filler)
        top_3 = top_3[:3]

        return {
            "risk_tier": math_res["risk_tier"],
            "readiness_status": math_res["readiness_status"],
            "risk_score_pct": math_res["probability_pct"],
            "logit_z": math_res["logit_z"],
            "top_3_reasons": top_3,
            "math_breakdown": math_res["breakdown"],
            "raw_metrics": metrics
        }

    def generate_ai_briefing(self, player_id, risk_result):
        """
        Step 2: Reads club's own rulebook (protocol.md) and writes a short note:
        - Quotes specific clause IDs (e.g. LM-3.4, WEL-4.1)
        - Detects conflicting clauses (Conflict A: RTP-5.3 vs LM-3.4; Conflict B: LM-3.2 vs AI-6.2)
        - Strictly adheres to AI-6.4 (never diagnoses, never says 'fit to play')
        """
        m = risk_result["raw_metrics"]
        tier = risk_result["risk_tier"]
        acwr = float(m.get("acwr", 1.0))
        sleep_h = float(m.get("sleep_hours", 7.5))
        sleep_debt = float(m.get("sleep_debt_3w", 0.0))
        soreness = float(m.get("soreness", 3.0))
        wellness = float(m.get("wellness", 7.0))
        rtp_stage = m.get("rtp_stage", None)
        weeks_since_return = m.get("weeks_since_return", None)

        matched_rules = []
        is_conflicting = False
        conflict_details = ""

        # Check Load Rules (LM)
        if acwr > 1.50:
            matched_rules.append(("LM-3.4", "Red Band (ACWR > 1.50)", "Cap load at ≤1.2× chronic load, remove high-speed running and sprint blocks for 48 hours, and schedule a physio screen within 24 hours."))
        elif acwr >= 1.31:
            matched_rules.append(("LM-3.3", "Amber Band (ACWR 1.31-1.50)", "Next week's planned load must not rise by more than 10%; review plan before next high-intensity session."))
        elif acwr < 0.80:
            matched_rules.append(("LM-3.5", "Amber Band (ACWR < 0.80)", "Rebuild load gradually: increase weekly load by no more than 15% per week until back in Green band."))
        else:
            matched_rules.append(("LM-3.2", "Green Band (ACWR 0.80-1.30)", "Load is in line with player baseline. Available for full training as planned."))

        # Check Wellness Rules (WEL)
        if sleep_h < 6.0:
            matched_rules.append(("WEL-4.1", "Red Sleep (<6.0h)", "Average sleep below 6.0h triggers a mandatory wellness review with the Lead Physiotherapist before next high-intensity session."))
        elif sleep_h < 6.5:
            matched_rules.append(("WEL-4.1", "Amber Sleep (<6.5h)", "Average sleep below 6.5h: conduct sleep consultation with performance staff."))

        if sleep_debt > 10.0:
            matched_rules.append(("WEL-4.2", "Accumulated Sleep Debt (>10h)", "Sleep debt over 3 weeks exceeds 10 hours: conduct sleep-hygiene consultation."))

        if soreness >= 8:
            matched_rules.append(("WEL-4.4", "Red Soreness (≥8/10)", "High soreness: player must not train at high intensity until assessed by Lead Physiotherapist."))
        elif soreness == 7:
            matched_rules.append(("WEL-4.4", "Amber Soreness (7/10)", "Physio check required before any high-intensity session."))

        if wellness <= 3:
            matched_rules.append(("WEL-4.5", "Red Wellness (≤3/10)", "Refer to Club Doctor, as low wellness can indicate systemic illness or high distress."))
        elif wellness == 4:
            matched_rules.append(("WEL-4.5", "Amber Wellness (4/10)", "Check-in conversation with staff member required this week."))

        # Check AI Risk Tier Rule
        if tier == "HIGH RISK":
            matched_rules.append(("AI-6.2", "AI High-Risk Tier", "Lead Physiotherapist carries out physio screen within 24 hours; player does modified training (no sprinting) until screened."))
        elif tier == "MODERATE RISK":
            matched_rules.append(("AI-6.2", "AI Moderate-Risk Tier", "Elevated fatigue indicators detected: review training plan before high-intensity sessions."))
        else:
            matched_rules.append(("AI-6.3", "AI Low-Risk Tier", "Low risk is not medical clearance; standard protocols still apply."))

        # Check Multiple Amber combination rule (WEL-4.6)
        # Count amber signals
        amber_count = 0
        if (acwr >= 1.31 and acwr <= 1.50) or acwr < 0.80: amber_count += 1
        if sleep_h >= 6.0 and sleep_h < 6.5: amber_count += 1
        if sleep_debt > 10.0: amber_count += 1
        if soreness == 7: amber_count += 1
        if wellness == 4: amber_count += 1
        if tier == "HIGH RISK": amber_count += 1
        
        if amber_count >= 2:
            matched_rules.append(("WEL-4.6", "Combining Warning Signs", "Two or more Amber signals present: treated as Red. Lead Physiotherapist screens within 24 hours."))

        # Check Conflict A: Return-to-play Stage 5 vs Load Spike (DATA_README.md Section 6)
        if weeks_since_return == 1 and acwr > 1.50:
            is_conflicting = True
            conflict_details = (
                "⚠️ **PROTOCOL CONFLICT (Conflict A: RTP vs Load Spike):**\n"
                "- **Rule RTP-5.3** states a Stage 5 player may return to full, unrestricted training including sprints.\n"
                "- **Rule LM-3.4** states ACWR > 1.50 requires removing sprints for 48h and capping load.\n"
                "- *(Note: Rule MON-2.3 explains ACWR is inflated due to low chronic baseline during rehab).*\n"
                "> **Action under Rule GOV-1.4:** Apply the more conservative instruction (no sprints) and escalate to the Medical Lead today."
            )

        # Check Conflict B: Green ACWR vs Model High (DATA_README.md Section 6)
        elif tier == "HIGH RISK" and (acwr >= 0.80 and acwr <= 1.30):
            is_conflicting = True
            conflict_details = (
                "⚠️ **PROTOCOL CONFLICT (Conflict B: Green ACWR vs Model High):**\n"
                "- **Rule LM-3.2** states Green ACWR allows full training with no restrictions.\n"
                "- **Rule AI-6.2** states an AI High-risk flag requires modified training until a physio screen.\n"
                "> **Action under Rule GOV-1.4:** Apply the more conservative instruction (modified training) and escalate to the Medical Lead today."
            )

        # Construct concise note
        lines = []
        if is_conflicting:
            lines.append(conflict_details + "\n")
            lines.append("### Applicable Club Protocol Guidance:")
        else:
            lines.append(f"### Medical & Load Guidance for {player_id}:")

        for r_id, r_name, r_action in matched_rules:
            lines.append(f"- **Under rule {r_id} ({r_name}):** {r_action}")

        lines.append("\n> *Compliance Notice (Rule AI-6.4 & GOV-1.5): This briefing does not provide medical clearance or make benching decisions. A human club doctor must sign off on availability below.*")

        return {
            "briefing_text": "\n".join(lines),
            "matched_rules": matched_rules,
            "is_conflicting": is_conflicting,
            "recommended_action": "MODIFIED_TRAINING" if tier == "HIGH RISK" else "FULL_TRAINING"
        }

_engine = None
def get_harbourline_engine():
    global _engine
    if _engine is None:
        _engine = HarbourlineRiskEngine()
    return _engine
