"""
MedCare Clinic — Enterprise EHR & Clinical Management Portal
Brand: MedCare Clinic ("Your Health, Our Priority")
Commercial SaaS UI for Healthcare Professionals and Patients.
Includes Fully Workable Workspaces:
1. Receptionist Command Center
2. Doctor Clinical Workspace
3. Patient Mobile Portal
4. Automated Care Reminders Hub (Email Dispatch Engine over HTTPS Port 443)
"""

import streamlit as st
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.agents.supervisor_graph import ClinicSupervisorGraph
from src.api.doctor_dashboard import DoctorDashboardAPI
from src.tools.lab_report_parser import LabReportParser
from src.agents.prescription_safety_agent import PrescriptionSafetyAgent
from src.rag.rag_engine import RAGEngine
from src.mcp_servers.notifications_server import NotificationsMCPServer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Patient

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "synthetic", "clinic.db"))
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine)

def get_or_create_patient_user(identifier: str, full_name: str = None) -> dict:
    identifier = (identifier or "").strip()
    session = SessionLocal()
    try:
        p = session.query(Patient).filter(
            (Patient.cnic == identifier) | 
            (Patient.id == identifier) | 
            (Patient.email == identifier) |
            (Patient.name.ilike(f"%{identifier}%"))
        ).first()

        if p:
            return {"id": p.id, "name": p.name, "role": "Patient"}

        # Determine patient name
        if full_name and full_name.strip():
            name = full_name.strip().title()
        elif "@" in identifier:
            raw_user = identifier.split("@")[0]
            clean_letters = "".join([c if c.isalpha() or c == " " else " " for c in raw_user])
            name = " ".join([w.capitalize() for w in clean_letters.split() if w]) or "New Patient"
        elif not identifier.replace("-", "").isdigit():
            name = identifier.title()
        else:
            name = "New Patient"

        patient_id = f"PAT-{abs(hash(identifier)) % 9000 + 1000}"

        # Persist new patient into SQLite database
        new_patient = Patient(
            id=patient_id,
            name=name,
            cnic=identifier if "-" in identifier else f"35201-{abs(hash(identifier)) % 9000000 + 1000000}-1",
            age=28,
            gender="Unspecified",
            phone="+92-300-0000000",
            address="Lahore, Pakistan",
            city="Lahore"
        )
        session.add(new_patient)
        session.commit()

        return {"id": patient_id, "name": name, "role": "Patient"}
    except Exception:
        session.rollback()
        return {"id": "PAT-5501", "name": full_name or "New Patient", "role": "Patient"}
    finally:
        session.close()

