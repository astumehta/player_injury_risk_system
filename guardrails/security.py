"""
Security and Guardrails Engine
AI-Assisted Player Health and Injury Risk System
Compliance with Section 5 of Midterm Progress Report:
1. Input validation (bounds checking, prevents injection in numeric fields)
2. PII De-identification (replaces names with IDs before processing)
3. Output filter (blocks medical diagnoses, medication prescription, unauthorized clearance)
4. Prompt injection detector
"""

import re

class SecurityGuardrails:
    # Diagnostic terms prohibited under B2B athletic software regulations
    PROHIBITED_DIAGNOSES = [
        r"\bdiagnos(?:ed|is|ing)\b",
        r"\bpathology\b",
        r"\bgrade\s+[123]\s+(?:tear|strain|sprain)\b",
        r"\bavulsion\b",
        r"\bruptur(?:e|ed)\b",
        r"\btendinopathy\b",
        r"\bfracture\b"
    ]
    
    # Medication / drug terms prohibited
    PROHIBITED_MEDICATIONS = [
        r"\bprescri(?:be|ption|bed)\b",
        r"\bibuprofen\b",
        r"\bparacetamol\b",
        r"\badvil\b",
        r"\bcorticosteroid\b",
        r"\bnsaid\b",
        r"\banalgesic\b",
        r"\btramadol\b",
        r"\bdose\b",
        r"\bmg\b",
        r"\binjection\b"
    ]
    
    # Premature or automated clearance prohibited before medical sign-off
    PROHIBITED_CLEARANCES = [
        r"\bcleared\s+to\s+play\b",
        r"\bfit\s+to\s+play\b",
        r"\bunconditionally\s+cleared\b",
        r"\bmatch\s+day\s+certified\b"
    ]
    
    # Prompt injection vectors
    INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?(?:previous\s+)?(?:instructions|rules|protocol)",
        r"(?:system\s+)?override",
        r"system\s+(?:prompt|dump)",
        r"bypass\s+(?:protocol|check|human)",
        r"you\s+are\s+now\s+(?:an?\s+)?(?:unconstrained|doctor|physician)",
        r"clear\s+player\s+\d+",
        r"print\s+(?:all\s+)?(?:secrets|keys)",
        r"jailbreak",
        r"developer\s+mode",
        r"<script.*?>",
        r"javascript:",
        r"(?:union\s+select|select\s+.*\s+from|drop\s+table|--|'\s*or\s*'1'='1')",
        r"(?:real\s+names|exfiltrat|webhook|phone\s+numbers|addresses)",
        r"(?:update\s+.*\s+table|direct\s+database)",
        r"(?:invent\s+clause|unregistered\s+clause)"
    ]

    @staticmethod
    def validate_inputs(features):
        """
        Rejects out-of-range values and blocks free-text injection.
        Returns: (is_valid: bool, error_message: str or None)
        """
        # 1. Check Sleep: 0.0 to 14.0 hrs
        try:
            sleep = float(features.get("sleep_hours", 7.0))
            if sleep < 0.0 or sleep > 14.0:
                return False, f"Sleep duration ({sleep:.1f} hrs) is out of valid bounds [0.0 - 14.0 hrs]."
        except (ValueError, TypeError):
            return False, "Sleep value must be a valid numeric quantity, not text."

        # 2. Check ACWR: 0.2 to 3.0
        try:
            acwr = float(features.get("acwr", 1.0))
            if acwr < 0.2 or acwr > 3.0:
                return False, f"ACWR ({acwr:.2f}) is out of valid bounds [0.20 - 3.00]."
        except (ValueError, TypeError):
            return False, "ACWR must be a valid numeric float."

        # 3. Check Soreness: 1.0 to 10.0
        try:
            soreness = float(features.get("soreness", 3.0))
            if soreness < 1.0 or soreness > 10.0:
                return False, f"Soreness ({soreness:.1f}) must be on a 1.0 to 10.0 scale."
        except (ValueError, TypeError):
            return False, "Soreness must be a valid numeric score."

        # 4. Check Workload: 0 to 8000 AU
        try:
            acute = float(features.get("acute_load", 2000.0))
            if acute < 0 or acute > 8000:
                return False, f"Acute load ({acute:.0f}) out of physical bounds [0 - 8000 AU]."
        except (ValueError, TypeError):
            return False, "Acute load must be a valid integer or float."

        # 5. Check for injection attempt in string fields (like staff notes)
        staff_notes = str(features.get("staff_notes", ""))
        for pattern in SecurityGuardrails.INJECTION_PATTERNS:
            if re.search(pattern, staff_notes, re.IGNORECASE):
                return False, f"Security Violation: Suspected adversarial prompt injection detected in notes ('{pattern}')."

        return True, None

    @staticmethod
    def deidentify_pii(text, player_name, player_id):
        """
        DPDP Compliance: Replaces player names with standardized IDs before LLM processing.
        """
        if not text:
            return ""
        # Mask specific name
        masked = re.sub(re.escape(player_name), player_id, text, flags=re.IGNORECASE)
        # Mask general name patterns if any
        return masked

    @classmethod
    def sanitize_output(cls, raw_output_text):
        """
        Enforces output guardrails:
        - Blocks clinical diagnoses
        - Blocks medication/drug instructions
        - Blocks unauthorized 'cleared to play' wording
        Returns: (sanitized_text, violations_detected)
        """
        violations = []
        sanitized = raw_output_text

        # 1. Scan diagnoses
        for pattern in cls.PROHIBITED_DIAGNOSES:
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                violations.append(f"Clinical Diagnosis Language: '{matches[0]}'")
                sanitized = re.sub(pattern, "[REDACTED: Non-Diagnostic Policy]", sanitized, flags=re.IGNORECASE)

        # 2. Scan medications
        for pattern in cls.PROHIBITED_MEDICATIONS:
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                violations.append(f"Medication / Prescription Term: '{matches[0]}'")
                sanitized = re.sub(pattern, "[REDACTED: Medical Prescription Policy]", sanitized, flags=re.IGNORECASE)

        # 3. Scan premature clearance
        for pattern in cls.PROHIBITED_CLEARANCES:
            matches = re.findall(pattern, sanitized, re.IGNORECASE)
            if matches:
                violations.append(f"Unauthorized Clearance Phrase: '{matches[0]}'")
                sanitized = re.sub(pattern, "[REQUIRES MEDICAL SIGN-OFF]", sanitized, flags=re.IGNORECASE)

        # 4. Scan for invented / unregistered protocol clauses
        if re.search(r"(?:invent\s+clause|clause\s+[789]\.\d+)", sanitized, re.IGNORECASE):
            violations.append("Unverified Protocol Clause Invention Attempt")
            sanitized = re.sub(r"(?:invent\s+clause|clause\s+[789]\.\d+)", "[INVALID: Unregistered Protocol Clause]", sanitized, flags=re.IGNORECASE)

        return sanitized, violations
