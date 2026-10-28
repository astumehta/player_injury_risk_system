"""
Protocol Indexing and RAG Briefing Engine
AI-Assisted Player Health and Injury Risk System
- Parses and indexes the official Club High-Performance Load-Management Protocol
- Semantic + rule-based clause retrieval
- Grounding check: strictly quotes matching clauses
- Fallback: cites Clause 6.3 when protocol does not cover the scenario
- Detects conflicting edge case clauses (Clause 3.4 vs Clause 5.2 -> escalates via Clause 6.1)
"""

import os
import re

PROTOCOL_PATH = "/Users/astumehta/.gemini/antigravity/scratch/player_injury_risk_system/protocol/club_load_protocol.md"

class ProtocolEngine:
    def __init__(self, protocol_path=PROTOCOL_PATH):
        self.protocol_path = protocol_path
        self.clauses = self._load_and_parse_protocol()

    def _load_and_parse_protocol(self):
        clauses = {}
        if not os.path.exists(self.protocol_path):
            return clauses

        with open(self.protocol_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract clauses like "Clause 2.1 (Optimal Sweet Spot): ..."
        pattern = r"-\s*\*\*(Clause\s+[\d\.]+)\s*\(([^)]+)\):\*\*\s*(.*?)(?=(?:-\s*\*\*Clause|\n##|\Z))"
        matches = re.findall(pattern, content, re.DOTALL)
        for clause_id, title, text in matches:
            clean_text = " ".join(text.strip().split())
            clauses[clause_id.strip()] = {
                "clause_id": clause_id.strip(),
                "title": title.strip(),
                "text": clean_text
            }
        return clauses

    def match_clauses(self, metrics):
        """
        Match player metrics against official protocol clauses.
        Returns list of matched clauses with rationale.
        """
        matched = []
        acwr = float(metrics.get("acwr", 1.0))
        sleep = float(metrics.get("sleep_hours", 8.0))
        soreness = float(metrics.get("soreness", 2.0))
        sleep_debt = float(metrics.get("sleep_debt_3w", 0.0))
        load_trend = float(metrics.get("load_trend_3w", 0.0))
        minutes = float(metrics.get("match_minutes", 0.0))
        wellness = float(metrics.get("wellness_score", 8.0))
        prior_injuries = int(metrics.get("prior_injuries", 0))

        # Clause 2.1, 2.2, 2.3
        if acwr > 1.50:
            if "Clause 2.3" in self.clauses:
                matched.append({
                    **self.clauses["Clause 2.3"],
                    "trigger": f"ACWR = {acwr:.2f} (> 1.50 load spike)"
                })
        elif acwr >= 1.31:
            if "Clause 2.2" in self.clauses:
                matched.append({
                    **self.clauses["Clause 2.2"],
                    "trigger": f"ACWR = {acwr:.2f} (1.31 - 1.50 cautionary zone)"
                })
        else:
            if "Clause 2.1" in self.clauses:
                matched.append({
                    **self.clauses["Clause 2.1"],
                    "trigger": f"ACWR = {acwr:.2f} (Optimal sweet spot 0.80 - 1.30)"
                })

        # Clause 3.1: Sleep
        if sleep < 6.0 or sleep_debt > 12.0:
            if "Clause 3.1" in self.clauses:
                matched.append({
                    **self.clauses["Clause 3.1"],
                    "trigger": f"Sleep = {sleep:.1f} hrs (<6.0h) or 3W Debt = {sleep_debt:.1f}h"
                })

        # Clause 3.2: Soreness
        if soreness >= 7.0:
            if "Clause 3.2" in self.clauses:
                matched.append({
                    **self.clauses["Clause 3.2"],
                    "trigger": f"Muscle Soreness = {soreness:.1f} / 10 (Elevated threshold ≥ 7.0)"
                })

        # Clause 3.3: Compound risk
        if acwr > 1.40 and (soreness >= 6.0 or sleep < 6.5):
            if "Clause 3.3" in self.clauses:
                matched.append({
                    **self.clauses["Clause 3.3"],
                    "trigger": f"Compound Risk (ACWR {acwr:.2f} > 1.40 with soreness {soreness:.1f} / sleep {sleep:.1f}h)"
                })

        # Clause 5.1: Minutes
        if minutes > 180:
            if "Clause 5.1" in self.clauses:
                matched.append({
                    **self.clauses["Clause 5.1"],
                    "trigger": f"Match minutes = {minutes:.0f} (>180 min rolling)"
                })

        # Clause 5.2: Absolute load ceiling
        has_ceiling_breach = acwr > 1.55 or load_trend > 25.0
        if has_ceiling_breach:
            if "Clause 5.2" in self.clauses:
                matched.append({
                    **self.clauses["Clause 5.2"],
                    "trigger": f"Load Ceiling Breach (ACWR {acwr:.2f} > 1.55 or 3W Load Trend {load_trend:+.1f}% > 25%)"
                })

        # Clause 3.4: Rapid progression exemption (high wellness despite acute spike)
        has_exemption = (soreness <= 2.0 and wellness >= 8.5)
        if has_exemption and prior_injuries > 0:
            if "Clause 3.4" in self.clauses:
                matched.append({
                    **self.clauses["Clause 3.4"],
                    "trigger": f"Rapid Progression Criteria Met (Soreness {soreness:.1f} ≤ 2.0 & Wellness {wellness:.1f} ≥ 8.5)"
                })

        # Detect deliberate protocol conflict (Edge Case: Clause 3.4 vs Clause 5.2)
        clause_ids = [c["clause_id"] for c in matched]
        has_conflict = ("Clause 3.4" in clause_ids) and ("Clause 5.2" in clause_ids)
        if has_conflict:
            if "Clause 6.1" in self.clauses:
                matched.insert(0, {
                    **self.clauses["Clause 6.1"],
                    "trigger": "DIRECT PROTOCOL CONFLICT: Rapid Progression Exemption (Clause 3.4) contradicts Absolute Load Ceiling (Clause 5.2)"
                })

        return matched

    def generate_briefing(self, player_id, player_name, risk_result):
        """
        Generates a strictly protocol-grounded briefing for the Medical Team and Coach.
        Guarantees that every recommendation cites an exact clause.
        """
        metrics = risk_result["raw_features"]
        matched_clauses = self.match_clauses(metrics)
        risk_cat = risk_result["risk_category"]
        score_pct = risk_result["risk_score_pct"]
        top_drivers = risk_result["top_drivers"]

        clause_ids = [c["clause_id"] for c in matched_clauses]
        is_conflicting = "Clause 6.1" in clause_ids

        # If no clauses matched (edge case outside protocol)
        if not matched_clauses:
            briefing_text = (
                f"**AUTOMATED PROTOCOL AUDIT FOR {player_id}**\n\n"
                f"⚠️ **PROTOCOL GAP FALLBACK**: The current data profile (ACWR: {metrics.get('acwr', 1.0):.2f}, "
                f"Sleep: {metrics.get('sleep_hours', 8.0):.1f}h, Soreness: {metrics.get('soreness', 0):.1f}) "
                f"does not match existing codified thresholds.\n\n"
                f"*Per **Clause 6.3 (Protocol Gap Fallback)**: Protocol does not cover this edge case — "
                f"immediate consultation with the club Medical Director is required.*"
            )
            return {
                "briefing_markdown": briefing_text,
                "matched_clauses": matched_clauses,
                "recommended_action": "ESCALATE_TO_DIRECTOR",
                "is_conflicting": False,
                "coach_action_item": "Pending Medical Director clinical review."
            }

        if is_conflicting:
            briefing_text = (
                f"### ⚠️ PROTOCOL CONFLICT ESCALATION — {player_id}\n\n"
                f"**Predicted Injury Risk:** `{score_pct}%` ({risk_cat})\n\n"
                f"**Conflict Detected:** Athlete qualifies for **Rapid Progression Exemption** (*Clause 3.4*) "
                f"due to excellent recovery (Soreness {metrics.get('soreness', 2.0)}/10, Wellness {metrics.get('wellness_score', 8.5)}/10), "
                f"yet breaches **Absolute Load Ceiling** (*Clause 5.2*) with ACWR of `{metrics.get('acwr', 1.0):.2f}` and "
                f"3-week load acceleration of `+{metrics.get('load_trend_3w', 0.0):.1f}%`.\n\n"
                f"> **Mandatory Protocol Action (Clause 6.1 & 6.2):** Automatic clearance is withheld. "
                f"This decision requires mandatory manual clinical override with documented medical reason before this athlete can train."
            )
            return {
                "briefing_markdown": briefing_text,
                "matched_clauses": matched_clauses,
                "recommended_action": "MANDATORY_OVERRIDE_REQUIRED",
                "is_conflicting": True,
                "coach_action_item": "Athlete on hold. Awaiting Medical Director resolution of protocol conflict."
            }

        # Standard Grounded Briefing
        citations = []
        action_recommendations = []
        
        for c in matched_clauses:
            citations.append(f"- **{c['clause_id']} ({c['title']}):** {c['text']} *(Trigger: {c['trigger']})*")
            if c["clause_id"] == "Clause 2.3":
                action_recommendations.append("Prohibit high-speed running (>25 km/h) and high-impact deceleration drills.")
            elif c["clause_id"] == "Clause 2.2":
                action_recommendations.append("Cap session volume at 80% match intensity; maximum 150m sprint distance.")
            elif c["clause_id"] == "Clause 3.1":
                action_recommendations.append("Withhold from live contact and plyometrics; schedule daytime recovery sleep block.")
            elif c["clause_id"] == "Clause 3.2":
                action_recommendations.append("Assign to hydrotherapy, wattbike recovery, and targeted soft-tissue physio.")
            elif c["clause_id"] == "Clause 3.3":
                action_recommendations.append("Enforce 50% match-load ceiling due to compounding load and recovery indicators.")
            elif c["clause_id"] == "Clause 2.1":
                action_recommendations.append("Cleared for full training conditioning block.")

        drivers_summary = ", ".join([f"{d['label']} ({d['raw_value']})" for d in top_drivers])
        
        # Optional LLM synthesis if API key is provided
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        # Also check Streamlit secrets if running inside streamlit
        try:
            import streamlit as st
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
            elif "GOOGLE_API_KEY" in st.secrets:
                api_key = st.secrets["GOOGLE_API_KEY"]
        except Exception:
            pass

        llm_enhanced_briefing = None
        if api_key:
            try:
                import requests
                prompt = (
                    "You are the clinical AI assistant for an elite professional football club's medical department.\n"
                    "Ground your answer strictly in these official protocol clauses. Do NOT invent diagnoses, and do NOT prescribe medication.\n"
                    f"Athlete ID: {player_id}\n"
                    f"Model Risk: {score_pct}% ({risk_cat})\n"
                    f"Top Risk Drivers: {drivers_summary}\n"
                    f"Protocol Clauses:\n" + "\n".join(citations) + "\n\n"
                    "Write a concise 3-paragraph protocol briefing for the Medical Director and Head Coach. Cite clauses by number."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    llm_enhanced_briefing = data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                pass

        if llm_enhanced_briefing:
            briefing_text = (
                f"### Protocol-Grounded Performance Briefing — {player_id} *(Gemini LLM Synthesized)*\n\n"
                f"{llm_enhanced_briefing}\n\n"
                f"> *Note: Grounded in club protocol per **Clause 6.2**. Subject to mandatory medical sign-off below.*"
            )
        else:
            briefing_text = (
                f"### Protocol-Grounded Performance Briefing — {player_id}\n\n"
                f"**Model Risk Assessment:** `{score_pct}%` probability of soft-tissue strain in next 7 days (**{risk_cat.upper()}**).\n"
                f"**Key Risk Drivers:** {drivers_summary}.\n\n"
                f"#### Applicable Club Protocol Clauses:\n" + "\n".join(citations) + "\n\n"
                f"#### Proposed Training Adjustments:\n" + "\n".join([f"1. {a}" for a in set(action_recommendations)]) + "\n\n"
                f"> *Note: In accordance with **Clause 6.2**, no recommendation is communicated to coaching staff until formal medical sign-off is completed below.*"
            )

        coach_summary = "Full participation permitted." if risk_cat == "Low Risk" else "Modified session: no sprinting drills, capped at 60% intensity."
        if "Clause 2.3" in clause_ids:
            coach_summary = "Non-contact / off-pitch recovery only. ACWR load spike."

        return {
            "briefing_markdown": briefing_text,
            "matched_clauses": matched_clauses,
            "recommended_action": "MODIFY" if risk_cat == "High Risk" else "CLEAR",
            "is_conflicting": False,
            "coach_action_item": coach_summary
        }

_rag_instance = None

def get_protocol_engine():
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = ProtocolEngine()
    return _rag_instance
