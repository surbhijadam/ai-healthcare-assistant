"""
MediCare AI — Clinical Emergency Triage & Guardrails Service
Conforms to FR-03.3 (Emergency Red-Flag Interception) and US-03.
Detects acute life-threatening symptoms and directs users to immediate emergency services.
"""

from typing import Dict, Any, List, Optional
from backend.core.config import settings


class ClinicalTriageService:
    """Evaluates user queries against clinical emergency criteria and non-diagnostic guardrails."""

    def __init__(self, emergency_keywords: Optional[List[str]] = None):
        self.emergency_keywords = [
            kw.lower() for kw in (emergency_keywords or settings.EMERGENCY_KEYWORDS)
        ]
        # Extended high-risk acute symptom patterns
        self.critical_patterns = [
            "crushing chest pain",
            "chest pain radiating",
            "can't breathe",
            "cannot breathe",
            "short of breath",
            "coughing blood",
            "vomiting blood",
            "sudden weakness",
            "face drooping",
            "slurred speech",
            "loss of vision",
            "anaphylactic",
            "severe allergic reaction",
            "passed out",
            "unconscious",
            "suicidal",
            "kill myself",
            "overdosed"
        ]

    def evaluate_query(self, query: str) -> Dict[str, Any]:
        """
        Scans query for critical red-flag symptoms.
        Returns triage evaluation detailing emergency status and safety instructions.
        """
        q_lower = query.lower()
        matched_flags = []

        # Check critical multi-word patterns first
        for pattern in self.critical_patterns:
            if pattern in q_lower:
                matched_flags.append(pattern)

        # Check configured emergency keywords
        for kw in self.emergency_keywords:
            if kw in q_lower and kw not in matched_flags:
                matched_flags.append(kw)

        if matched_flags:
            return {
                "is_emergency": True,
                "matched_symptoms": matched_flags,
                "emergency_warning": f"Critical symptoms detected: {', '.join(matched_flags)}",
                "directive": (
                    "🚨 **CRITICAL MEDICAL EMERGENCY DIRECTIVE**\n\n"
                    "Your query describes symptoms that may represent an immediate, life-threatening emergency. "
                    "**Do not wait for or rely on an AI assistant.**\n\n"
                    "**Immediate Actions Required:**\n"
                    "1. **Dial 112 / 911** (Emergency Services in India / US / International) immediately.\n"
                    "2. Proceed to the nearest Hospital Emergency Department.\n"
                    "3. If experiencing acute chest pain or difficulty breathing, rest calmly while waiting for paramedics."
                ),
                "contacts": {
                    "emergency_india": "112",
                    "emergency_ambulance": "108",
                    "emergency_us": "911",
                    "emergency_uk": "999"
                }
            }

        return {
            "is_emergency": False,
            "matched_symptoms": [],
            "emergency_warning": None,
            "directive": None,
            "contacts": None
        }


# Global singleton instance
triage_service = ClinicalTriageService()
