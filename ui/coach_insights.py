"""
Harbourline FC — Coach Decision Support Engine
Translates sports science metrics, model risk scores, and doctor sign-offs
into tactical coaching insights:
1. Availability Status (Available / Modified / Benched)
2. Primary Reason for restriction or clearance
3. Likely Return-to-Play Timeline (When ready for 90-min competitive match)
4. Doctor's Specific Drill Recommendations for Head Coach
"""

def get_coach_player_insights(row, model_res, signoff_record=None):
    """
    Computes coach-specific tactical availability, return timeline, and doctor drill instructions.
    """
    pid = row["player_id"]
    pos = row["position"]
    acwr = float(row.get("acwr", 1.0))
    soreness = int(row.get("soreness", 3))
    sleep_h = float(row.get("sleep_hours", 7.5))
    sleep_debt = float(row.get("sleep_debt_3w", 0.0))
    wellness = int(row.get("wellness", 7))
    weeks_since_return = row.get("weeks_since_return")
    
    tier = model_res.get("risk_tier", "LOW RISK")
    prob = model_res.get("risk_score_pct", model_res.get("probability_pct", 0.0))
    reasons = model_res.get("top_3_reasons", [])
    top_driver = reasons[0] if len(reasons) > 0 else f"ACWR {acwr:.2f}, Soreness {soreness}/10"

    # Check if there is an official Doctor Sign-Off in the workflow store
    if signoff_record:
        doc_status = signoff_record.get("status")
        doctor_name = signoff_record.get("doctor_name", "Dr. Astu Mehta, Medical Lead")
        signed_at = signoff_record.get("signed_at", "")
        coach_drills = signoff_record.get("coach_notes", "")
        clinical_reason = signoff_record.get("clinical_reason", "")
        is_signed = True
        
        if doc_status == "CLEARED_FULL":
            status_code = "AVAILABLE"
            status_label = "🟢 AVAILABLE (MATCH READY)"
            badge_color = "#10b981"
            timeline = "⚽ Immediate (Cleared for Match Selection)"
            timeline_desc = "Fully cleared for 90-minute competitive match intensity and full tactical pitch drills."
            if not coach_drills:
                coach_drills = "Full session as planned. Standard squad matchload."
        elif doc_status == "CLEARED_MODIFIED":
            status_code = "MODIFIED"
            status_label = "🟡 MODIFIED TRAINING ONLY"
            badge_color = "#f59e0b"
            timeline = "⏱️ Likely Match-Ready in 3–5 Days"
            timeline_desc = "Requires 48–72h active de-loading (ACWR ≤ 1.20, no sprinting >20 km/h) before full match clearance."
            if not coach_drills:
                coach_drills = "Modified technical drills only; max 45 mins; NO sprint drills >20 km/h."
        else: # BENCHED or REJECTED
            status_code = "BENCHED"
            status_label = "🔴 BENCHED / SIDELINED"
            badge_color = "#ef4444"
            timeline = "🏥 Estimated 10–14 Days (Physio Screen Required)"
            timeline_desc = "Mandatory 48h complete off-pitch rest followed by 5-stage return-to-play protocol under Rule RTP-5."
            if not coach_drills:
                coach_drills = "Off-pitch gym recovery only; Wattbike and pool session; NO on-pitch drills."

        doctor_block = {
            "is_signed": True,
            "status_code": status_code,
            "status_label": status_label,
            "badge_color": badge_color,
            "doctor_name": doctor_name,
            "signed_at": signed_at,
            "clinical_reason": clinical_reason,
            "coach_drills": coach_drills,
            "timeline": timeline,
            "timeline_desc": timeline_desc,
            "reason": top_driver
        }
        return doctor_block

    # If NO doctor sign-off has been submitted yet:
    # Use Model & Protocol provisional tier, but flag compliance warning under Rule AI-6.4 & GOV-1.5
    is_signed = False
    if tier == "LOW RISK":
        status_code = "AVAILABLE"
        status_label = "🟢 AVAILABLE (Provisional Check)"
        badge_color = "#10b981"
        timeline = "⚽ Available for Selection (Pending Sign-off)"
        timeline_desc = "Optimal conditioning. Low probability (P < 5.0%). Expected full match readiness."
        coach_drills = "Adhere to standard squad matchload. Normal hydration and recovery."
        clinical_reason = "Model evaluated low risk. Awaiting routine medical lead stamp."
    elif tier == "MODERATE RISK":
        status_code = "MODIFIED"
        status_label = "🟡 MODIFIED TRAINING (Provisional)"
        badge_color = "#f59e0b"
        timeline = "⏱️ Likely Match-Ready in 3–5 Days"
        timeline_desc = "Elevated ACWR or accumulated sleep debt requires active recovery before full selection."
        coach_drills = "Technical passing drills only; NO sprint blocks >20 km/h; cap session at 45 mins."
        clinical_reason = "Cautionary fatigue flag. Capping high-speed sprint volume under Rule LM-3.3."
    else: # HIGH RISK
        status_code = "BENCHED"
        status_label = "🔴 SIDELINED / HIGH RISK (Pending Doctor)"
        badge_color = "#ef4444"
        timeline = "🏥 Estimated 10–14 Days (Physio Screen Required)"
        timeline_desc = "Workload spike or high muscle soreness. Critical strain danger under Rule LM-3.4."
        coach_drills = "Do NOT select for pitch training. Wattbike and gym recovery only until screened."
        clinical_reason = "Mandatory physio ultrasound screen required within 24 hours under Rule AI-6.2."

    # Edge Case: Returning player
    import pandas as pd
    if pd.notna(weeks_since_return) and weeks_since_return in [1, 2]:
        timeline = f"🎯 Stage 5 Return-to-Play: 5–7 Days to 90-min clearance"
        timeline_desc = f"Athlete in {('first' if weeks_since_return == 1 else 'second')} week back from soft-tissue injury. Max 30 mins match exposure."

    return {
        "is_signed": False,
        "status_code": status_code,
        "status_label": status_label,
        "badge_color": badge_color,
        "doctor_name": "Pending Doctor Call (Dr. Astu Mehta)",
        "signed_at": "Pending",
        "clinical_reason": clinical_reason,
        "coach_drills": coach_drills,
        "timeline": timeline,
        "timeline_desc": timeline_desc,
        "reason": top_driver
    }
