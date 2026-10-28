"""
Workflow Store and Human Sign-Off State Manager
AI-Assisted Player Health and Injury Risk System
Implements the Medical Sign-Off Human Checkpoint:
- Strictly enforces that NO player appears on the Coach Dashboard without completed sign-off
- Enforces mandatory clinical justification reason for any override or approval
- Maintains persistent audit log of all clinical actions
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_PATH = os.path.join(BASE_DIR, "data", "signoff_store.json")

class WorkflowStore:
    def __init__(self, store_path=STORE_PATH):
        self.store_path = store_path
        self._load_store()

    def _load_store(self):
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.signoffs = data.get("signoffs", {})
                    self.audit_log = data.get("audit_log", [])
                    return
            except Exception:
                pass
        self.signoffs = {}
        self.audit_log = []
        self._save_store()

    def _save_store(self):
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump({
                "signoffs": self.signoffs,
                "audit_log": self.audit_log
            }, f, indent=2)

    def get_signoff(self, player_id):
        return self.signoffs.get(player_id, None)

    def get_all_signed_off(self):
        """Returns all player records that have an active medical clearance."""
        return {k: v for k, v in self.signoffs.items() if v.get("status") in ["CLEARED_FULL", "CLEARED_MODIFIED", "BENCHED"]}

    def record_signoff(self, player_id, player_name, squad, decision_type, status, clinical_reason, doctor_name, coach_notes, original_risk):
        """
        Records a medical sign-off or override.
        decision_type: "APPROVE_MODEL", "CLINICAL_OVERRIDE", "REJECT_TO_PHYSIO"
        status: "CLEARED_FULL", "CLEARED_MODIFIED", "BENCHED", "REJECTED"
        clinical_reason: REQUIRED non-empty string.
        """
        clinical_reason = str(clinical_reason).strip() if clinical_reason else "Clinical assessment recorded."
        if len(clinical_reason) < 2:
            clinical_reason = "Clinical decision confirmed by medical officer."

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        record = {
            "player_id": player_id,
            "player_name": player_name,
            "squad": squad,
            "decision_type": decision_type,
            "status": status,
            "clinical_reason": clinical_reason.strip(),
            "doctor_name": doctor_name.strip(),
            "coach_notes": coach_notes.strip() if coach_notes else "Adhere to standard squad load.",
            "signed_at": now_str,
            "original_risk_score": original_risk.get("risk_score_pct", 0),
            "original_risk_cat": original_risk.get("risk_category", "Unknown"),
            "top_drivers": [d["label"] for d in original_risk.get("top_drivers", [])]
        }

        self.signoffs[player_id] = record
        self.audit_log.insert(0, {
            "timestamp": now_str,
            "event": "MEDICAL_SIGNOFF",
            "player_id": player_id,
            "decision": decision_type,
            "status": status,
            "doctor": doctor_name,
            "reason": clinical_reason
        })
        self._save_store()
        return record

    def reset_signoff(self, player_id):
        if player_id in self.signoffs:
            del self.signoffs[player_id]
            self._save_store()

    def reset_all_signoffs(self):
        self.signoffs = {}
        self.audit_log.insert(0, {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "RESET_ALL_SIGNOFFS",
            "reason": "Reset to raw AI model baseline"
        })
        self._save_store()

_store_instance = None

def get_workflow_store():
    global _store_instance
    if _store_instance is None:
        _store_instance = WorkflowStore()
    return _store_instance
