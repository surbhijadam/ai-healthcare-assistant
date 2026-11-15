"""
MediCare AI — Centralized Frontend API Client
Conforms to NFR-03.2 (Standardized error envelope) and Clean Architecture.
Provides robust communication between Streamlit frontend and FastAPI backend.
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
import streamlit as st

DEFAULT_API_BASE = os.getenv("MEDICARE_API_BASE", "http://127.0.0.1:8000/api/v1")
SESSION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".session_auth.json"))


class HealthcareApiClient:
    """Client for MediCare AI REST API with persistent session token management and offline resilience."""

    def __init__(self, base_url: str = DEFAULT_API_BASE, timeout: float = 4.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._in_memory_session: Dict[str, Any] = {}
        self._load_persisted_session()

    def _load_persisted_session(self) -> None:
        """Loads saved session from disk cache into in-memory session if valid."""
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("authenticated") and data.get("user"):
                        self._in_memory_session = data
        except Exception:
            pass

    def save_session(self, user: Dict[str, Any], token: Optional[str] = None) -> None:
        """Persists the user session so it survives browser navigations across pages."""
        session_data = {
            "authenticated": True,
            "token": token or "active_jwt_token",
            "user": user
        }
        self._in_memory_session = session_data
        try:
            with open(SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(session_data, f)
        except Exception:
            pass
        if hasattr(st, "session_state"):
            st.session_state["authenticated"] = True
            st.session_state["token"] = session_data["token"]
            st.session_state["user"] = user

    def get_persisted_session(self) -> Optional[Dict[str, Any]]:
        """Returns the active persistent session if available."""
        if self._in_memory_session.get("authenticated") and self._in_memory_session.get("user"):
            return self._in_memory_session
        self._load_persisted_session()
        if self._in_memory_session.get("authenticated") and self._in_memory_session.get("user"):
            return self._in_memory_session
        return None

    def clear_session(self) -> None:
        """Clears both memory and disk session caches."""
        self._in_memory_session = {}
        try:
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except Exception:
            pass
        if hasattr(st, "session_state"):
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["user"] = None

    def sync_session_state(self) -> Optional[Dict[str, Any]]:
        """
        Synchronizes Streamlit session_state with persistent storage.
        Call this at the beginning of any page render to prevent session loss on navigation.
        """
        if not hasattr(st, "session_state"):
            return None

        # 1. If currently marked authenticated with user in memory, ensure it is persisted
        if st.session_state.get("authenticated") and st.session_state.get("user"):
            token = st.session_state.get("token")
            user = st.session_state.get("user")
            if not self._in_memory_session.get("authenticated"):
                self.save_session(user, token)
            return user

        # 2. Otherwise restore from persistent disk cache
        stored = self.get_persisted_session()
        if stored and stored.get("authenticated") and stored.get("user"):
            st.session_state["authenticated"] = True
            st.session_state["token"] = stored.get("token")
            st.session_state["user"] = stored.get("user")
            return stored.get("user")

        # 3. Default to guest state
        st.session_state["authenticated"] = False
        st.session_state["token"] = None
        st.session_state["user"] = None
        return None

    def _get_headers(self, custom_token: Optional[str] = None) -> Dict[str, str]:
        """Constructs headers including Bearer token from session state if present."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        token = custom_token
        if not token and hasattr(st, "session_state"):
            token = st.session_state.get("token")
        if not token and self._in_memory_session.get("token"):
            token = self._in_memory_session.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parses response conforming to NFR-03.2 standardized envelope."""
        try:
            payload = response.json()
        except Exception:
            payload = {"status": "error", "message": response.text, "detail": None}

        if response.status_code >= 400:
            return {
                "success": False,
                "status_code": response.status_code,
                "message": payload.get("message", f"HTTP {response.status_code} Error"),
                "detail": payload.get("detail"),
                "data": None
            }
        return {
            "success": True,
            "status_code": response.status_code,
            "message": payload.get("message", "Success"),
            "data": payload.get("data")
        }

    def _offline_error(self, err: Exception) -> Dict[str, Any]:
        """Generates standardized offline/unreachable response when backend is down."""
        return {
            "success": False,
            "status_code": 503,
            "offline": True,
            "message": "MediCare AI Backend is offline or unreachable.",
            "detail": str(err),
            "data": None
        }

    # --------------------------------------------------------------------------
    # Health & System Probes
    # --------------------------------------------------------------------------
    def is_backend_online(self) -> bool:
        """Quickly checks if the FastAPI backend server is responsive."""
        try:
            res = requests.get(f"{self.base_url}/health", timeout=1.5)
            return res.status_code == 200
        except Exception:
            return False

    # --------------------------------------------------------------------------
    # Authentication & User Context
    # --------------------------------------------------------------------------
    def register(
        self,
        email: str,
        full_name: str,
        password: str,
        date_of_birth: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a new patient account (US-01 / FR-01.1)."""
        url = f"{self.base_url}/auth/register"
        body = {
            "email": email.strip(),
            "full_name": full_name.strip(),
            "password": password
        }
        if date_of_birth:
            body["date_of_birth"] = date_of_birth
        try:
            res = requests.post(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticates user credentials and returns JWT Bearer token (US-01 / FR-01.2)."""
        url = f"{self.base_url}/auth/login"
        body = {
            "email": email.strip(),
            "password": password
        }
        try:
            res = requests.post(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_me(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Fetches the current authenticated user details."""
        url = f"{self.base_url}/auth/me"
        try:
            res = requests.get(url, headers=self._get_headers(token), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def logout(self) -> Dict[str, Any]:
        """Invalidates user session and clears Streamlit state and persistent storage."""
        url = f"{self.base_url}/auth/logout"
        try:
            requests.post(url, headers=self._get_headers(), timeout=self.timeout)
        except Exception:
            pass
        self.clear_session()
        return {"success": True, "message": "Logged out successfully"}

    # --------------------------------------------------------------------------
    # Patient Profile & DPDP Act 2023
    # --------------------------------------------------------------------------
    def get_profile(self) -> Dict[str, Any]:
        """Retrieves user profile with calculated age and BMI."""
        url = f"{self.base_url}/profile"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def update_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates user demographic and clinical parameters."""
        url = f"{self.base_url}/profile"
        try:
            res = requests.put(url, json=profile_data, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def delete_profile(self) -> Dict[str, Any]:
        """Performs DPDP Act 2023 permanent cascading account and data erasure."""
        url = f"{self.base_url}/profile"
        try:
            res = requests.delete(url, headers=self._get_headers(), timeout=self.timeout)
            parsed = self._handle_response(res)
            if parsed.get("success"):
                if hasattr(st, "session_state"):
                    st.session_state["authenticated"] = False
                    st.session_state["token"] = None
                    st.session_state["user"] = None
            return parsed
        except Exception as e:
            return self._offline_error(e)

    # --------------------------------------------------------------------------
    # Clinical Entities (Reports, Meds, Appointments)
    # --------------------------------------------------------------------------
    def get_reports(self) -> Dict[str, Any]:
        """Retrieves patient medical reports list."""
        url = f"{self.base_url}/reports"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def upload_report(
        self,
        file_bytes: bytes,
        filename: str = "report.pdf",
        report_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Uploads a PDF medical report for PyMuPDF extraction & clinical analysis (FR-05)."""
        url = f"{self.base_url}/reports/upload"
        headers = {}
        token = None
        if hasattr(st, "session_state"):
            token = st.session_state.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        files = {"file": (filename, file_bytes, "application/pdf")}
        data = {}
        if report_title:
            data["report_title"] = report_title

        try:
            res = requests.post(url, files=files, data=data, headers=headers, timeout=self.timeout + 6.0)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_report_detail(self, report_id: int) -> Dict[str, Any]:
        """Retrieves structured parameters and AI summary for a specific report."""
        url = f"{self.base_url}/reports/{report_id}"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def delete_report(self, report_id: int) -> Dict[str, Any]:
        """Deletes a report record."""
        url = f"{self.base_url}/reports/{report_id}"
        try:
            res = requests.delete(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_medications(self) -> Dict[str, Any]:
        """Retrieves patient active medication regimen."""
        url = f"{self.base_url}/medications"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def create_medication(
        self,
        medication_name: str,
        dosage: str,
        frequency: str,
        start_date: str,
        end_date: Optional[str] = None,
        instructions: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers a new medication prescription (FR-06.1)."""
        url = f"{self.base_url}/medications"
        body = {
            "medication_name": medication_name.strip(),
            "dosage": dosage.strip(),
            "frequency": frequency.strip(),
            "start_date": start_date,
            "end_date": end_date,
            "instructions": instructions,
            "category": category
        }
        try:
            res = requests.post(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def toggle_dose_status(self, medication_id: int, status: str) -> Dict[str, Any]:
        """Toggles dose adherence status: Taken, Skipped, Upcoming (FR-06.2, US-05)."""
        url = f"{self.base_url}/medications/{medication_id}/toggle"
        body = {"status": status}
        try:
            res = requests.put(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def delete_medication(self, medication_id: int) -> Dict[str, Any]:
        """Deletes a medication entry."""
        url = f"{self.base_url}/medications/{medication_id}"
        try:
            res = requests.delete(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_appointments(self) -> Dict[str, Any]:
        """Retrieves scheduled appointments."""
        url = f"{self.base_url}/appointments"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def create_appointment(
        self,
        doctor_name: str,
        appointment_datetime: str,
        specialty: Optional[str] = None,
        clinic_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Books a new clinical doctor consultation (FR-07.1)."""
        url = f"{self.base_url}/appointments"
        body = {
            "doctor_name": doctor_name.strip(),
            "appointment_datetime": appointment_datetime,
            "specialty": specialty,
            "clinic_name": clinic_name,
            "notes": notes
        }
        try:
            res = requests.post(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def update_appointment(
        self,
        appointment_id: int,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        appointment_datetime: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates appointment status (upcoming, completed, cancelled) or notes (FR-07.2)."""
        url = f"{self.base_url}/appointments/{appointment_id}"
        body = {}
        if status:
            body["status"] = status
        if notes:
            body["notes"] = notes
        if appointment_datetime:
            body["appointment_datetime"] = appointment_datetime
        try:
            res = requests.put(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def delete_appointment(self, appointment_id: int) -> Dict[str, Any]:
        """Deletes an appointment consultation."""
        url = f"{self.base_url}/appointments/{appointment_id}"
        try:
            res = requests.delete(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    # --------------------------------------------------------------------------
    # AI Healthcare Chatbot & Conversations (FR-03 / US-02 / US-03 / FR-03.5)
    # --------------------------------------------------------------------------
    def chat_query(
        self,
        query: str,
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Submits conversational healthcare query with safety guardrails."""
        url = f"{self.base_url}/chat/query"
        body = {
            "query": query,
            "conversation_id": conversation_id,
            "stream": False
        }
        try:
            res = requests.post(url, json=body, headers=self._get_headers(), timeout=self.timeout + 6.0)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_conversations(self) -> Dict[str, Any]:
        """Retrieves list of user conversation threads."""
        url = f"{self.base_url}/chat/conversations"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def create_conversation(self, title: str = "Health Consultation") -> Dict[str, Any]:
        """Creates a new conversation session."""
        url = f"{self.base_url}/chat/conversations"
        body = {"title": title}
        try:
            res = requests.post(url, json=body, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_conversation_messages(self, conversation_id: int) -> Dict[str, Any]:
        """Retrieves all messages for a specific conversation."""
        url = f"{self.base_url}/chat/conversations/{conversation_id}/messages"
        try:
            res = requests.get(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def delete_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """Deletes a conversation thread and its message history."""
        url = f"{self.base_url}/chat/conversations/{conversation_id}"
        try:
            res = requests.delete(url, headers=self._get_headers(), timeout=self.timeout)
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    # --------------------------------------------------------------------------
    # Aggregated Dashboard Metrics Helper
    # --------------------------------------------------------------------------
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Gathers live metrics for Dashboard cards and widgets.
        Returns live counts if backend is online, or Canva prototype fallback if offline.
        """
        # Default empty fallbacks
        fallback_data = {
            "is_live": False,
            "total_reports": "00",
            "active_medications": "00",
            "upcoming_appointments": "00",
            "adherence_recorded": 0,
            "adherence_total": 0,
            "recent_activity": []
        }

        # Check online probe first
        if not self.is_backend_online():
            return fallback_data

        # Attempt to gather live backend data
        try:
            reports_res = self.get_reports()
            meds_res = self.get_medications()
            appts_res = self.get_appointments()

            total_reports = len(reports_res["data"]) if reports_res.get("success") and reports_res.get("data") else 0
            
            meds_list = meds_res.get("data", []) if meds_res.get("success") and meds_res.get("data") else []
            active_meds = len([m for m in meds_list if m.get("is_active", True)])
            taken_meds = len([m for m in meds_list if m.get("today_status") == "Taken"])

            appts_list = appts_res.get("data", []) if appts_res.get("success") and appts_res.get("data") else []
            upcoming_appts = len([a for a in appts_list if a.get("status") == "scheduled"])

            activities = []
            if reports_res.get("success") and reports_res.get("data"):
                for r in reports_res["data"][:2]:
                    activities.append({
                        "title": f"Report: {r.get('file_name', 'Lab report')}",
                        "date": str(r.get("uploaded_at", "Recently"))[:10],
                        "icon": "📄"
                    })
            if appts_res.get("success") and appts_res.get("data"):
                for a in appts_res["data"][:2]:
                    activities.append({
                        "title": f"Dr. {a.get('doctor_name', 'Specialist')} ({a.get('specialty', 'Consult')})",
                        "date": str(a.get("appointment_datetime", "Upcoming"))[:10],
                        "icon": "📅"
                    })

            return {
                "is_live": True,
                "total_reports": f"{total_reports:02d}",
                "active_medications": f"{active_meds:02d}",
                "upcoming_appointments": f"{upcoming_appts:02d}",
                "adherence_recorded": taken_meds,
                "adherence_total": len(meds_list),
                "recent_activity": activities
            }
        except Exception:
            return fallback_data

    # ==========================================================================
    # 7. Admin & Clinical Governance API Methods (FR-08.1 - FR-08.4, US-08)
    # ==========================================================================

    def get_admin_stats(self, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """Fetches platform overview statistics cards (FR-08.3)."""
        try:
            res = requests.get(
                f"{self.base_url}/admin/stats",
                headers=self._get_headers(custom_token),
                timeout=self.timeout
            )
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_admin_activity(self, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """Fetches chronological system activity feed."""
        try:
            res = requests.get(
                f"{self.base_url}/admin/activity",
                headers=self._get_headers(custom_token),
                timeout=self.timeout
            )
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_admin_audit_logs(self, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """Inspects platform audit telemetry logs (FR-08.2)."""
        try:
            res = requests.get(
                f"{self.base_url}/admin/audit-logs",
                headers=self._get_headers(custom_token),
                timeout=self.timeout
            )
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_admin_users(self, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """Fetches user management accounts table."""
        try:
            res = requests.get(
                f"{self.base_url}/admin/users",
                headers=self._get_headers(custom_token),
                timeout=self.timeout
            )
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def get_admin_knowledge_documents(self, custom_token: Optional[str] = None) -> Dict[str, Any]:
        """Fetches RAG knowledge base guidelines list (FR-04.1)."""
        try:
            res = requests.get(
                f"{self.base_url}/admin/knowledge-documents",
                headers=self._get_headers(custom_token),
                timeout=self.timeout
            )
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)

    def create_knowledge_document(
        self,
        title: str,
        category: str = "Clinical Guideline",
        content: str = "",
        source_url: str = "",
        custom_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ingests a verified healthcare guideline into RAG vector repository (FR-04.1)."""
        try:
            payload = {
                "title": title,
                "category": category,
                "content": content,
                "source_url": source_url
            }
            res = requests.post(
                f"{self.base_url}/admin/knowledge-documents",
                json=payload,
                headers=self._get_headers(custom_token),
                timeout=self.timeout
            )
            return self._handle_response(res)
        except Exception as e:
            return self._offline_error(e)


# Global client instance
api_client = HealthcareApiClient()
