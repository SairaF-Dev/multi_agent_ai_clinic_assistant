# MedCare Clinic — Enterprise End-to-End AI Healthcare Platform

[![System Status](https://img.shields.io/badge/System%20Status-Production%20Ready-brightgreen)](https://github.com)
[![Evaluation Benchmark](https://img.shields.io/badge/Evaluation%20Benchmark-65%2F65%20Passed%20(100%25)-blue)](https://github.com)
[![Emergency Recall](https://img.shields.io/badge/Emergency%20Recall-100.0%25-red)](https://github.com)
[![Prescription Safety](https://img.shields.io/badge/Prescription%20Safety-100.0%25%20Recall-orange)](https://github.com)

> **Brand:** MedCare Clinic  
> **Tagline:** *Your Health, Our Priority*  
> **Core Principle:** *"AI handles the workflow, but doctors remain in control of clinical decisions."*  
> **🌐 Live Production Deployment:** [https://multiagentaiclinicassistant-production.up.railway.app](https://multiagentaiclinicassistant-production.up.railway.app)

---

## 🏥 Platform Overview

**MedCare Clinic** is an end-to-end healthcare SaaS platform for outpatient clinic operations. The platform integrates:
- **Public Patient Website & Returning Patient Greeting**
- **Bilingual Conversational AI Assistant** (English, Roman Urdu / UrduLish, Urdu)
- **LangGraph Multi-Agent Supervisor Backend** (11 agents with parallel fan-out and HITL interrupt)
- **Rule-First Emergency Filter** (100% Recall for acute chest pain, dyspnoea, and casual minimization)
- **Prompt-Injection Hardened Lab Report Workflow**
- **5-Stage Deterministic Drug Interaction & Allergy Safety Engine**
- **Doctor Clinical Workspace** (Split-Screen Queue, Intake Notes, and SOAP Consultations)
- **Human-in-the-Loop (HITL) Approvals** (Lab Explanations, Prescription Orders, Low-Confidence Triage)
- **Receptionist Command Center** (High-Density Live Feed & Manual Takeover Override)
- **Dual Memory Layer** (Short-term conversation buffer + Long-term cross-visit preferences)
- **AI Observability & Trace Waterfalls** (Step latency, token metrics, cost tracking, tool calls)
- **Immutable Clinical Audit Trail** (HIPAA-inspired access and modification logging)
- **Benchmark Evaluation Suite** (65 automated scenarios passing with 100% success rate)

---

## 🎨 Global Design System

- **Background:** White (`#FFFFFF`) / Light Gray Slate (`#F8FAFC`)
- **Typography:** Inter Sans-Serif font hierarchy
- **Text:** Dark Navy (`#0F172A`)
- **Primary Brand Color:** Medical Teal (`#0D9488` / `#14B8A6`)
- **Primary Action Color:** Clinical Blue (`#0284C7` / `#2563EB`)
- **Success / Low-Risk:** Emerald Green (`#16A34A`)
- **Warning / Review Required:** Amber (`#D97706`)
- **Emergency / Contraindication:** Clinical Red (`#DC2626`)
- **Strictly No Emojis:** Zero default emojis in clinical tables and grids (clean SVG icons via Lucide)
- **Zero Academic AI Jargon:** Standard clinical terminology only ("Patient Records", "Clinical Summary", "Safety Alert")

---

## 🌐 Application Route Map

| Route | View Description | Target Persona |
|-------|------------------|----------------|
| `/` | **Public Homepage**: Hero, trust badges, 4 service cards, and returning patient personalized card (`Ahmed Khan 👋` / `Dr. Bilal Ahmed`) | Public / Patient |
| `/assistant` | **MedCare AI Assistant**: 5-step progress indicator, quick response chips, right-side intake panel, and emergency modal | Patient |
| `/portal`, `/profile` | **Patient Portal & Medical Profile**: Chronological medical timeline, active conditions, allergies, and care plan | Patient |
| `/doctor` | **Doctor Clinical Workspace**: Split-screen patient queue, SOAP consultation notes, and allergy safety alert banner | Physician (Dr. Bilal Ahmed) |
| `/doctor/approvals` | **Human-in-the-Loop Approvals**: Lab explanations, prescription orders, and low-confidence triage cases | Physician (Dr. Bilal Ahmed) |
| `/appointments/book` | **Appointment Booking**: Specialty → Doctor (Dr. Bilal) → Date → Slot → Confirmation with Reference ID | Patient |
| `/reports` | **Lab Reports Workflow**: File upload with prompt-injection defense and 6-stage lifecycle pipeline | Patient / Doctor |
| `/prescriptions` | **Prescription Management**: Active medications, dosage instructions, and 5-stage conflict verification | Patient / Physician |
| `/receptionist` | **Receptionist Command Center**: Dense data grid live feed, urgency tags, and manual takeover toggle | Front Desk Operations |
| `/reminders` | **Care Reminders Hub**: Medication adherence tracking, pre-draw lab fasting alerts, and Early Warning Safety Net escalations | Care Coordinator (Farhan Ali) |
| `/admin/graph` | **LangGraph Multi-Agent Topology**: Interactive visualization of supervisor routing and parallel branches | Administrator |
| `/admin/traces` | **AI Observability Traces**: Waterfall latency breakdown (ms), token usage, cost ($), and tool calls | Administrator |
| `/admin/audit` | **Immutable Audit Trail**: Append-only compliance log for logins, views, approvals, and escalations | Administrator / Compliance |
| `/admin/evaluations` | **Benchmark Evaluation Dashboard**: Visual results of the 65-scenario clinical test suite | Administrator |
| `/health` | **API Health Check**: JSON status of database, MCP servers, and safety engine | Developer / DevOps |

---

## 👥 Demo Personas & Fast 1-Click Access

| Persona | Username | Password | Profile Details |
|---------|----------|----------|-----------------|
| **Patient** | `ahmed` | `password123` | **Ahmed Khan** (MRN: `PAT-1001`), Age 38, Hypertension, Penicillin Allergy, Preferred Doctor: Dr. Bilal Ahmed |
| **Doctor** | `dr.bilal` | `password123` | **Dr. Bilal Ahmed** (ID: `DOC-101`), General Physician (Rating 4.9), DHA Phase 5 Branch, Lahore |
| **Receptionist** | `receptionist` | `password123` | **Sana Front Desk** (ID: `REC-001`), High-density queue management & manual override |
| **Care Lead** | `coordinator` | `password123` | **Farhan Ali** (ID: `FLD-001`), Care Reminder Coordinator, Adherence & Early Warning Safety Net |
| **Clinic Admin** | `admin` | `password123` | **Clinic Administrator**, Observability, LangGraph topology, and audit trail |

---

## 📚 Role-Based User Manuals & Documentation

Comprehensive step-by-step operating guides are provided for each clinical role:

- 📖 **[Master User Guides Index](docs/user-guides/README.md)** — Architecture overview, credentials, and cross-functional guide directory.
- 👩‍⚕️ **[Patient Portal Guide](docs/user-guides/01-patient-portal-guide.md)** — Bilingual conversational AI intake, 5-stage progress indicator, emergency red-flag bypass (1122), appointment booking, and lab report explanations.
- 👨‍⚕️ **[Doctor Clinical Workspace Guide](docs/user-guides/02-doctor-clinical-workspace-guide.md)** — Split-screen queue, allergy contraindications, automated SOAP consultation notes, and Human-in-the-Loop (HITL) approval workflows.
- 👩‍💼 **[Receptionist Command Center Guide](docs/user-guides/03-receptionist-command-center-guide.md)** — Real-time live feed, walk-in registration, triage tags, and live **Manual Chat Takeover / Intercept**.
- 🩺 **[Care Reminders Hub Guide](docs/user-guides/04-care-coordinator-hub-guide.md)** — Medication adherence monitoring, pre-draw lab fasting alerts, omnichannel batch dispatch (Resend Email API + WhatsApp), and Early Warning Safety Net escalations.
- 🛠️ **[Operations & Maintenance Runbook](docs/runbook.md)** — Architecture diagrams, `.env` specification, execution commands (FastAPI, Streamlit, Docker), automated test verification, incident troubleshooting, and enterprise roadmap.

---

## 🚀 Running the Application

### Option 1: Launch Full-Stack Web Application (FastAPI + SPA)

```bash
# 1. Activate virtual environment
D:\Netixsol\Week9\multi_agent_env\Scripts\activate

# 2. Navigate to project directory
cd D:\Netixsol\Week9\ai-clinic-assistant

# 3. Launch FastAPI server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Web Application Portal:** [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **System Health:** [http://localhost:8000/health](http://localhost:8000/health)

### Option 2: Launch Streamlit Enterprise EHR Portal

```bash
python -m streamlit run src/ui/app.py --server.port 8501
```
- **Streamlit EHR Portal:** [http://localhost:8501](http://localhost:8501)

### Option 3: Docker Compose

```bash
docker-compose up --build
```
- Both port **8000** (Full-Stack Web App) and port **8501** (Streamlit EHR) will be active.

---

## 🧪 Testing & Evaluation Verification

All 12 backend test suites and all 5 evaluation benchmarks pass with **100% success**:

```bash
# Run All 12 Unit & Integration Test Suites
python tests/test_supervisor_graph.py
python tests/test_red_teaming.py
python tests/test_nlp_triage_nurse.py
python tests/test_observability.py
python tests/test_channel_gateway.py
python tests/test_hitl_approval.py

# Run Full 65-Scenario Benchmark Evaluation Suite
python tests/eval_suite.py
```

### Benchmark Summary Results

| Metric | Target | Result | Status |
|--------|--------|--------|--------|
| **Total Test Scenarios** | 65 | **65 / 65** | **100.0% Pass** |
| **Emergency Recall Rate** | 100.0% | **100.0%** | **PASSED** |
| **Specialty Accuracy** | &ge; 90.0% | **100.0%** | **PASSED** |
| **Booking Accuracy Rate** | &ge; 95.0% | **100.0%** | **PASSED** |
| **RAG Grounding Rate** | 100.0% | **100.0%** | **PASSED** |
| **Allergy & Interaction Recall** | 100.0% | **100.0%** | **PASSED** |
| **Safety Boundary Enforcement** | 100.0% | **100.0%** | **PASSED** |
| **Average Latency per Case** | &lt; 50 ms | **0.22 ms** | **PASSED** |
| **Average Cost per Case** | &lt; $0.001 | **$0.000060 USD** | **PASSED** |

---

## 🛡️ Critical Safety Workflows Demonstrated

1. **Journey 1 — Returning Patient (Ahmed Khan):**
   - System identifies Ahmed Khan (`PAT-1001`), recalls preferred language (Urdu) and preferred physician (Dr. Bilal Ahmed).
   - Conversational intake in Roman Urdu extracts symptoms and computes routine triage.
   - Slot booking confirmed for tomorrow at 10:30 AM with Reference ID and automated confirmation dispatch.
2. **Journey 2 — Casual UrduLish Emergency Bypass:**
   - Patient types: *"Seene mein thora dard hai lekin koi baat nahi"* (downplaying cardiac red flag).
   - Rule-first red-flag filter instantly halts routine booking and renders the **Emergency Protocol Screen** with 1122 escalation instructions.
3. **Journey 3 — Lab Report & Doctor Approval:**
   - Patient uploads lab report containing potential prompt-injection attack strings.
   - Document text is treated strictly as untrusted data; clinical entities are regex-extracted.
   - Plain-language explanation is drafted, LangGraph execution pauses at `HITL_APPROVAL_CHECKPOINT`, and Dr. Bilal Ahmed approves the explanation before patient delivery.
4. **Journey 4 — Prescription Safety Contraindication:**
   - Prescribing Augmentin (Amoxicillin) triggers the 5-stage safety engine, cross-referencing Ahmed's severe Penicillin allergy, locking autonomous order execution and alerting the doctor.
