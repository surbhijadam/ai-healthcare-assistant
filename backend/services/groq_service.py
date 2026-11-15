"""
MediCare AI — Groq LPU Inference Service
Conforms to FR-03.1 (Streaming responses), FR-03.2 (Disclaimers), FR-03.4 (Guardrails), and NFR-01.1 (Latency).
Utilizes Groq LPU high-speed inference with resilient offline educational fallback.
"""

import os
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from backend.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_CLINICAL_PROMPT = """You are MediCare AI, an empathetic, highly knowledgeable, and safety-first AI Healthcare Assistant.
Your primary mission is to explain medical concepts, lab results, medications, and general health topics in clear, patient-friendly, everyday language.

MANDATORY CLINICAL SAFETY RULES:
1. NON-DIAGNOSTIC MANDATE: Never provide a definitive medical diagnosis. Always explain potential general causes of symptoms and emphasize that only a qualified physician can diagnose medical conditions.
2. NO PRESCRIPTION OR DOSAGE ADVICE: Never recommend specific prescription pharmaceuticals, calculate drug dosages, or advise the user to start, alter, or discontinue any prescription medication.
3. EMERGENCY INTERCEPTION: If the user appears to experience acute, life-threatening symptoms (e.g., severe crushing chest pain, difficulty breathing, stroke symptoms, uncontrolled bleeding), immediately direct them to call emergency services (112 / 911).
4. CLINICAL DISCLAIMER: Every response must be educational in nature, reminding the user that this does not substitute for professional medical care.
5. TONE & CLARITY: Maintain a calm, empathetic, and reassuring tone. Avoid dense medical jargon, or explain technical terms immediately in plain English.
"""

DISCLAIMER_TEXT = "\n\n---\n*Notice: This information is for educational purposes only and does not constitute medical advice, diagnosis, or prescription. Always consult your healthcare provider.*"


