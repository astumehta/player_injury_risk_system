"""
Demo Cases Module
AI-Assisted Player Health and Injury Risk System
Implements the 3 canonical rehearsal demo cases specified in Section 8 of Midterm Report:
1. Low Risk (Starter cleared for full match intensity)
2. High Risk (Severe ACWR spike + sleep debt + hamstring history)
3. Borderline / Conflicting Protocol Edge Case (Exceptional subjective wellness vs Absolute Load Ceiling)
"""

DEMO_CASES = {
    "case_low_risk": {
        "id": "CASE_1",
        "title": "Case 1: Low Risk (Fit Starter)",
        "badge_color": "#10b981", # Emerald
        "player_id": "PL-003",
        "player_name": "Marcus Vance",
        "squad": "First Team Squad",
        "position": "Forward",
        "age": 27,
        "prior_injuries": 0,
        "metrics": {
            "acwr": 1.08,
            "acute_load": 2350.0,
            "chronic_load": 2180.0,
            "sleep_hours": 8.2,
            "soreness": 2.0,
            "wellness_score": 9.1,
            "prior_injuries": 0,
            "age": 27,
            "match_minutes": 85,
            "load_trend_3w": 3.2,
            "sleep_debt_3w": 0.0,
            "avg_soreness_3w": 2.2,
            "staff_notes": "Completed full technical session with no tightness reported."
        },
        "description": "Prime starter exhibiting optimal acute:chronic workload balance and ideal sleep recovery. Demonstrates clean protocol alignment with Clause 2.1."
    },
    "case_high_risk": {
        "id": "CASE_2",
        "title": "Case 2: High Risk (Acute Spike & Sleep Debt)",
        "badge_color": "#ef4444", # Crimson
        "player_id": "PL-017",
        "player_name": "Mateo Silva",
        "squad": "First Team Squad",
        "position": "Midfielder",
        "age": 29,
        "prior_injuries": 2,
        "metrics": {
            "acwr": 1.68,
            "acute_load": 3850.0,
            "chronic_load": 2290.0,
            "sleep_hours": 5.4,
            "soreness": 7.8,
            "wellness_score": 4.1,
            "prior_injuries": 2,
            "age": 29,
            "match_minutes": 90,
            "load_trend_3w": 34.5,
            "sleep_debt_3w": 14.2,
            "avg_soreness_3w": 7.1,
            "staff_notes": "Complained of hamstring stiffness post-match. Late travel return affected sleep."
        },
        "description": "High-risk soft tissue profile: severe ACWR spike (>1.50), high 3-week sleep debt, and elevated hamstring soreness. Model and protocol trigger immediate red-flag modification."
    },
    "case_borderline_conflict": {
        "id": "CASE_3",
        "title": "Case 3: Borderline (Conflicting Protocol Edge Case)",
        "badge_color": "#f59e0b", # Amber
        "player_id": "PL-024",
        "player_name": "Liam O'Connor",
        "squad": "First Team Squad",
        "position": "Defender",
        "age": 24,
        "prior_injuries": 1,
        "metrics": {
            "acwr": 1.58,
            "acute_load": 3450.0,
            "chronic_load": 2180.0,
            "sleep_hours": 8.5,
            "soreness": 1.5,
            "wellness_score": 9.3,
            "prior_injuries": 1,
            "age": 24,
            "match_minutes": 65,
            "load_trend_3w": 28.0,
            "sleep_debt_3w": 0.0,
            "avg_soreness_3w": 2.0,
            "staff_notes": "Returning from Grade 1 strain. Subjectively feels in peak shape with zero soreness."
        },
        "description": "Deliberate conflicting edge case: Athlete meets Rapid Progression Exemption (Clause 3.4) but breaches the Absolute Load Ceiling (Clause 5.2). Requires Medical Director clinical intervention (Clause 6.1)."
    }
}