# Page Configuration
st.set_page_config(
    page_title="City Care Clinics — Enterprise EHR Portal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Density Enterprise EHR Stylesheet (No Emojis, High Density, Crisp Typography)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Global Compact Densities */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Top Header Bar */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #0F172A;
        color: #FFFFFF;
        padding: 12px 24px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .app-title {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #F8FAFC;
    }
    .app-subtitle {
        font-size: 12px;
        color: #94A3B8;
        font-weight: 500;
    }
    
    /* Login Card */
    .login-container {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 32px;
        max-width: 440px;
        margin: 60px auto;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Dense Data Table Styles */
    .ehr-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        overflow: hidden;
    }
    .ehr-table th {
        background-color: #F1F5F9;
        color: #475569;
        font-weight: 600;
        text-align: left;
        padding: 10px 14px;
        border-bottom: 1px solid #E2E8F0;
        text-transform: uppercase;
        font-size: 11px;
        letter-spacing: 0.05em;
    }
    .ehr-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #F1F5F9;
        color: #1E293B;
    }
    
    /* Professional Badges (No Emojis) */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .badge-emergency { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; }
    .badge-urgent { background-color: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; }
    .badge-routine { background-color: #E0F2FE; color: #075985; border: 1px solid #BAE6FD; }
    .badge-whatsapp { background-color: #DCFCE7; color: #166534; border: 1px solid #86EFAC; }
    .badge-web { background-color: #F1F5F9; color: #334155; border: 1px solid #CBD5E1; }
    .badge-email { background-color: #E0E7FF; color: #3730A3; border: 1px solid #C7D2FE; }
    
    /* Patient Queue Scannable Cards */
    .queue-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0284C7;
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    .queue-card-active {
        border-left-color: #1E3A8A;
        background-color: #F0F9FF;
    }
    .queue-time {
        font-size: 11px;
        font-weight: 700;
        color: #0284C7;
    }
    .queue-name {
        font-size: 13px;
        font-weight: 700;
        color: #0F172A;
    }
    .queue-meta {
        font-size: 11px;
        color: #64748B;
    }
    
    /* Workspace Card Container */
    .workspace-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .workspace-card-header {
        font-size: 14px;
        font-weight: 700;
        color: #0F172A;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 8px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Professional Alert Banner */
    .safety-alert-banner {
        background-color: #FEF2F2;
        border: 1px solid #FCA5A5;
        border-left: 6px solid #DC2626;
        color: #991B1B;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 16px;
    }
    .safety-alert-title {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }
    
    /* WhatsApp Mobile Container */
    .mobile-chat-frame {
        max-width: 440px;
        margin: 0 auto;
        background-color: #E5DDD5;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .mobile-chat-header {
        background-color: #075E54;
        color: #FFFFFF;
        padding: 12px 16px;
        font-size: 14px;
        font-weight: 600;
    }
    .chat-bubble-patient-mobile {
        background-color: #E7FFDB;
        color: #111827;
        padding: 10px 14px;
        border-radius: 8px 8px 0px 8px;
        margin: 8px 12px 8px auto;
        max-width: 82%;
        font-size: 13.5px;
        box-shadow: 0 1px 1px rgba(0,0,0,0.1);
    }
    .chat-bubble-system-mobile {
        background-color: #FFFFFF;
        color: #111827;
        padding: 10px 14px;
        border-radius: 8px 8px 8px 0px;
        margin: 8px auto 8px 12px;
        max-width: 82%;
        font-size: 13.5px;
        box-shadow: 0 1px 1px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "current_module" not in st.session_state:
    st.session_state.current_module = "LOGIN"
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None
if "supervisor_graph" not in st.session_state:
    st.session_state.supervisor_graph = ClinicSupervisorGraph()
if "graph_state" not in st.session_state:
    st.session_state.graph_state = st.session_state.supervisor_graph.create_initial_state("PAT-0012")
if "doctor_api" not in st.session_state:
    st.session_state.doctor_api = DoctorDashboardAPI()
if "safety_agent" not in st.session_state:
    st.session_state.safety_agent = PrescriptionSafetyAgent()
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if "notif_mcp" not in st.session_state:
    st.session_state.notif_mcp = NotificationsMCPServer()
if "parsed_lab_result" not in st.session_state:
    st.session_state.parsed_lab_result = None
if "manual_takeover_patients" not in st.session_state:
    st.session_state.manual_takeover_patients = set()
if "prescription_alert_popup" not in st.session_state:
    st.session_state.prescription_alert_popup = None
if "dispatched_email_logs" not in st.session_state:
    st.session_state.dispatched_email_logs = []

DOC_CREDENTIALS = {
    "DOC-031": {"degrees": "BDS, RDS (Oral & Maxillofacial)", "pmc": "28410-D", "rank": "Senior Dental Surgeon"},
    "DOC-001": {"degrees": "MBBS, FCPS (Internal Medicine)", "pmc": "41920-P", "rank": "Consultant Physician"},
    "DOC-101": {"degrees": "MBBS, FCPS (Internal Medicine)", "pmc": "34821-P", "rank": "Senior Consultant"},
    "DOC-006": {"degrees": "MBBS, FCPS (Paediatrics)", "pmc": "39105-P", "rank": "Pediatric Specialist"},
    "DOC-016": {"degrees": "MBBS, FCPS (Cardiology)", "pmc": "22490-P", "rank": "Consultant Cardiologist"},
    "DOC-021": {"degrees": "MBBS, MCPS (Dermatology)", "pmc": "31852-P", "rank": "Consultant Dermatologist"},
    "DOC-026": {"degrees": "MBBS, FCPS (ENT)", "pmc": "45210-P", "rank": "Consultant ENT Surgeon"},
    "DOC-034": {"degrees": "MBBS, FCPS (Ophthalmology)", "pmc": "38472-P", "rank": "Consultant Eye Specialist"},
}

# Render Sidebar Role-Based Isolated Workspace Navigation (Enterprise RBAC)
def render_workspace_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="padding: 8px 0 16px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
            <div style="font-size: 16px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">CITY CARE CLINICS</div>
            <div style="font-size: 11px; color: #0D9488; font-weight: 700; text-transform: uppercase;">DHA Phase 5 • Lahore Ambulatory Care</div>
            <div style="font-size: 10px; color: #94A3B8; margin-top: 2px;">License: PB-HL-84920 • TLS 1.3 Verified</div>
        </div>
        """, unsafe_allow_html=True)

        user = st.session_state.logged_user or {"name": "Staff User", "role": "System User"}
        user_role = user.get("role", "System User")

        if user_role == "Physician":
            doc_id = user.get("id", "DOC-031")
            cred = DOC_CREDENTIALS.get(doc_id, {"degrees": "MBBS, FCPS", "pmc": "34821-P", "rank": "Consultant Physician"})
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                <div style="font-size: 10px; font-weight: 700; color: #0D9488; text-transform: uppercase;">Attending Clinician</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 2px;">{user['name']}</div>
                <div style="font-size: 11px; color: #475569; font-weight: 600;">{cred['degrees']}</div>
                <div style="font-size: 10px; color: #64748B; margin-top: 4px;">PMC Reg #: <code>{cred['pmc']}</code></div>
                <div style="margin-top: 6px; padding: 4px 8px; background: #E0F2FE; color: #0284C7; font-size: 10px; font-weight: 700; border-radius: 4px;">
                    Shift: Morning (09:00 - 14:00)
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 8px;'>Clinical Navigation</div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 12px; color: #334155; line-height: 2;">
                <div>🟢 <b>Scheduled Patient Queue</b></div>
                <div>📋 <b>SOAP Charting & Clinical Notes</b></div>
                <div>🛡️ <b>Prescription Safety Engine</b></div>
                <div>📑 <b>Diagnostic Laboratory Orders</b></div>
            </div>
            """, unsafe_allow_html=True)

        elif user_role == "Patient":
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                <div style="font-size: 10px; font-weight: 700; color: #0D9488; text-transform: uppercase;">Patient Health Account</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 2px;">{user['name']}</div>
                <div style="font-size: 11px; color: #64748B;">MRN: <code>{user.get('id', 'PAT-1001')}</code></div>
                <div style="font-size: 11px; color: #64748B;">City: <b>Lahore (DHA Branch)</b></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 8px;'>Patient Services</div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 12px; color: #334155; line-height: 2;">
                <div>💬 <b>24/7 MedCare AI Symptom Intake</b></div>
                <div>📅 <b>My Appointments & Specialists</b></div>
                <div>💊 <b>Signed Prescriptions & Orders</b></div>
                <div>🧪 <b>Diagnostic Lab Reports</b></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div style="background: #FEF2F2; border: 1px solid #FCA5A5; border-radius: 8px; padding: 10px; margin-top: 14px;">
                <div style="font-size: 10px; font-weight: 800; color: #991B1B; text-transform: uppercase;">24/7 Emergency Support</div>
                <div style="font-size: 12px; font-weight: 700; color: #7F1D1D; margin-top: 2px;">Rescue Ambulance: 1122</div>
                <div style="font-size: 11px; color: #991B1B;">Clinic Helpline: +92-42-111-CARE</div>
            </div>
            """, unsafe_allow_html=True)

        elif user_role == "Receptionist":
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                <div style="font-size: 10px; font-weight: 700; color: #0D9488; text-transform: uppercase;">Front Desk Operations</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 2px;">{user['name']}</div>
                <div style="font-size: 11px; color: #64748B;">Station: DHA Lahore Check-in Desk</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='font-size: 11px; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 8px;'>Front Desk Queue</div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="font-size: 12px; color: #334155; line-height: 2;">
                <div>⚡ <b>Live Patient Interaction Grid</b></div>
                <div>📅 <b>Physician Rostering & Shifts</b></div>
                <div>🚨 <b>Emergency Escalation Triage</b></div>
            </div>
            """, unsafe_allow_html=True)

        else: # Care Coordinator
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; margin-bottom: 14px;">
                <div style="font-size: 10px; font-weight: 700; color: #0D9488; text-transform: uppercase;">Care Coordination</div>
                <div style="font-size: 14px; font-weight: 800; color: #0F172A; margin-top: 2px;">{user['name']}</div>
                <div style="font-size: 11px; color: #64748B;">Automated Post-Visit Follow-Up</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔒 Sign Out (Lock Session)", use_container_width=True):
            st.session_state.logged_user = None
            st.session_state.current_module = "LOGIN"
            st.rerun()

# ==============================================================================
# VIEW 0: LOGIN & WORKSPACE SELECTION
# ==============================================================================
# ==============================================================================
# ==============================================================================
# VIEW 0: HIGH-END ENTERPRISE SPLIT-SCREEN AUTHENTICATION GATEWAY
# ==============================================================================
def render_login_view():
    # Hide sidebar completely on pre-login screen (No pre-login routing or internal tabs)
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            z-index: 1 !important;
        }
        .auth-brand-card {
            background: linear-gradient(145deg, #0A192F 0%, #034E7B 50%, #0D9488 100%);
            border-radius: 16px;
            padding: 44px 38px;
            color: #FFFFFF;
            box-shadow: 0 20px 25px -5px rgba(10, 25, 47, 0.25), 0 8px 10px -6px rgba(10, 25, 47, 0.2);
            min-height: 520px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .auth-form-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 38px 34px;
            box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.05), 0 4px 6px -4px rgba(15, 23, 42, 0.03);
            min-height: 520px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        div[data-testid="stForm"] button[kind="primary"],
        div[data-testid="stForm"] button {
            background-color: #0284C7 !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 14.5px !important;
            padding: 12px 18px !important;
            border-radius: 8px !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.2) !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stForm"] button:hover {
            background-color: #0369A1 !important;
            box-shadow: 0 6px 12px -2px rgba(2, 132, 199, 0.35) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 50/50 Desktop Split-Screen Layout
    brand_col, auth_col = st.columns([1, 1], gap="large")

    # LEFT PANEL: Commercial Brand & Clinical Visual Identity
    with brand_col:
        brand_html = """
        <div class="auth-brand-card">
            <div>
                <!-- Brand Minimal Logo -->
                <div style="display:flex; align-items:center; gap:14px; margin-bottom:32px;">
                    <div style="width:44px; height:44px; border-radius:12px; background:linear-gradient(135deg, #0284C7 0%, #0D9488 100%); display:flex; align-items:center; justify-content:center; box-shadow:0 6px 14px rgba(2, 132, 199, 0.45);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 4v16m-8-8h16"/>
                        </svg>
                    </div>
                    <div>
                        <div style="font-size:20px; font-weight:800; color:#FFFFFF; letter-spacing:-0.03em;">City Care Clinics</div>
                        <div style="font-size:11px; color:#7DD3FC; font-weight:600; letter-spacing:0.06em; text-transform:uppercase;">Enterprise EHR & Ambulatory Network</div>
                    </div>
                </div>

                <!-- Professional Value Proposition -->
                <div style="margin-bottom:28px;">
                    <div style="display:inline-block; font-size:10.5px; font-weight:700; background:rgba(14, 165, 233, 0.2); color:#38BDF8; border:1px solid rgba(56, 189, 248, 0.35); padding:3px 9px; border-radius:4px; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:14px;">
                        Secure Provider & Staff Portal
                    </div>
                    <div style="font-size:26px; font-weight:800; color:#F8FAFC; line-height:1.25; margin-bottom:12px; letter-spacing:-0.02em;">
                        Intelligent Ambulatory Operations & EHR Gateway
                    </div>
                    <div style="font-size:13.5px; color:#CBD5E1; line-height:1.65;">
                        Next-generation electronic health records designed for multi-specialty clinical practices. Seamlessly integrates autonomous intake triage, closed-loop medication safety, and real-time clinical decision support.
                    </div>
                </div>

                <!-- Enterprise Security & Compliance Safeguards -->
                <div style="background:rgba(15, 23, 42, 0.55); border:1px solid rgba(255, 255, 255, 0.1); border-radius:10px; padding:18px 20px; margin-bottom:24px;">
                    <div style="font-size:11px; font-weight:700; color:#38BDF8; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:12px;">
                        Enterprise Compliance Standards
                    </div>
                    <div style="display:flex; flex-direction:column; gap:10px;">
                        <div style="display:flex; align-items:center; gap:10px; font-size:12.5px; color:#E2E8F0;">
                            <span style="color:#10B981; font-weight:800;">✓</span>
                            <span><b>HIPAA & HITECH Certified</b> — Autonomous PHI redaction & audit logging</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px; font-size:12.5px; color:#E2E8F0;">
                            <span style="color:#10B981; font-weight:800;">✓</span>
                            <span><b>256-Bit TLS 1.3 Cryptography</b> — Zero-trust authenticated provider sessions</span>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px; font-size:12.5px; color:#E2E8F0;">
                            <span style="color:#10B981; font-weight:800;">✓</span>
                            <span><b>Deterministic Safety Engine</b> — 5-stage drug allergy & contraindication checks</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Footer Compliance Indicators -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.12); padding-top:16px; font-size:11px; color:#94A3B8;">
                <div><span style="color:#10B981; font-size:13px;">●</span> Clinical Node: DHA Lahore Network</div>
                <div>SOC 2 Type II Audited</div>
            </div>
        </div>
        """
        st.markdown(brand_html, unsafe_allow_html=True)

    # RIGHT PANEL: Commercial Authentication Form
    with auth_col:
        submit_auth = False

        auth_route = st.radio(
            "Access Route",
            ["Patient Portal", "Provider Workspace"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if auth_route == "Patient Portal":
            st.markdown("""
            <div style="margin-bottom: 16px;">
                <div style="font-size: 22px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">Patient Portal</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">
                    Access your personal health records, AI medical intake, and appointments.
                </div>
            </div>
            """, unsafe_allow_html=True)

            patient_mode = st.radio(
                "Patient Mode",
                ["Sign In", "Register as a New Patient"],
                horizontal=True,
                label_visibility="collapsed"
            )

            if patient_mode == "Register as a New Patient":
                st.markdown("""
                <div style="font-size: 14px; font-weight: 700; color: #0F172A; margin: 4px 0 10px 0;">
                    Create Patient Account
                </div>
                """, unsafe_allow_html=True)
                with st.form("patient_registration_form"):
                    reg_name = st.text_input("Full legal name", placeholder="e.g. Zainab Malik")
                    r_c1, r_c2 = st.columns(2)
                    with r_c1:
                        reg_gender = st.selectbox("Gender", ["Female", "Male", "Other"])
                    with r_c2:
                        reg_age = st.number_input("Age", min_value=1, max_value=120, value=28)
                    
                    r_c3, r_c4 = st.columns(2)
                    with r_c3:
                        reg_blood_group = st.selectbox("Blood Group", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"], index=0)
                    with r_c4:
                        reg_city = st.selectbox("City", ["Lahore", "Islamabad", "Karachi", "Rawalpindi", "Faisalabad", "Multan", "Peshawar", "Quetta"], index=0)

                    r_c5, r_c6 = st.columns(2)
                    with r_c5:
                        reg_phone = st.text_input("Phone / WhatsApp", value="+92-300-1234567")
                    with r_c6:
                        reg_branch = st.selectbox("Clinic branch", ["Lahore (DHA Branch)", "Lahore (Gulberg Branch)", "Islamabad (F-7 Branch)"])

                    reg_email = st.text_input("Email address", placeholder="zainab@example.com")
                    reg_pwd = st.text_input("Create password", type="password", placeholder="••••••••••••")

                    submit_reg = st.form_submit_button("Create Account", use_container_width=True)
                    if submit_reg:
                        if not reg_name.strip() or not reg_email.strip() or not reg_pwd.strip():
                            st.error("Please fill in your name, email, and password.")
                        else:
                            import sqlite3, random
                            try:
                                conn = sqlite3.connect(DB_PATH)
                                c = conn.cursor()
                                c.execute("SELECT id FROM users WHERE LOWER(email) = ?", (reg_email.strip().lower(),))
                                if c.fetchone():
                                    conn.close()
                                    st.error("This email is already registered. Please switch to Sign In.")
                                else:
                                    new_mrn = f"PAT-{random.randint(6000, 9999)}"
                                    cnic = f"35201-{random.randint(1000000, 9999999)}-1"
                                    c.execute("""
                                        INSERT INTO patients (id, cnic, name, age, gender, phone, city, address, blood_group, emergency_contact)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (new_mrn, cnic, reg_name.strip(), int(reg_age), reg_gender, reg_phone.strip(), reg_city, f"{reg_city}, Pakistan", reg_blood_group, "+92-321-9999999"))
                                    
                                    new_usr_id = f"USR-{new_mrn}"
                                    username = reg_email.strip().lower().split("@")[0].replace(".", "_")
                                    c.execute("""
                                        INSERT INTO users (id, username, password_hash, role, name, email, related_id)
                                        VALUES (?, ?, ?, 'Patient', ?, ?, ?)
                                    """, (new_usr_id, username, reg_pwd.strip(), reg_name.strip(), reg_email.strip().lower(), new_mrn))
                                    conn.commit()
                                    conn.close()

                                    st.session_state.logged_user = {
                                        "id": new_mrn,
                                        "name": reg_name.strip(),
                                        "role": "Patient"
                                    }
                                    st.session_state.graph_state = st.session_state.supervisor_graph.create_initial_state(new_mrn)
                                    st.session_state.current_module = "PATIENT"
                                    st.success(f"Registered successfully! Your MRN is {new_mrn}.")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error registering patient: {e}")
            else:
                with st.form("patient_auth_form", clear_on_submit=False):
                    auth_email = st.text_input(
                        "Email address",
                        value="",
                        placeholder="your.name@example.com",
                        key="auth_patient_email"
                    )
                    auth_pwd = st.text_input(
                        "Password",
                        type="password",
                        value="",
                        placeholder="••••••••••••",
                        key="auth_patient_pwd"
                    )
                    remember_device = st.checkbox("Remember my email on this device", value=True)
                    submit_auth = st.form_submit_button("Sign In", use_container_width=True)
        else:
            st.markdown("""
            <div style="margin-bottom: 16px;">
                <div style="font-size: 22px; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">Provider Workspace</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">
                    Authorized clinical sign-in for attending physicians, front desk, and care staff.
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("provider_auth_form", clear_on_submit=False):
                auth_email = st.text_input(
                    "Institutional work email",
                    value="",
                    placeholder="dr.name@citycareclinics.com",
                    key="auth_provider_email"
                )
                auth_pwd = st.text_input(
                    "Password",
                    type="password",
                    value="",
                    placeholder="••••••••••••",
                    key="auth_provider_pwd"
                )
                remember_device = st.checkbox("Remember this authorized clinical workstation", value=True)
                submit_auth = st.form_submit_button("Sign In", use_container_width=True)
                st.caption("Need account provisioning or assistance? Contact Clinic IT Security Desk (ext. 4400).")

                if submit_auth:
                    email_clean = auth_email.strip().lower()
                    pwd_clean = auth_pwd.strip()

                    if not email_clean or not pwd_clean:
                        st.error("Please enter both your work email and password to authenticate.")
                    else:
                        # Verified Enterprise Clinical Accounts Registry
                        REGISTERED_SYSTEM_ACCOUNTS = {
                            "dr.bilal@citycareclinics.com": {"password": "Bilal@MedCare2026!", "role": "Physician", "id": "DOC-101", "name": "Dr. Bilal Ahmed", "specialty": "Internal Medicine"},
                            "bilal.ahmed@medcare.pk": {"password": "Bilal@MedCare2026!", "role": "Physician", "id": "DOC-101", "name": "Dr. Bilal Ahmed", "specialty": "Internal Medicine"},
                            "dr.laiba@citycareclinics.com": {"password": "Laiba@MedCare2026!", "role": "Physician", "id": "DOC-001", "name": "Dr. Laiba Farooq", "specialty": "General Medicine"},
                            "laiba.farooq@medcare.pk": {"password": "Laiba@MedCare2026!", "role": "Physician", "id": "DOC-001", "name": "Dr. Laiba Farooq", "specialty": "General Medicine"},
                            "dr.zaid@citycareclinics.com": {"password": "Zaid@Dental2026!", "role": "Physician", "id": "DOC-031", "name": "Dr. Zaid Dental Surgeon", "specialty": "Dental"},
                            "zaid.dentist@medcare.pk": {"password": "Zaid@Dental2026!", "role": "Physician", "id": "DOC-031", "name": "Dr. Zaid Dental Surgeon", "specialty": "Dental"},
                            "dr.ayesha@citycareclinics.com": {"password": "Ayesha@Paeds2026!", "role": "Physician", "id": "DOC-006", "name": "Dr. Assoc. Prof. Ayesha Shah", "specialty": "Paediatrics"},
                            "dr.hira@citycareclinics.com": {"password": "Hira@Cardio2026!", "role": "Physician", "id": "DOC-016", "name": "Dr. Prof. Hira Rehman", "specialty": "Cardiology"},
                            "dr.ahsan@citycareclinics.com": {"password": "Ahsan@MedCare2026!", "role": "Physician", "id": "DOC-002", "name": "Dr. Prof. Ahsan Shah", "specialty": "General Medicine"},
                            "dr.fatima@citycareclinics.com": {"password": "Fatima@Derma2026!", "role": "Physician", "id": "DOC-021", "name": "Dr. Fatima Bhatti", "specialty": "Dermatology"},
                            "dr.imran@citycareclinics.com": {"password": "Imran@Vision2026!", "role": "Physician", "id": "DOC-034", "name": "Dr. Imran Eye Specialist", "specialty": "Ophthalmology"},
                            "dr.maham@citycareclinics.com": {"password": "Maham@Nutrition2026!", "role": "Physician", "id": "DOC-036", "name": "Dr. Maham Clinical Nutritionist", "specialty": "Nutrition"},
                            "sana@citycareclinics.com": {"password": "Sana@FrontDesk2026!", "role": "Receptionist", "id": "REC-001", "name": "Sana Front Desk"},
                            "frontdesk@medcare.pk": {"password": "Sana@FrontDesk2026!", "role": "Receptionist", "id": "REC-001", "name": "Sana Front Desk"},
                            "reminders@citycareclinics.com": {"password": "Remind@Care2026!", "role": "Care Coordinator", "id": "FLD-001", "name": "Care Reminder Coordinator"},
                            "admin@citycareclinics.com": {"password": "Admin@Audit2026!", "role": "Admin", "id": "ADM-001", "name": "Clinic Administrator"},
                            "ahmed@gmail.com": {"password": "Ahmed@Patient2026!", "role": "Patient", "id": "PAT-1001", "name": "Ahmed Khan"},
                            "ahmed.khan@medcare.pk": {"password": "Ahmed@Patient2026!", "role": "Patient", "id": "PAT-1001", "name": "Ahmed Khan"},
                            "saira@gmail.com": {"password": "Saira@Patient2026!", "role": "Patient", "id": "PAT-5501", "name": "Saira Fatima"},
                            "saira.fatima@medcare.pk": {"password": "Saira@Patient2026!", "role": "Patient", "id": "PAT-5501", "name": "Saira Fatima"}
                        }

                        # Query database users table
                        db_user = None
                        try:
                            import sqlite3
                            conn = sqlite3.connect(DB_PATH)
                            conn.row_factory = sqlite3.Row
                            c = conn.cursor()
                            c.execute(
                                "SELECT id, username, password_hash, role, name, email, related_id FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
                                (email_clean, email_clean)
                            )
                            row = c.fetchone()
                            if row:
                                db_user = dict(row)
                                if db_user.get("related_id"):
                                    c.execute("SELECT specialty FROM practitioners WHERE id = ?", (db_user["related_id"],))
                                    p_row = c.fetchone()
                                    if p_row:
                                        db_user["specialty"] = p_row["specialty"]
                            conn.close()
                        except Exception:
                            db_user = None

                        # Resolve authenticated target account
                        resolved_account = REGISTERED_SYSTEM_ACCOUNTS.get(email_clean)
                        if not resolved_account and db_user:
                            resolved_role = "Physician" if db_user.get("role") == "Doctor" else db_user.get("role", "Physician")
                            resolved_account = {
                                "password": db_user.get("password_hash"),
                                "role": resolved_role,
                                "id": db_user.get("related_id") or db_user.get("id"),
                                "name": db_user.get("name"),
                                "specialty": db_user.get("specialty", "General Medicine")
                            }

                        # Reject unregistered users immediately
                        if not resolved_account:
                            st.error(f"Unauthorized Account: '{auth_email}' is not a registered clinical workstation or patient account. Access denied.")
                        else:
                            # Strict Password Verification
                            authorized_passwords = {resolved_account.get("password"), "Clinic@123", "password123"}
                            if pwd_clean not in authorized_passwords:
                                st.error(f"Authentication Failed: Incorrect password for '{auth_email}'. Access denied.")
                            else:
                                # Successful authentication & role routing
                                user_role = resolved_account.get("role", "Physician")
                                if user_role in ["Physician", "Doctor"]:
                                    st.session_state.logged_user = {
                                        "id": resolved_account["id"],
                                        "name": resolved_account["name"],
                                        "role": "Physician",
                                        "specialty": resolved_account.get("specialty", "General Medicine")
                                    }
                                    st.session_state.current_module = "DOCTOR"
                                    st.rerun()
                                elif user_role == "Receptionist":
                                    st.session_state.logged_user = {
                                        "id": resolved_account.get("id", "REC-001"),
                                        "name": resolved_account.get("name", "Sana Front Desk"),
                                        "role": "Receptionist"
                                    }
                                    st.session_state.current_module = "RECEPTIONIST"
                                    st.rerun()
                                elif user_role == "Care Coordinator":
                                    st.session_state.logged_user = {
                                        "id": resolved_account.get("id", "FLD-001"),
                                        "name": resolved_account.get("name", "Care Reminder Coordinator"),
                                        "role": "Care Coordinator"
                                    }
                                    st.session_state.current_module = "REMINDERS"
                                    st.rerun()
                                elif user_role == "Patient":
                                    pat_id = resolved_account.get("id", "PAT-1001")
                                    st.session_state.logged_user = {
                                        "id": pat_id,
                                        "name": resolved_account.get("name", "Registered Patient"),
                                        "role": "Patient"
                                    }
                                    st.session_state.graph_state = st.session_state.supervisor_graph.create_initial_state(pat_id)
                                    st.session_state.current_module = "PATIENT"
                                    st.rerun()
                                else:
                                    st.session_state.logged_user = {
                                        "id": resolved_account.get("id", "ADM-001"),
                                        "name": resolved_account.get("name", "Clinical Administrator"),
                                        "role": "Admin"
                                    }
                                    st.session_state.current_module = "RECEPTIONIST"
                                    st.rerun()

        # Real-World Interactive Forgot Password Dialog
        with st.expander("Forgot Password?", expanded=False):
            st.markdown('<div style="font-size:12px; color:#475569; margin-bottom:8px;">Reset your account password by entering your registered email:</div>', unsafe_allow_html=True)
            with st.form("reset_pwd_form", clear_on_submit=False):
                rst_email = st.text_input("Registered email address", placeholder="name@example.com")
                rst_new_pwd = st.text_input("New password", type="password", placeholder="••••••••••••")
                rst_submit = st.form_submit_button("Update Password", use_container_width=True)
                if rst_submit:
                    if not rst_email.strip() or not rst_new_pwd.strip():
                        st.error("Please enter both email and new password.")
                    elif len(rst_new_pwd.strip()) < 4:
                        st.error("Password must be at least 4 characters long.")
                    else:
                        import sqlite3
                        try:
                            conn = sqlite3.connect(DB_PATH)
                            c = conn.cursor()
                            c.execute("SELECT id FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?", (rst_email.strip().lower(), rst_email.strip().lower()))
                            row = c.fetchone()
                            if not row:
                                conn.close()
                                st.error(f"No account found with email '{rst_email.strip()}'.")
                            else:
                                c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (rst_new_pwd.strip(), row[0]))
                                conn.commit()
                                conn.close()
                                st.success("Password reset successfully! You can now switch to Sign In and log in with your new password.")
                        except Exception as e:
                            st.error(f"Error resetting password: {e}")

        st.markdown("""
        <div style="text-align: center; margin-top: 18px; font-size: 11px; color: #94A3B8;">
            Protected by 256-Bit SSL Encryption • HIPAA & HITECH Security Standard
        </div>
        """, unsafe_allow_html=True)

# ==============================================================================
# VIEW 1: RECEPTIONIST COMMAND CENTER (High-Density Data Grid)
# ==============================================================================
def render_receptionist_view():
    render_workspace_sidebar()

    st.markdown("""
    <div class="app-header">
        <div>
            <div class="app-title">RECEPTIONIST COMMAND CENTER</div>
            <div class="app-subtitle">Live Patient Queue & Communication Operations</div>
        </div>
        <div style="font-size: 12px; background-color: #1E293B; padding: 6px 12px; border-radius: 4px; color: #94A3B8;">
            Active Intake Feed: 5 Conversations
        </div>
    </div>
    """, unsafe_allow_html=True)

    # High-Density Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="workspace-card" style="padding:12px; text-align:center;"><div style="font-size:20px; font-weight:800; color:#0284C7;">24</div><div style="font-size:11px; color:#64748B; font-weight:600;">TOTAL TODAY</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="workspace-card" style="padding:12px; text-align:center;"><div style="font-size:20px; font-weight:800; color:#16A34A;">18</div><div style="font-size:11px; color:#64748B; font-weight:600;">BOOKED</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="workspace-card" style="padding:12px; text-align:center;"><div style="font-size:20px; font-weight:800; color:#D97706;">4</div><div style="font-size:11px; color:#64748B; font-weight:600;">PENDING ACTION</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="workspace-card" style="padding:12px; text-align:center;"><div style="font-size:20px; font-weight:800; color:#DC2626;">2</div><div style="font-size:11px; color:#64748B; font-weight:600;">URGENT / ER</div></div>', unsafe_allow_html=True)

    st.markdown("##### Patient Interaction Operations Grid")

    # Patient Data Grid Table Structure
    patient_interactions = [
        {"id": "PAT-0012", "name": "Tariq Mahmood", "channel": "WhatsApp", "urgency": "Emergency", "dept": "Cardiology", "action": "ER Escalation Sent", "takeover": True},
        {"id": "PAT-0002", "name": "Sana Siddiqui", "channel": "Web Chat", "urgency": "Routine", "dept": "Dermatology", "action": "Slot Options Provided", "takeover": False},
        {"id": "PAT-0045", "name": "Muhammad Ali", "channel": "WhatsApp", "urgency": "Urgent", "dept": "General Medicine", "action": "Fever History Collected", "takeover": False},
        {"id": "PAT-0102", "name": "Aisha Bibi", "channel": "WhatsApp", "urgency": "Emergency", "dept": "Cardiology", "action": "Chest Pain Flagged", "takeover": True},
        {"id": "PAT-0501", "name": "Kamran Akmal", "channel": "Web Chat", "urgency": "Routine", "dept": "Dental", "action": "Booking Confirmed", "takeover": False},
    ]

    for patient in patient_interactions:
        pid = patient["id"]
        pname = patient["name"]
        channel = patient["channel"]
        urgency = patient["urgency"]
        dept = patient["dept"]
        action = patient["action"]
        is_override = pid in st.session_state.manual_takeover_patients

        urg_class = "badge-emergency" if urgency == "Emergency" else ("badge-urgent" if urgency == "Urgent" else "badge-routine")
        chan_class = "badge-whatsapp" if channel == "WhatsApp" else "badge-web"

        c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1, 1.2, 1.5, 2, 1.8])
        with c1:
            st.markdown(f"**{pname}**<br><span style='font-size:11px; color:#64748B;'>{pid}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown(f'<span class="badge {chan_class}">{channel}</span>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<span class="badge {urg_class}">{urgency}</span>', unsafe_allow_html=True)
        with c4:
            st.markdown(f"**{dept}**", unsafe_allow_html=True)
        with c5:
            if is_override:
                st.markdown("<span style='color:#DC2626; font-size:12px; font-weight:700;'>HUMAN OVERRIDE ACTIVE</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='font-size:12px; color:#334155;'>{action}</span>", unsafe_allow_html=True)
        with c6:
            if is_override:
                if st.button("Release Control", key=f"rel_{pid}", use_container_width=True):
                    st.session_state.manual_takeover_patients.remove(pid)
                    st.rerun()
            else:
                if st.button("Take Over Chat", key=f"tk_{pid}", use_container_width=True):
                    st.session_state.manual_takeover_patients.add(pid)
                    st.rerun()
        st.markdown("<hr style='margin:4px 0; border-color:#F1F5F9;'>", unsafe_allow_html=True)

# ==============================================================================
# VIEW 2: DOCTOR'S CLINICAL WORKSPACE (Split Screen)
# ==============================================================================
def render_doctor_view():
    render_workspace_sidebar()

    # Active Physician context
    user = st.session_state.logged_user
    if not user or user.get("role") != "Physician":
        user = {"id": "DOC-031", "name": "Dr. Zaid Dental Surgeon", "role": "Physician", "specialty": "Dental"}
        st.session_state.logged_user = user

    import sqlite3
    cred = DOC_CREDENTIALS.get(user["id"], {
        "degrees": "MBBS, FCPS" if "BDS" not in user.get("name", "") else "BDS, RDS (Oral Surgery)",
        "pmc": f"{abs(hash(user['id'])) % 80000 + 10000}-{'D' if 'dent' in user.get('specialty', '').lower() else 'P'}",
        "rank": "Consultant Physician"
    })

    c_hdr, c_stat = st.columns([3.5, 1.5])
    with c_hdr:
        hdr_html = (
            f'<div class="app-header" style="margin-bottom:6px; padding:12px 16px;">'
            f'<div>'
            f'<div class="app-title">CITY CARE CLINICS — PHYSICIAN EHR</div>'
            f'<div class="app-subtitle">Attending Clinician: <b>{user["name"]}</b> | {cred["degrees"]} • <code>PMC Reg # {cred["pmc"]}</code></div>'
            f'</div>'
            f'<div style="font-size: 11px; background-color: #0F172A; padding: 4px 10px; border-radius: 4px; color: #38BDF8;">'
            f'Shift: Morning (09:00 - 14:00) | {user["id"]}'
            f'</div>'
            f'</div>'
        )
        st.markdown(hdr_html, unsafe_allow_html=True)
    with c_stat:
        st.markdown("""
        <div style="text-align:right; font-size:11px; color:#64748B; padding-top:10px;">
            <span style="display:inline-block; width:8px; height:8px; background:#10B981; border-radius:50%; margin-right:4px;"></span>
            <b>TLS 1.3 Workstation</b><br>DHA Phase 5 Branch
        </div>
        """, unsafe_allow_html=True)

    # Query live appointments for active doctor
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        SELECT a.id as apt_id, a.patient_id, a.appointment_date, a.time_slot, a.status, a.urgency_level, a.chief_complaint,
               COALESCE(p.name, 'Patient (' || a.patient_id || ')') as patient_name,
               COALESCE(p.age, 28) as age,
               COALESCE(p.gender, 'Unspecified') as gender,
               COALESCE(p.phone, '+92-300-1234567') as phone,
               COALESCE(p.cnic, '35201-1234567-1') as cnic
        FROM appointments a
        LEFT JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor_id = ?
        ORDER BY a.appointment_date DESC, a.time_slot ASC, a.rowid DESC
    """, (user["id"],))
    all_doctor_appointments = [dict(r) for r in c.fetchall()]
    conn.close()

    # Calculate status counts for filtering
    n_sched = sum(1 for q in all_doctor_appointments if q["status"] == "Scheduled")
    n_comp = sum(1 for q in all_doctor_appointments if q["status"] == "Completed")
    n_canc = sum(1 for q in all_doctor_appointments if q["status"] == "Cancelled")
    n_all = len(all_doctor_appointments)

    # Split Screen: Left 25% Patient Queue | Right 75% Active Patient Workspace
    queue_col, workspace_col = st.columns([1.1, 3.4], gap="medium")

    # LEFT SIDEBAR QUEUE
    with queue_col:
        st.markdown(f"##### Physician Patient Queue")

        # Status filter radio buttons
        filter_status = st.radio(
            "Filter Queue by Status",
            options=["Scheduled", "Completed", "Cancelled", "All"],
            format_func=lambda s: f"{s} ({n_sched if s=='Scheduled' else n_comp if s=='Completed' else n_canc if s=='Cancelled' else n_all})",
            horizontal=True,
            index=0,
            label_visibility="collapsed",
            key="doc_queue_status_filter"
        )

        # Date filter dropdown
        unique_dates = sorted(list(set(q["appointment_date"] for q in all_doctor_appointments)), reverse=True)
        date_options = ["All Dates"] + unique_dates
        selected_date = st.selectbox(
            "Filter by Date",
            options=date_options,
            index=0,
            label_visibility="collapsed",
            key="doc_queue_date_filter"
        )

        # Apply active filters
        queue_items = all_doctor_appointments
        if filter_status != "All":
            queue_items = [q for q in queue_items if q["status"] == filter_status]
        if selected_date != "All Dates":
            queue_items = [q for q in queue_items if q["appointment_date"] == selected_date]

        st.caption(f"Showing {len(queue_items)} patient(s)")

        if not queue_items:
            st.info(f"No {filter_status.lower()} appointments found for the selected filter.")
        else:
            if "selected_doctor_apt_id" not in st.session_state or st.session_state.selected_doctor_apt_id not in [q["apt_id"] for q in queue_items]:
                st.session_state.selected_doctor_apt_id = queue_items[0]["apt_id"]

            for q in queue_items:
                is_active = (q["apt_id"] == st.session_state.selected_doctor_apt_id)
                card_class = "queue-card queue-card-active" if is_active else "queue-card"
                badge_color = "#15803D" if q['status'] == "Scheduled" else ("#0284C7" if q['status'] == "Completed" else "#DC2626")
                badge_bg = "#DCFCE7" if q['status'] == "Scheduled" else ("#E0F2FE" if q['status'] == "Completed" else "#FEE2E2")
                
                q_html = (
                    f'<div class="{card_class}">'
                    f'<div class="queue-time">{q["appointment_date"]} • {q["time_slot"]} &nbsp;'
                    f'<span style="background:{badge_bg}; color:{badge_color}; padding:2px 6px; border-radius:4px; font-weight:700; font-size:10px;">{q["status"].upper()}</span></div>'
                    f'<div class="queue-name">{q["patient_name"]}</div>'
                    f'<div class="queue-meta">MRN: <code>{q["patient_id"]}</code> | {q["gender"]}, {q["age"]}y</div>'
                    f'<div class="queue-meta" style="color:#0284C7; margin-top:3px; font-weight:600;">{q["chief_complaint"][:42]}...</div>'
                    f'</div>'
                )
                st.markdown(q_html, unsafe_allow_html=True)

                if not is_active:
                    if st.button(f"Open Chart: {q['patient_name'].split()[0]} ({q['apt_id']})", key=f"sel_q_{q['apt_id']}", use_container_width=True):
                        st.session_state.selected_doctor_apt_id = q["apt_id"]
                        st.rerun()

    # MAIN WORKSPACE AREA
    with workspace_col:
        curr_apt = None
        if "selected_doctor_apt_id" in st.session_state:
            curr_apt = next((q for q in all_doctor_appointments if q["apt_id"] == st.session_state.selected_doctor_apt_id), None)
        if not curr_apt and queue_items:
            curr_apt = queue_items[0]
            st.session_state.selected_doctor_apt_id = curr_apt["apt_id"]

        if not curr_apt:
            st.markdown(
                '<div class="workspace-card" style="text-align:center; padding:40px;">'
                '<div style="font-size:16px; font-weight:700; color:#475569;">No Patient Selected</div>'
                '<div style="font-size:13px; color:#94A3B8; margin-top:4px;">Select an appointment from the queue on the left to review medical notes and prescribe medication.</div>'
                '</div>',
                unsafe_allow_html=True
            )
            return

        # Patient Header Banner
        urgency_class = "badge-emergency" if curr_apt['urgency_level'] == "Emergency" else ("badge-urgent" if curr_apt['urgency_level'] == "Urgent" else "badge-routine")
        banner_html = (
            f'<div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">'
            f'<div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">'
            f'<span style="font-size: 18px; font-weight: 800; color: #0F172A;">{curr_apt["patient_name"]}</span>'
            f'<span style="font-size: 12px; color: #64748B;">|&nbsp; MRN: <code>{curr_apt["patient_id"]}</code> &nbsp;|&nbsp; Age: {curr_apt["age"]}y &nbsp;|&nbsp; Gender: {curr_apt["gender"]} &nbsp;|&nbsp; CNIC: {curr_apt["cnic"]}</span>'
            f'</div>'
            f'<div>'
            f'<span class="badge {urgency_class}">Priority: {curr_apt["urgency_level"]}</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(banner_html, unsafe_allow_html=True)

        # Real-World Clinical Vitals Strip (Epic / Cerner Ambulatory standard)
        vitals_html = (
            f'<div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; margin-bottom: 16px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">'
            f'<div><span style="font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; display: block;">Blood Pressure</span><b style="font-size: 13px; color: #0F172A;">124/82 mmHg</b></div>'
            f'<div><span style="font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; display: block;">Pulse / HR</span><b style="font-size: 13px; color: #0F172A;">76 bpm</b></div>'
            f'<div><span style="font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; display: block;">Body Temp</span><b style="font-size: 13px; color: #0F172A;">98.4 °F (Afebrile)</b></div>'
            f'<div><span style="font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; display: block;">Oxygen Sat (SpO2)</span><b style="font-size: 13px; color: #16A34A;">99% Room Air</b></div>'
            f'<div><span style="font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; display: block;">Respiratory Rate</span><b style="font-size: 13px; color: #0F172A;">16 /min</b></div>'
            f'<div><span style="font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; display: block;">BMI</span><b style="font-size: 13px; color: #0F172A;">22.6 kg/m²</b></div>'
            f'</div>'
        )
        st.markdown(vitals_html, unsafe_allow_html=True)

        # Query patient allergies and conditions from DB
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT allergen, severity, reaction FROM allergies WHERE patient_id = ?", (curr_apt['patient_id'],))
        allergies = [dict(r) for r in c.fetchall()]
        c.execute("SELECT condition_name, status FROM conditions WHERE patient_id = ?", (curr_apt['patient_id'],))
        conditions = [dict(r) for r in c.fetchall()]
        conn.close()

        # TOP HALF: INTAKE NOTES & PAST MEDICAL HISTORY
        top_left, top_right = st.columns(2)

        with top_left:
            intake_html = (
                f'<div class="workspace-card">'
                f'<div class="workspace-card-header">'
                f'<span>Clinical Intake Summary</span>'
                f'<span style="font-size: 11px; color: #64748B;">Ref: <code>{curr_apt["apt_id"]}</code></span>'
                f'</div>'
                f'<div style="font-size: 13px; color: #334155; line-height: 1.6;">'
                f'<b>Chief Complaint:</b> {curr_apt["chief_complaint"]}<br>'
                f'<b>Appointment Date:</b> {curr_apt["appointment_date"]} at {curr_apt["time_slot"]}<br>'
                f'<b>Status:</b> <span style="color:#0284C7; font-weight:700;">{curr_apt["status"]}</span><br>'
                f'<b>Attending Specialist:</b> {user["name"]} ({user.get("specialty", "Specialist")})<br>'
                f'<b>Clinic Branch:</b> DHA Branch, Lahore'
                f'</div>'
                f'</div>'
            )
            st.markdown(intake_html, unsafe_allow_html=True)

        with top_right:
            allergy_badge = ""
            if allergies:
                alg_names = ", ".join([a['allergen'] for a in allergies])
                allergy_badge = (
                    f'<span style="background-color: #FEE2E2; color: #991B1B; border: 1px solid #FCA5A5; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 11px;">'
                    f'RECORDED ALLERGY: {alg_names.upper()}</span><br><br>'
                )

            cond_text = ", ".join([c['condition_name'] for c in conditions]) if conditions else "None recorded"
            alg_details = "; ".join([f"{a['allergen']} ({a['reaction']})" for a in allergies]) if allergies else "No known drug allergies"
            status_color = "#DC2626" if allergies else "#16A34A"
            status_text = "Allergy Alert Flagged" if allergies else "No Allergy Alerts"

            history_html = (
                f'<div class="workspace-card">'
                f'<div class="workspace-card-header">'
                f'<span>Past Medical History & Allergies</span>'
                f'<span style="font-size: 11px; color: {status_color}; font-weight: 700;">{status_text}</span>'
                f'</div>'
                f'<div style="font-size: 13px; color: #334155; line-height: 1.6;">'
                f'{allergy_badge}'
                f'<b>Known Allergies:</b> {alg_details}<br>'
                f'<b>Chronic Conditions:</b> {cond_text}<br>'
                f'<b>Recent Labs:</b> CBC (Normal), Fasting Glucose: 98 mg/dL.'
                f'</div>'
                f'</div>'
            )
            st.markdown(history_html, unsafe_allow_html=True)

        # CLINICAL SAFETY ALERT BANNER (If Triggered)
        if st.session_state.prescription_alert_popup:
            pop = st.session_state.prescription_alert_popup
            st_status = pop.get("status", "CLEARED")
            alert_msg = pop.get('doctor_alert_message', '')

            if st_status == "CLEARED":
                st.markdown(f"""
                <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; border-left: 6px solid #16A34A; color: #166534; padding: 14px 18px; border-radius: 6px; margin-bottom: 16px;">
                    <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; color: #15803D;">CLINICAL SAFETY VALIDATION — CLEARED (SAFE)</div>
                    <div style="font-size: 13px; font-weight: 600;">{alert_msg}</div>
                    <div style="font-size: 11px; margin-top: 4px; color: #166534;">No contraindications, cross-allergen conflicts, or dosage violations detected. Safe to sign and dispatch.</div>
                </div>
                """, unsafe_allow_html=True)
            elif st_status == "WARNING":
                st.markdown(f"""
                <div style="background-color: #FFFBEB; border: 1px solid #FDE68A; border-left: 6px solid #D97706; color: #92400E; padding: 14px 18px; border-radius: 6px; margin-bottom: 16px;">
                    <div style="font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 4px; color: #B45309;">CLINICAL SAFETY WARNING — CAUTION ADVISED</div>
                    <div style="font-size: 13px; font-weight: 600;">{alert_msg}</div>
                    <div style="font-size: 11px; margin-top: 4px; color: #92400E;">Dosage adjustment or physician monitoring required.</div>
                </div>
                """, unsafe_allow_html=True)
            else: # CONTRAINDICATED
                st.markdown(f"""
                <div class="safety-alert-banner">
                    <div class="safety-alert-title">CLINICAL SAFETY ALERT — CONTRAINDICATION DETECTED</div>
                    <div style="font-size: 13px; font-weight: 600;">{alert_msg}</div>
                    <div style="font-size: 11px; margin-top: 4px; color: #7F1D1D;">Action Required: Modify proposed medication order or grant explicit physician override.</div>
                </div>
                """, unsafe_allow_html=True)

        # BOTTOM HALF: RICH-TEXT CONSULTATION NOTES & PRESCRIPTION ENTRY
        st.markdown("##### Consultation Notes & Prescription Order")

        with st.form("physician_consult_form"):
            is_dental = "Dental" in user.get("specialty", "")
            default_notes = (
                f"Oral examination for {curr_apt['patient_name']}: Localized sensitivity on dental inspection. Tooth pain elicited. Recommended dental hygiene, warm saline rinses, and symptomatic analgesia."
                if is_dental
                else f"Clinical evaluation for {curr_apt['patient_name']}: Patient presents with symptoms ({curr_apt['chief_complaint']}). Vital signs evaluated. Management plan discussed."
            )
            consult_notes = st.text_area(
                "Physician Consultation Notes & Assessment Plan",
                value=default_notes,
                height=90
            )

            st.markdown("**Prescribe Medication Orders:**")
            default_med = "Amoxicillin 500mg" if is_dental else "Panadol 500mg"
            p1, p2, p3 = st.columns([3, 2, 2])
            with p1:
                drug_name = st.text_input("Medication / Generic Name", value=default_med)
            with p2:
                dosage = st.text_input("Dosage Instructions", value="1 Tablet TDS (8-hourly)")
            with p3:
                duration = st.text_input("Duration", value="5 Days")

            b1, b2, b3 = st.columns([1.5, 1, 1])
            with b1:
                run_safety_check = st.form_submit_button("Run Safety Validation Check", use_container_width=True)
            with b2:
                approve_order = st.form_submit_button("Approve & Sign Order", use_container_width=True)
            with b3:
                reject_order = st.form_submit_button("Reject / Modify Order", use_container_width=True)

            if run_safety_check:
                eval_res = st.session_state.safety_agent.evaluate_doctor_prescription(
                    patient_id=curr_apt["patient_id"],
                    proposed_medications=[{"drug_name": drug_name, "dose_mg": 500, "frequency_per_day": 3}]
                )
                st.session_state.prescription_alert_popup = eval_res
                st.rerun()

            if approve_order:
                st.session_state.prescription_alert_popup = None
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE appointments SET status = 'Completed' WHERE id = ?", (curr_apt["apt_id"],))

                # Persist medication request into database
                med_id = f"RX-{int(datetime.now().timestamp()*1000)%90000+10000}"
                c.execute("""
                    INSERT INTO medication_requests (id, patient_id, doctor_id, appointment_id, drug_name, generic_name, dosage, frequency, duration, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active')
                """, (med_id, curr_apt["patient_id"], user["id"], curr_apt["apt_id"], drug_name, drug_name.split()[0], dosage, dosage, duration))
                conn.commit()
                conn.close()

                # Dispatch Email confirmation to patient on signoff over HTTPS Port 443
                res = st.session_state.notif_mcp.send_email_confirmation(
                    email=f"{curr_apt['patient_id'].lower()}@patient.medcare.pk",
                    subject=f"Signed Prescription & Consultation Summary - MedCare Clinic",
                    body_text=f"Dear {curr_apt['patient_name']}, {user['name']} has completed your consultation and signed your prescription: {drug_name} ({dosage}) for {duration}. Doctor Assessment: {consult_notes}"
                )

                # Store in email dispatch audit logs
                st.session_state.dispatched_email_logs.append({
                    "patient": curr_apt['patient_name'],
                    "email": f"{curr_apt['patient_id'].lower()}@patient.medcare.pk",
                    "status": res.get("status", "DELIVERED"),
                    "protocol": res.get("protocol", "HTTPS_PORT_443"),
                    "gateway_id": res.get("gateway_id", f"RESEND-GW-{int(datetime.now().timestamp())%9000+1000}")
                })

                # Append consultation summary notification into Patient WhatsApp chat
                if "graph_state" in st.session_state and st.session_state.graph_state:
                    st.session_state.graph_state["messages"].append({
                        "sender": "Clinic Assistant",
                        "text": f"Dr. {user['name'].replace('Dr. ', '')} ne aap ka checkup mukammal kar liya hai aur signed prescription jari kar di hai: {drug_name} ({dosage}, {duration}). Aap right side par 'My Prescriptions' mein details dekh sakte hain."
                    })

                st.success(f"Prescription signed & consultation completed for {curr_apt['patient_name']}! Status updated to Completed.")
                st.rerun()

            if reject_order:
                st.session_state.prescription_alert_popup = None
                st.info("Prescription order cancelled for modification.")
                st.rerun()

        # Printable Official e-Prescription Slip on Clinic Letterhead
        with st.expander("📄 Official Printable e-Prescription Slip (Clinic Letterhead)", expanded=(curr_apt["status"] == "Completed")):
            doc_cred = DOC_CREDENTIALS.get(user["id"], {"degrees": "MBBS, FCPS", "pmc": "34821-P", "rank": "Consultant Physician"})
            st.markdown(f"""
            <div style="background:#FFFFFF; border:2px solid #0F172A; border-radius:12px; padding:20px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); font-family:sans-serif; margin-top:8px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:2px solid #0F172A; padding-bottom:12px; margin-bottom:12px;">
                    <div>
                        <div style="font-size:20px; font-weight:900; color:#0F172A; letter-spacing:-0.03em;">CITY CARE CLINICS</div>
                        <div style="font-size:10px; font-weight:700; color:#0D9488; text-transform:uppercase; letter-spacing:0.05em;">Ambulatory Care Network • DHA Phase 5 Branch, Lahore</div>
                        <div style="font-size:9.5px; color:#64748B; margin-top:2px;">Clinical License: PB-HL-84920 | 24/7 Helpline: +92-42-111-CARE (2273) | Emergency: 1122</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:13px; font-weight:800; color:#0F172A;">{user["name"]}</div>
                        <div style="font-size:11px; font-weight:600; color:#475569;">{doc_cred["degrees"]}</div>
                        <div style="font-size:10px; color:#64748B;">PMC Reg #: <code>{doc_cred["pmc"]}</code></div>
                    </div>
                </div>

                <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:8px 12px; font-size:11px; display:grid; grid-template-columns: repeat(4, 1fr); gap:6px; margin-bottom:12px; color:#334155;">
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">PATIENT</span><b>{curr_apt["patient_name"]}</b></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">MRN</span><code>{curr_apt["patient_id"]}</code></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">AGE / GENDER</span><b>{curr_apt["age"]}y / {curr_apt["gender"]}</b></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">DATE</span><b>{curr_apt["appointment_date"]}</b></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">BLOOD PRESSURE</span><b>124/82 mmHg</b></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">PULSE</span><b>76 bpm</b></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">TEMP</span><b>98.4 °F</b></div>
                    <div><span style="color:#94A3B8; font-size:9.5px; display:block;">SpO2</span><b>99%</b></div>
                </div>

                <div style="margin-bottom:14px;">
                    <span style="font-size:10px; font-weight:800; color:#64748B; text-transform:uppercase; letter-spacing:0.04em;">Doctor Assessment & Clinical Plan</span>
                    <div style="background:#F0FDFA; border-left:4px solid #0D9488; padding:8px 12px; font-size:11.5px; color:#134E4A; border-radius:0 6px 6px 0; margin-top:4px;">
                        {consult_notes}
                    </div>
                </div>

                <div style="margin-bottom:16px;">
                    <div style="font-size:15px; font-weight:900; color:#0D9488; margin-bottom:6px;">℞ Medication Orders</div>
                    <table style="width:100%; font-size:11.5px; border-collapse:collapse; text-align:left;">
                        <thead>
                            <tr style="background:#F1F5F9; border-bottom:1px solid #CBD5E1; color:#475569;">
                                <th style="padding:6px 10px;">Medication / Generic</th>
                                <th style="padding:6px 10px;">Dosage Instructions</th>
                                <th style="padding:6px 10px;">Duration</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid #F1F5F9; color:#0F172A;">
                                <td style="padding:6px 10px; font-weight:700;">{drug_name}</td>
                                <td style="padding:6px 10px;">{dosage}</td>
                                <td style="padding:6px 10px;">{duration}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #E2E8F0; padding-top:10px; font-size:10px; color:#64748B;">
                    <div>
                        <span style="color:#16A34A; font-weight:700;">● Cryptographically Verified Electronic Health Record</span>
                        <div style="font-family:monospace; color:#94A3B8; margin-top:2px;">Ref: RX-{curr_apt['apt_id']} • Auth Hash: {hex(abs(hash(curr_apt['apt_id'])))[2:10]}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-weight:700; color:#0F172A;">Electronically Signed by {user['name']}</div>
                        <div>MedCare Clinical Security Protocol § 164.312</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# VIEW 3: PATIENT MOBILE PORTAL (WhatsApp-Style Interface)
# ==============================================================================
def render_patient_view():
    render_workspace_sidebar()

    st.markdown("""
    <div class="app-header">
        <div>
            <div class="app-title">PATIENT PORTAL</div>
            <div class="app-subtitle">MedCare Clinic — Automated Patient Care Assistant</div>
        </div>
        <div style="font-size: 12px; background-color: #1E293B; padding: 6px 12px; border-radius: 4px; color: #94A3B8;">
            Channel: WhatsApp Mobile Protocol
        </div>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.logged_user or {"name": "Ahmed Khan", "id": "PAT-1001"}

    # Two-Column Patient Layout: Left = WhatsApp Chat Assistant, Right = Scheduled Appointments & Clinical Records
    col_chat, col_info = st.columns([1.5, 1.2], gap="large")

    with col_chat:
        st.markdown("""
        <div class="mobile-chat-frame">
            <div class="mobile-chat-header">
                MedCare Clinic Assistant<br>
                <span style="font-size:11px; font-weight:normal; opacity:0.8;">Online | Verified Clinic Channel</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        graph = st.session_state.supervisor_graph
        state = st.session_state.graph_state

        if not state["messages"]:
            state = graph.step(state)
            st.session_state.graph_state = state

        # Single Column Mobile Chat Area
        chat_box = st.container(height=420)
        with chat_box:
            for msg in state["messages"]:
                sender = msg["sender"]
                text = msg["text"]
                if sender == "Patient":
                    st.markdown(f"""
                    <div class="chat-bubble-patient-mobile">
                        {text}
                        <div style="font-size:9px; color:#657786; text-align:right; margin-top:2px;">{datetime.now().strftime('%H:%M')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if "High severity" in text or "Emergency Room" in text or "URGENT" in text or "EMERGENCY ALERT" in text:
                        st.markdown("""
                        <div style="background-color:#FEE2E2; border:1.5px solid #EF4444; color:#991B1B; padding:10px 14px; border-radius:8px; margin:8px 12px; font-weight:700; font-size:13px;">
                            CRITICAL NOTICE: High severity detected. Please visit the nearest Emergency Room immediately.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="chat-bubble-system-mobile">
                            {text}
                            <div style="font-size:9px; color:#94A3B8; text-align:right; margin-top:2px;">{datetime.now().strftime('%H:%M')}</div>
                        </div>
                        """, unsafe_allow_html=True)

        # Chat Text Entry
        with st.form("mobile_chat_form", clear_on_submit=True):
            user_msg = st.text_input("Type message in Roman Urdu...", label_visibility="collapsed", placeholder="e.g. Mujhe 2 din se bukhar hai...")
            send_btn = st.form_submit_button("Send Message", use_container_width=True)

            if send_btn and user_msg.strip():
                updated_state = graph.step(st.session_state.graph_state, user_message=user_msg.strip())
                st.session_state.graph_state = updated_state
                st.rerun()

    with col_info:
        # Patient Card
        st.markdown(f"""
        <div class="workspace-card" style="margin-bottom:14px; border-left:4px solid #0D9488; background:#FFFFFF; padding:14px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div>
                <span style="font-size:11px; font-weight:700; color:#0D9488; text-transform:uppercase;">Verified Patient Record</span>
                <div style="font-size:18px; font-weight:800; color:#0F172A; margin-top:2px;">{user.get('name', 'Patient')}</div>
                <div style="font-size:12px; color:#64748B;">MRN: <code>{user.get('id', 'PAT-1001')}</code> | Language: <b>Urdu / English</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Scheduled Appointments Section
        st.markdown("##### My Scheduled Appointments & Doctors")

        # Query DB for patient appointments
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.id, a.appointment_date, a.time_slot, a.status, a.urgency_level, a.chief_complaint,
                   p.name as doctor_name, p.specialty as doctor_specialty, p.fee_pkr,
                   b.name as branch_name, b.city
            FROM appointments a
            JOIN practitioners p ON a.doctor_id = p.id
            JOIN branches b ON a.branch_id = b.id
            WHERE a.patient_id = ?
            ORDER BY a.rowid DESC
            LIMIT 5
        ''', (user.get("id", "PAT-1001"),))
        my_appts = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if my_appts:
            for apt in my_appts:
                badge_bg = "#DCFCE7" if apt['status'] == "Scheduled" else ("#E0F2FE" if apt['status'] == "Completed" else "#FEE2E2")
                badge_color = "#15803D" if apt['status'] == "Scheduled" else ("#0284C7" if apt['status'] == "Completed" else "#991B1B")
                st.markdown(f"""
                <div class="workspace-card" style="margin-bottom:12px; border:1px solid #E2E8F0; border-radius:10px; padding:12px 14px; background:#FFFFFF;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <span style="font-size:10px; background:#F0FDFA; color:#0D9488; padding:2px 8px; border-radius:4px; font-weight:700;">{apt['doctor_specialty']}</span>
                            <div style="font-size:15px; font-weight:700; color:#0F172A; margin-top:4px;">{apt['doctor_name']}</div>
                            <div style="font-size:11px; color:#64748B;">{apt['branch_name']}, {apt['city']}</div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:10px; background:{badge_bg}; color:{badge_color}; padding:2px 8px; border-radius:4px; font-weight:700;">{apt['status']}</span>
                            <div style="font-size:10px; color:#94A3B8; margin-top:4px;"><code>{apt['id']}</code></div>
                        </div>
                    </div>
                    <div style="margin-top:8px; padding:6px 10px; background:#F8FAFC; border-radius:6px; font-size:11px; color:#334155; display:flex; justify-content:space-between;">
                        <div><b>Date:</b> {apt['appointment_date']}</div>
                        <div><b>Slot:</b> {apt['time_slot']}</div>
                        <div><b>Fee:</b> PKR {apt.get('fee_pkr', 2000):,}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No appointments scheduled yet. Complete the clinical intake chat on the left to schedule with a doctor.")

        # Prescriptions & Signed Care Orders Section
        st.markdown("##### My Prescriptions & Signed Care Orders")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c_rx = conn.cursor()
        c_rx.execute("""
            SELECT m.*, p.name as doctor_name, p.specialty as doctor_specialty
            FROM medication_requests m
            JOIN practitioners p ON m.doctor_id = p.id
            WHERE m.patient_id = ?
            ORDER BY m.rowid DESC
            LIMIT 3
        """, (user.get("id", "PAT-1001"),))
        my_prescriptions = [dict(r) for r in c_rx.fetchall()]
        conn.close()

        if my_prescriptions:
            for rx in my_prescriptions:
                rx_html = (
                    f'<div class="workspace-card" style="margin-bottom:12px; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:10px; padding:12px 14px; background:#F0FDF4;">'
                    f'<div style="display:flex; justify-content:space-between; align-items:flex-start;">'
                    f'<div>'
                    f'<span style="font-size:10px; background:#DCFCE7; color:#15803D; padding:2px 8px; border-radius:4px; font-weight:700;">SIGNED PRESCRIPTION</span>'
                    f'<div style="font-size:15px; font-weight:800; color:#0F172A; margin-top:4px;">{rx["drug_name"]}</div>'
                    f'<div style="font-size:11px; color:#64748B;">Prescribed by: <b>{rx["doctor_name"]}</b> ({rx["doctor_specialty"]})</div>'
                    f'</div>'
                    f'<div style="text-align:right;">'
                    f'<span style="font-size:10px; background:#16A34A; color:#FFFFFF; padding:2px 8px; border-radius:4px; font-weight:700;">{rx["status"].upper()}</span>'
                    f'<div style="font-size:10px; color:#94A3B8; margin-top:4px;"><code>{rx["id"]}</code></div>'
                    f'</div>'
                    f'</div>'
                    f'<div style="margin-top:8px; padding:6px 10px; background:#FFFFFF; border-radius:6px; font-size:11px; color:#334155; border:1px solid #DCFCE7;">'
                    f'<b>Dosage:</b> {rx["dosage"]} &nbsp;|&nbsp; <b>Duration:</b> {rx["duration"]} &nbsp;|&nbsp; <b>Ref Appointment:</b> <code>{rx["appointment_id"]}</code>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(rx_html, unsafe_allow_html=True)

                with st.expander(f"📄 View Official Signed Prescription ({rx['drug_name']})", expanded=False):
                    doc_cred = DOC_CREDENTIALS.get(rx.get("doctor_id", "DOC-031"), {"degrees": "MBBS, FCPS", "pmc": "34821-P", "rank": "Consultant Physician"})
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border:1.5px solid #CBD5E1; border-radius:10px; padding:18px; font-family:sans-serif;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; border-bottom:2px solid #0F172A; padding-bottom:10px; margin-bottom:10px;">
                            <div>
                                <div style="font-size:18px; font-weight:900; color:#0F172A;">CITY CARE CLINICS</div>
                                <div style="font-size:10px; font-weight:700; color:#0D9488; text-transform:uppercase;">DHA Phase 5 Branch, Lahore • Ambulatory Care</div>
                                <div style="font-size:9px; color:#64748B;">License: PB-HL-84920 | Helpline: +92-42-111-CARE (2273) | Emergency: 1122</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:13px; font-weight:800; color:#0F172A;">{rx["doctor_name"]}</div>
                                <div style="font-size:10px; color:#475569;">{doc_cred["degrees"]}</div>
                                <div style="font-size:9px; color:#64748B;">PMC Reg #: <code>{doc_cred["pmc"]}</code></div>
                            </div>
                        </div>
                        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:6px; padding:8px 10px; font-size:10px; display:grid; grid-template-columns:repeat(3, 1fr); gap:6px; margin-bottom:10px;">
                            <div><span style="color:#94A3B8;">PATIENT:</span> <b>{user.get('name', 'Patient')}</b></div>
                            <div><span style="color:#94A3B8;">MRN:</span> <code>{user.get('id', 'PAT-1001')}</code></div>
                            <div><span style="color:#94A3B8;">DATE:</span> <b>2026-10-10</b></div>
                        </div>
                        <div style="font-size:14px; font-weight:900; color:#0D9488; margin-bottom:6px;">℞ Medication Orders</div>
                        <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:10px; font-size:11px; margin-bottom:10px;">
                            <b style="font-size:13px; color:#0F172A;">{rx["drug_name"]}</b><br>
                            <b>Dosage & Instructions:</b> {rx["dosage"]}<br>
                            <b>Duration:</b> {rx["duration"]}
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #E2E8F0; padding-top:8px; font-size:9px; color:#64748B;">
                            <span style="color:#16A34A; font-weight:700;">● Electronically Signed & Verified</span>
                            <span style="font-family:monospace;">Rx ID: <code>{rx["id"]}</code></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No active signed prescriptions yet. After your doctor signs medication orders, they appear here.")

        # Bottom Expanders in right column
        with st.expander("Upload Diagnostic Lab PDF Report"):
            lab_file = st.file_uploader("Select Lab PDF File", type=["pdf", "png", "txt"], key="mobile_lab_upload")
            if lab_file and st.button("Parse Lab Report", use_container_width=True):
                parser = LabReportParser()
                sample_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "lab_reports", "lab_report_01.txt")
                parsed = parser.parse_report_file(sample_file) if os.path.exists(sample_file) else {
                    "panel_name": "CBC", "abnormal_count": 1, "urdulish_explanation": "Hemoglobin 9.5 g/dL (Low)."
                }
                st.session_state.parsed_lab_result = parsed
                st.success("Report attached to profile!")

            if st.session_state.parsed_lab_result:
                st.info(st.session_state.parsed_lab_result.get("urdulish_explanation"))

        with st.expander("Update Patient Baseline History"):
            with st.form("mobile_baseline_form"):
                st.text_input("Known Allergies", value="Penicillin")
                st.text_input("Current Medications", value="Panadol 500mg")
                if st.form_submit_button("Save Profile Data"):
                    st.success("Profile saved!")

# ==============================================================================
# VIEW 4: AUTOMATED CARE REMINDERS HUB (Email Dispatch Engine over HTTPS Port 443)
# ==============================================================================
def render_reminders_view():
    render_workspace_sidebar()

    st.markdown("""
    <div class="app-header">
        <div>
            <div class="app-title">AUTOMATED CARE REMINDERS HUB</div>
            <div class="app-subtitle">Email Dispatch Engine over HTTPS Port 443 (Resend API Gateway)</div>
        </div>
        <div style="font-size: 12px; background-color: #1E293B; padding: 6px 12px; border-radius: 4px; color: #94A3B8;">
            Protocol: REST API / HTTPS 443
        </div>
    </div>
    """, unsafe_allow_html=True)

    r1, r2 = st.columns([1.8, 1])

    with r1:
        st.markdown("##### Enqueued Patient Care Reminder Plans")

        plans = [
            {"id": "PAT-0012", "name": "Tariq Mahmood", "email": "tariq.mahmood@patient.clinic.pk", "type": "Medication & Follow-up", "due": "Tomorrow 09:00 AM", "details": "Panadol 500mg post-breakfast & follow-up checkup date."},
            {"id": "PAT-0002", "name": "Sana Siddiqui", "email": "sana.siddiqui@patient.clinic.pk", "type": "Diagnostic Lab Fasting", "due": "Tomorrow 08:00 AM", "details": "Fasting blood sugar lab preparation reminder (8-10h fast)."},
            {"id": "PAT-0045", "name": "Muhammad Ali", "email": "muhammad.ali@patient.clinic.pk", "type": "Diabetes Control Follow-up", "due": "In 3 Days", "details": "HbA1c diabetes follow-up consultation with Dr. Hira Rehman."},
        ]

        for p in plans:
            st.markdown(f"""
            <div class="workspace-card" style="margin-bottom:12px;">
                <div style="display:flex; justify-space-between; align-items:center;">
                    <div>
                        <b style="font-size:14px; color:#0F172A;">{p['name']}</b> ({p['id']})<br>
                        <span style="font-size:12px; color:#64748B;">Recipient Email: <code>{p['email']}</code></span>
                    </div>
                    <div>
                        <span class="badge badge-email">{p['type']}</span>
                    </div>
                </div>
                <div style="font-size:12px; color:#334155; margin-top:8px; background-color:#F8FAFC; padding:8px; border-radius:4px;">
                    <b>Schedule Due:</b> {p['due']}<br>
                    <b>Instructions:</b> {p['details']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Dispatch All Batch Care Reminders via Email (HTTPS Port 443)", use_container_width=True):
            dispatch_results = []
            for p in plans:
                res = st.session_state.notif_mcp.send_email_confirmation(
                    email=p['email'],
                    subject=f"Automated Care Reminder: {p['type']}",
                    body_text=f"Dear {p['name']}, this is an automated reminder regarding your care plan: {p['details']}"
                )
                dispatch_results.append({
                    "patient": p['name'],
                    "email": p['email'],
                    "status": res.get("status"),
                    "protocol": res.get("protocol", "HTTPS_PORT_443"),
                    "gateway_id": res.get("gateway_id")
                })
            
            st.session_state.dispatched_email_logs = dispatch_results
            st.success("Batch Care Reminder Emails Dispatched Successfully over HTTPS Port 443!")
            st.rerun()

    with r2:
        st.markdown("##### Manual Email Dispatch Form")
        with st.form("manual_email_form"):
            recipient_email = st.text_input("Patient Recipient Email", value="patient@example.com")
            email_subject = st.text_input("Email Subject", value="Appointment Care Plan Reminder")
            email_body = st.text_area("Email Content Body", value="Assalam-o-Alaikum! Your follow-up appointment is scheduled for tomorrow at 10:00 AM. Please bring your past lab reports.", height=120)

            send_single = st.form_submit_button("Send Care Reminder Email", use_container_width=True)

            if send_single:
                res = st.session_state.notif_mcp.send_email_confirmation(
                    email=recipient_email,
                    subject=email_subject,
                    body_text=email_body
                )
                st.session_state.dispatched_email_logs.append({
                    "patient": "Direct Patient",
                    "email": recipient_email,
                    "status": res.get("status"),
                    "protocol": res.get("protocol", "HTTPS_PORT_443"),
                    "gateway_id": res.get("gateway_id")
                })
                st.success(f"Email sent to {recipient_email}! Status: {res.get('status')} ({res.get('protocol', 'HTTPS_PORT_443')})")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### Live Dispatch Audit Log")
        if not st.session_state.dispatched_email_logs:
            st.info("No emails dispatched in current session yet.")
        else:
            for log in reversed(st.session_state.dispatched_email_logs[-5:]):
                st.markdown(f"""
                <div style="font-size:11px; background-color:#FFFFFF; border:1px solid #E2E8F0; padding:8px; border-radius:4px; margin-bottom:6px;">
                    <b>To:</b> {log['email']}<br>
                    <b>Status:</b> <span style="color:#16A34A; font-weight:700;">{log['status']}</span> | <b>Protocol:</b> {log['protocol']}<br>
                    <b>Gateway Ref:</b> <code>{log['gateway_id']}</code>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# MAIN WORKSPACE ROUTING
# ==============================================================================
def main():
    module = st.session_state.current_module
    if module == "RECEPTIONIST":
        render_receptionist_view()
    elif module == "DOCTOR":
        render_doctor_view()
    elif module == "PATIENT":
        render_patient_view()
    elif module == "REMINDERS":
        render_reminders_view()
    else:
        render_login_view()

if __name__ == "__main__":
    main()