class GroqHealthcareService:
    """Service for generating fast, clinically guardrailed conversational healthcare responses via Groq."""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY)
        self.model = os.getenv("GROQ_MODEL", settings.GROQ_MODEL)
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes Groq client if valid API key is present."""
        is_mock_key = not self.api_key or self.api_key in [
            "mock_groq_api_key_for_development",
            "your_groq_api_key_here",
            "mock_api_key"
        ]
        if not is_mock_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Groq client: {e}. Using resilient local fallback.")
                self._client = None
        else:
            self._client = None

    def is_live_groq_available(self) -> bool:
        """Returns True if a live Groq client with valid credentials is ready."""
        return self._client is not None

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        rag_context: Optional[str] = None
    ) -> str:
        """
        Generates conversational response using Groq LPU API if configured,
        or falls back to domain-specific clinical educational responses.
        """
        # Prepare full message payload including system prompt
        formatted_messages = [{"role": "system", "content": SYSTEM_CLINICAL_PROMPT}]

        # Inject RAG context if available (Phase 8 integration)
        if rag_context:
            formatted_messages.append({
                "role": "system",
                "content": f"Verified Clinical Knowledge Base Context:\n{rag_context}\nGround your answer in this verified clinical data."
            })

        for msg in messages:
            formatted_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })

        # Attempt live Groq call if client initialized
        if self._client:
            try:
                chat_completion = self._client.chat.completions.create(
                    messages=formatted_messages,
                    model=self.model,
                    temperature=0.3,
                    max_tokens=800
                )
                answer = chat_completion.choices[0].message.content
                if DISCLAIMER_TEXT not in answer:
                    answer += DISCLAIMER_TEXT
                return answer
            except Exception as e:
                logger.warning(f"Groq API call encountered error: {e}. Falling back to offline engine.")

        # Fallback intelligent clinical educational response
        last_query = messages[-1].get("content", "") if messages else ""
        return self._generate_educational_fallback(last_query)

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        rag_context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Streams response chunks in real-time conforming to FR-03.1 & NFR-01.1.
        """
        # If live Groq client is active, stream tokens
        if self._client:
            try:
                formatted_messages = [{"role": "system", "content": SYSTEM_CLINICAL_PROMPT}]
                if rag_context:
                    formatted_messages.append({
                        "role": "system",
                        "content": f"Verified Clinical Knowledge Base Context:\n{rag_context}"
                    })
                for msg in messages:
                    formatted_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })

                stream = self._client.chat.completions.create(
                    messages=formatted_messages,
                    model=self.model,
                    temperature=0.3,
                    max_tokens=800,
                    stream=True
                )
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    if delta:
                        yield delta
                yield DISCLAIMER_TEXT
                return
            except Exception as e:
                logger.warning(f"Groq streaming failed: {e}. Streaming offline fallback.")

        # Streaming offline fallback word-by-word
        last_query = messages[-1].get("content", "") if messages else ""
        full_text = self._generate_educational_fallback(last_query)
        words = full_text.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

    def _generate_educational_fallback(self, query: str) -> str:
        """High-quality educational responses adhering to FR-03.4 non-diagnostic rules."""
        q_lower = query.lower()

        # Specific medical topics
        if "ldl" in q_lower or "cholesterol" in q_lower:
            return (
                "**Understanding LDL Cholesterol and Cardiovascular Health**\n\n"
                "Low-Density Lipoprotein (LDL cholesterol) is often called 'bad' cholesterol because elevated levels can contribute to fatty deposits in arteries (atherosclerosis).\n\n"
                "**Clinical Guidelines Reference:**\n"
                "- Optimal: Below 100 mg/dL for most adults.\n"
                "- Near optimal: 100–129 mg/dL.\n"
                "- Borderline high: 130–159 mg/dL.\n"
                "- High: 160–189 mg/dL.\n\n"
                "**Next Steps to Discuss With Your Doctor:**\n"
                "- Ask how your individual cardiovascular risk factors (family history, blood pressure, lifestyle) influence your target LDL level.\n"
                "- Discuss heart-healthy dietary habits such as increasing soluble fiber and reducing saturated fats."
                + DISCLAIMER_TEXT
            )

        if "blood pressure" in q_lower or "hypertension" in q_lower:
            return (
                "**Understanding Blood Pressure Categories**\n\n"
                "Blood pressure readings consist of two numbers: systolic (pressure when the heart beats) over diastolic (pressure when the heart rests between beats).\n\n"
                "**Standard Adult Classifications:**\n"
                "- **Normal:** Less than 120/80 mmHg.\n"
                "- **Elevated:** Systolic between 120–129 mmHg and diastolic less than 80 mmHg.\n"
                "- **Stage 1 Hypertension:** Systolic 130–139 mmHg or diastolic 80–89 mmHg.\n"
                "- **Stage 2 Hypertension:** Systolic 140 mmHg or higher, or diastolic 90 mmHg or higher.\n\n"
                "**Key Questions for Your Doctor:**\n"
                "- Should I keep a home blood pressure log at consistent morning and evening times?\n"
                "- What lifestyle interventions (sodium reduction, physical activity) are recommended for my baseline?"
                + DISCLAIMER_TEXT
            )

        if "glucose" in q_lower or "sugar" in q_lower or "diabetes" in q_lower or "hba1c" in q_lower:
            return (
                "**Understanding Blood Glucose & HbA1c Markers**\n\n"
                "Blood glucose measurements assess how effectively your body regulates sugar for energy:\n\n"
                "- **Fasting Blood Glucose:** Measures blood sugar after an overnight fast (typically 70–99 mg/dL is considered normal).\n"
                "- **HbA1c (Glycated Hemoglobin):** Reflects average blood sugar levels over the past 2–3 months. A level below 5.7% is considered normal; 5.7%–6.4% indicates prediabetes; 6.5% or higher on two separate tests indicates diabetes.\n\n"
                "**Clinical Recommendation:**\n"
                "Discuss with your clinician whether repeat testing or targeted dietary modifications are advisable based on your complete metabolic panel."
                + DISCLAIMER_TEXT
            )

        if "asthma" in q_lower or "inhaler" in q_lower:
            return (
                "**Understanding Asthma & Respiratory Inhalers**\n\n"
                "Asthma is a chronic condition causing inflammation and narrowing of the airways. Inhalers generally fall into two broad categories:\n\n"
                "1. **Controller / Maintenance Inhalers:** Taken daily to reduce underlying airway inflammation (typically inhaled corticosteroids).\n"
                "2. **Rescue Inhalers:** Fast-acting bronchodilators (such as albuterol) used to relieve acute symptoms like wheezing or cough.\n\n"
                "**Safety Note:** Always follow your physician's written Asthma Action Plan regarding which inhaler to use and when to seek urgent care."
                + DISCLAIMER_TEXT
            )

        # General educational response
        return (
            "**Healthcare Assistant Educational Summary**\n\n"
            "I can help explain medical terms, laboratory reference ranges, and general preventive wellness habits in plain language.\n\n"
            "**Important Safety Principles:**\n"
            "- As an AI educational companion, I do not diagnose illnesses, prescribe medication, or adjust pharmaceutical dosages.\n"
            "- If you are experiencing unusual, persistent, or worsening symptoms, please schedule an appointment with your healthcare provider for an in-person physical assessment."
            + DISCLAIMER_TEXT
        )


# Global singleton instance
groq_service = GroqHealthcareService()
