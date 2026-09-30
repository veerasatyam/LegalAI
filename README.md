# 🏛️ Smart Legal Aid Assistance
### AI-Powered Legal Scenario Awareness System (Prototype)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Groq](https://img.shields.io/badge/Groq-LPU%20Acceleration-F55036.svg)](https://groq.com)
[![Chroma Cloud](https://img.shields.io/badge/ChromaDB-Cloud%20Vector%20Store-FF6F00.svg)](https://trychroma.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Elevator Pitch:**  
> *"Smart Legal Aid Assistance transforms everyday descriptions of incidents into source-backed Indian Penal Code (IPC) explanations using a multi-stage Retrieval-Augmented Generation (RAG) pipeline, helping citizens understand the law in plain language while strictly separating educational awareness from legal advice."*

---

## 📌 Table of Contents
1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [End-to-End System Architecture](#-end-to-end-system-architecture)
4. [Complete 7-Step Workflow](#-complete-7-step-workflow)
5. [Technology Stack](#-technology-stack)
6. [Directory Structure](#-directory-structure)
7. [API Reference & Endpoints](#-api-reference--endpoints)
8. [Setup & Installation Guide](#-setup--installation-guide)
9. [Running the Application](#-running-the-application)
10. [End-to-End Scenario Walkthrough](#-end-to-end-scenario-walkthrough)
11. [Verification & Automated Tests](#-verification--automated-tests)
12. [Safety Guardrails & Disclaimer](#-safety-guardrails--disclaimer)

---

## 📖 Project Overview

Ordinary citizens do not think in terms of legal sections. When faced with an incident, they do not ask:
> *"What is Section 341 of the Indian Penal Code?"*

Instead, they describe real-life events:
> *"Someone blocked my bike on a public road and wouldn't let me pass."*

To understand their legal rights or implications, citizens typically face confusing terminology, unreliable forum advice, and lack of statutory grounding. 

**Smart Legal Aid Assistance** bridges this gap:
- **Natural Language Input**: Accepts plain descriptions of everyday incidents.
- **Fact Extraction**: Automatically breaks down actors, actions, harm types, and locations.
- **Vector-Grounding (RAG)**: Searches verified bare-act statutes from **Chroma Cloud** to eliminate hallucinations.
- **Groq LPU Reasoning**: Uses low-latency LLM inference to explain why provisions apply, outlines punishments, and provides actionable evidence checklists.
- **Session Continuity**: Multi-turn inquiries saved to a **NoSQL database** with secure **JWT authentication**.

---

## ❗ Problem Statement

| Traditional Method | Smart Legal Aid Platform |
|---|---|
| Citizen must know IPC section numbers in advance. | Accepts everyday natural language descriptions. |
| Generic LLMs hallucinate non-existent sections or foreign laws. | RAG restricts reasoning to verified IPC bare-act text from Chroma Cloud. |
| Legal jargon confuses the citizen. | Plain-language explanation with real-life context. |
| No persistent audit trail or structured history. | NoSQL session store retains user inquiries and structured analyses. |
| Potential abuse for evasion or illegal instructions. | Intent & safety classification blocks malicious/evasion queries upfront. |

---

## 🏗️ End-to-End System Architecture

```
                                  ┌────────────────────────┐
                                  │   Citizen / User       │
                                  │  (React 19 Dashboard)  │
                                  └───────────┬────────────┘
                                              │ POST /api/sessions/{id}/query
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND SERVICE                                   │
│                                                                                        │
│  [ Step 1: JWT Authentication & Input Validation ]                                     │
│     ├── Validates Bearer Token & User Ownership                                        │
│     └── Sanitizes Input Text                                                           │
│                                                                                        │
│  [ Step 2: Intent & Risk Classification ]                                              │
│     ├── Allowed: "Explain situation", "Which IPC section applies?", "What to do?"     │
│     └── Blocked: "How to evade police?", "How to hide evidence?"                      │
│                                                                                        │
│  [ Step 3: Scenario Understanding & Legal Fact Extraction ]                            │
│     ├── Actors (strangers, groups, neighbors)                                          │
│     ├── Actions (blocked, pushed, threatened, snatched)                                │
│     ├── Harm Classification (restriction of movement, property, bodily harm)          │
│     └── Urgency Assessment (low, medium, high)                                         │
│                                                                                        │
│  [ Step 4: Dense Vector Embedding ]                                                    │
│     └── all-MiniLM-L6-v2 (384-dimensional dense vectors)                              │
│                                                                                        │
│  [ Step 5: ChromaDB Cloud Vector Search ] ──────────────────┐                          │
│     └── Queries 463 IPC Bare Act Sections                    │                          │
│         Collection: ipc_sections (Database: legal)          │                          │
│                                                              │                          │
│  [ Step 6: Groq LLM Legal Analysis & Response Assembly ] ────┴─► [ Chroma Cloud ]      │
│     ├── Model: qwen/qwen3.8-27b                                  (api.trychroma.com)   │
│     ├── Synthesizes Applicable Sections + Plain Meaning                                │
│     ├── Explains Legal Ingredients & Punishments                                       │
│     └── Compiles Evidence Checklist & Action Guidance                                  │
│                                                                                        │
│  [ Step 7: NoSQL Database Persistence ] ───────────────────────► [ NoSQL Store ]        │
│     ├── Stores multi-turn user/assistant conversation            (MongoDB / TinyDB)    │
│     └── Records audit log & processing metrics                                         │
└─────────────────────────────────────────────┬──────────────────────────────────────────┘
                                              │
                                              ▼
                                 [ Structured JSON Output ]
                                              │
                                              ▼
                                  ┌────────────────────────┐
                                  │  React UI Results View │
                                  │  - Summary             │
                                  │  - Applicable Sections │
                                  │  - Risk Level Badge    │
                                  │  - Evidence Checklist  │
                                  │  - Statutory Notice    │
                                  └────────────────────────┘
```

---

## 🔄 Complete 7-Step Workflow

1. **User Input**: The user describes an incident in natural language via the React frontend.
2. **Intent Classification**: The system checks if the scenario is an informational awareness query or an evasion attempt. Malicious queries are rejected with an advisory message.
3. **Scenario Fact Extraction**: Rule-based and semantic extractors convert free text into structured legal entities:
   - `actors`: e.g., `["unknown_person"]`
   - `actions`: e.g., `["stopped", "threatened"]`
   - `harm_types`: e.g., `["restriction_of_movement", "threat"]`
   - `legal_categories`: e.g., `["wrongful_restraint", "criminal_intimidation"]`
4. **Legal Element Mapping & Retrieval**: Query vectors are generated using `sentence-transformers/all-MiniLM-L6-v2` and searched against Chroma Cloud vector storage to retrieve candidate sections.
5. **Groq LPU Reasoning**: Candidates and extracted facts are assembled into a constrained legal prompt for Groq (`qwen/qwen3.8-27b`). The model:
   - Confirms which provisions apply.
   - Evaluates whether statutory conditions (such as physical blockage or threat) are satisfied.
   - Generates plain-language explanations and lists applicable penalties.
6. **Persistence**:
   - The query and structured output are appended to the active session in the NoSQL database.
   - Audit metadata (processing time, matched sections) is logged.
7. **Statutory Disclaimer**: Every analysis finishes with an educational notice distinguishing legal awareness from professional representation.

---

## 💻 Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | React 19, Vite 8, Lucide React | Modern SPA dashboard with session sidebar, risk badges, and error boundary |
| **Backend API** | FastAPI, Uvicorn, Pydantic v2 | Asynchronous REST API, OpenAPI docs at `/docs` |
| **LLM Provider** | Groq Cloud API | Ultra-fast inference with `qwen/qwen3.8-27b` |
| **Vector Database** | ChromaDB Cloud | Hosted at `api.trychroma.com`, tenant `1aad0ec5...`, database `legal` |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dimensional dense semantic vectors with local caching |
| **NoSQL Database** | MongoDB / TinyDB | Unified adapter: automatically connects to MongoDB or falls back to embedded TinyDB (`data/nosql_db/`) |
| **Authentication** | `bcrypt` + `python-jose` | Salted password hashing, signed JWT Bearer tokens |

---

## 📁 Directory Structure

```
RAG/
├── app.py                     # FastAPI entry point, API routes, and static asset serving
├── config.py                  # Root configuration bridge
├── requirements.txt           # Python package requirements
├── README.md                  # Comprehensive project documentation
├── .env                       # Environment variables and API credentials
├── .env.example               # Template environment configuration
│
├── src/                       # Backend Source Code
│   ├── config.py              # Centralized settings & environment loader
│   ├── auth/                  # Security & Authentication
│   │   ├── security.py        # bcrypt password hashing & JWT encoding/decoding
│   │   └── dependencies.py    # FastAPI dependencies (get_current_user, get_optional_user)
│   ├── db/                    # Unified NoSQL Database Layer
│   │   └── nosql_manager.py   # Multi-backend document store (MongoDB + TinyDB)
│   ├── embeddings/            # Vector Database Connectors
│   │   ├── chroma_store.py    # Chroma Cloud connection & indexing manager
│   │   └── vector_store.py    # Local FAISS fallback retriever
│   ├── legal_mapping/         # RAG & LLM Analysis
│   │   ├── hybrid_retriever.py# Hybrid ChromaDB + keyword retriever
│   │   ├── llm_analyzer.py    # Groq prompt formatting, JSON parsing & fallback
│   │   └── llm_pipeline.py    # Multi-step legal mapping coordinator
│   ├── models/                # Pydantic Schemas
│   │   └── legal_schemas.py   # Request/response contracts & legal entity models
│   ├── pipeline/              # Complete End-to-End Orchestrator
│   │   └── complete_pipeline.py# 7-step pipeline: Intent -> Facts -> Chroma -> Groq -> Advice
│   ├── scenario_understanding/# Natural Language Processing
│   │   ├── extractor.py       # Entity & fact extraction engine
│   │   ├── intent_classifier.py# Evasion & safety guardrail classifier
│   │   └── validator.py       # Completeness & clarity validator
│   └── utils/                 # Utilities
│       ├── legal_definitions.py# Statutory lookup constants
│       └── text_cleaner.py    # Input sanitization
│
├── frontend/                  # React + Vite Frontend Source
│   ├── index.html             # HTML entry point
│   ├── vite.config.js         # Vite build configuration (base: './', API proxy)
│   ├── package.json           # Frontend dependencies & scripts
│   └── src/
│       ├── main.jsx           # React root with ErrorBoundary
│       ├── App.jsx            # Main dashboard state & session manager
│       ├── index.css          # Design system & responsive layout
│       └── components/
│           ├── Navbar.jsx     # Header with live service indicators & auth controls
│           ├── Sidebar.jsx    # Session history & multi-turn thread switcher
│           ├── ScenarioInput.jsx# Preset chips, description textarea, and step progress
│           ├── ResultsView.jsx# Summary, IPC section cards, risk badge, and next steps
│           ├── AuthModal.jsx  # Sign In / Create Account modal dialog
│           └── ErrorBoundary.jsx# Fallback UI with cache-clearing recovery button
│
├── static/                    # Compiled Production Frontend (Served by FastAPI)
│   ├── index.html
│   ├── favicon.svg
│   └── assets/                # Vite JS & CSS production bundles
│
├── data/                      # Data Assets
│   ├── raw/                   # Bare Act source documents (PDF & page extractions)
│   ├── processed/             # Cleaned JSON sections & precomputed embeddings
│   ├── chroma_db/             # Local Chroma cache
│   └── nosql_db/              # Embedded TinyDB store (nosql_store.json)
│
└── tests/                     # Verification Suites
    ├── test_full_system.py    # End-to-end integration test (Auth, Chroma, Groq, NoSQL)
    └── test_scenarios.py      # Scenario fact extraction unit tests
```

---

## 🔌 API Reference & Endpoints

### 1. System Health
- **`GET /api/health`**
  - **Description**: Returns live connection status for Groq LLM, Chroma Cloud vector store, and NoSQL storage.
  - **Sample Response**:
    ```json
    {
      "status": "healthy",
      "llm_provider": "groq",
      "grok_model": "qwen/qwen3.8-27b",
      "has_grok_key": true,
      "vector_database": "chroma",
      "chroma_cloud_connected": true,
      "indexed_sections_count": 463,
      "nosql_database": "TinyDB (Embedded NoSQL)"
    }
    ```

### 2. Authentication
- **`POST /api/auth/register`**
  - **Payload**: `{"username": "citizen1", "email": "user@example.com", "password": "password123", "full_name": "Citizen One"}`
  - **Response**: JWT access token and user profile object.
- **`POST /api/auth/login`**
  - **Payload**: `{"username": "citizen1", "password": "password123"}`
  - **Response**: `{"access_token": "...", "token_type": "bearer", "user": {...}}`
- **`GET /api/auth/me`**
  - **Header**: `Authorization: Bearer <token>`
  - **Response**: Current authenticated user details.

### 3. Session Management (NoSQL Backed)
- **`GET /api/sessions`**: List all saved inquiry sessions for the logged-in user.
- **`POST /api/sessions`**: Create a new session (`{"title": "Bicycle incident on main road"}`).
- **`GET /api/sessions/{session_id}`**: Retrieve full message thread and structured legal outputs.
- **`DELETE /api/sessions/{session_id}`**: Delete a session and its associated messages.

### 4. Legal Inquiry & Analysis
- **`POST /api/sessions/{session_id}/query`** (Authenticated)
- **`POST /api/query`** (Guest / Direct Testing)
  - **Payload**: `{"query": "Someone stopped my bike in the middle of the road and threatened me."}`
  - **Response Structure**:
    ```json
    {
      "status": "success",
      "response": {
        "summary": "This appears to be a case of wrongful restraint - someone illegally blocked your movement.",
        "legal_analysis": {
          "applicable_sections": [
            {
              "section": "Section 341",
              "title": "Punishment for wrongful restraint",
              "plain_meaning": "Punishes anyone who obstructs a person from proceeding in a direction they have a right to move.",
              "punishment": "Simple imprisonment up to 1 month, or fine up to 500 rupees, or both.",
              "confidence": "HIGH",
              "why_applies": ["The offender physically stopped your vehicle on a public way."]
            },
            {
              "section": "Section 339",
              "title": "Wrongful restraint",
              "plain_meaning": "Defines wrongful obstruction of another person's movement.",
              "confidence": "HIGH"
            }
          ]
        },
        "risk_assessment": {
          "level": "medium",
          "advice": "Document the time and location; consider filing a police complaint."
        },
        "practical_guidance": {
          "immediate_actions": ["Ensure your physical safety", "Dial 100/112 if in danger"],
          "legal_steps": ["Submit written complaint at local police station", "Obtain FIR/CSR acknowledgment"],
          "evidence_to_collect": ["Eyewitness details", "Vehicle registration number", "CCTV recordings"]
        },
        "disclaimer": "This platform provides legal awareness for educational purposes and does not constitute legal advice."
      }
    }
    ```

---

## ⚙️ Setup & Installation Guide

### Prerequisites
- **Python**: 3.10 to 3.13
- **Node.js**: v18+ (only needed if modifying frontend code)
- **Git**

### 1. Clone the Repository
```powershell
git clone <repository-url>
cd RAG
```

### 2. Set Up Python Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Check that `.env` contains your active keys (a template is available in `.env.example`):
```env
# Groq LLM API
GROQ_API_KEY=gsk_...
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROK_MODEL=qwen/qwen3.8-27b

# ChromaDB Cloud Vector Store
CHROMA_HOST=api.trychroma.com
CHROMA_API_KEY=ck-...
CHROMA_TENANT=1aad0ec5-79dc-4ed2-9b03-160afcf8d952
CHROMA_DATABASE=legal
CHROMA_COLLECTION_NAME=ipc_sections

# NoSQL Database (tinydb or mongodb)
NOSQL_PROVIDER=tinydb
TINYDB_PATH=data/nosql_db/nosql_store.json

# Security
SECRET_KEY=legal-aid-secret-key-super-secure-2026
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

## 🚀 Running the Application

### Option A: Standard Production Mode (Recommended)
FastAPI serves the compiled React application and all API endpoints together from a single server:

```powershell
.\.venv\Scripts\activate
python app.py
```

- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Option B: Frontend Hot-Reload Development Mode
If you wish to edit React components with instant hot module replacement:

1. **Terminal 1 (Backend API)**:
   ```powershell
   .\.venv\Scripts\activate
   python app.py
   ```

2. **Terminal 2 (React Vite Dev Server)**:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
   - Vite is live at [http://localhost:5173](http://localhost:5173). Requests to `/api` and `/auth` are automatically proxied to port 8000.

3. **Rebuilding for Production**:
   ```powershell
   cd frontend
   npm run build
   ```
   This generates the optimized bundles directly into `../static/`.

---

## 🔍 End-to-End Scenario Walkthrough

### Scenario
> *"Someone stopped my bike in the middle of the road and threatened to hit me."*

### System Execution Steps:
1. **Safety Check**: Classified as an educational query regarding incident rights. No evasion detected.
2. **Fact Parsing**:
   - Actor: `unknown_person`
   - Actions: `stopped`, `threatened`
   - Object: `motorcycle / vehicle`
   - Location: `public_road`
   - Harms: `restriction_of_movement`, `threat_of_injury`
3. **ChromaDB Cloud Query**: Dense vector search retrieves Section 339, Section 341, Section 503, and Section 506.
4. **Groq LPU Synthesis**:
   - **Section 341 IPC**: *Punishment for Wrongful Restraint* (matched because physical blockage occurred on a public way).
   - **Section 506 IPC**: *Punishment for Criminal Intimidation* (matched because a threat of bodily harm was issued).
5. **Practical Guidance Generated**:
   - Note down the offender's physical description and license plate if available.
   - Look for traffic CCTV or shop security cameras near the roadblock.
   - File a written complaint under Sections 341 and 506 at the nearest police station.

---

## 🧪 Verification & Automated Tests

The codebase includes automated test suites:

### Full System End-to-End Test
Verifies health, user registration, JWT generation, session creation, ChromaDB retrieval, Groq analysis, NoSQL message storage, and safety evasion blocks:

```powershell
.\.venv\Scripts\activate
python tests/test_full_system.py
```

### Scenario Fact Extraction Test
Validates entity identification and issue detection across real-life scenarios:

```powershell
.\.venv\Scripts\activate
python tests/test_scenarios.py
```

---

## 🛡️ Safety Guardrails & Disclaimer

### 1. Misuse & Evasion Prevention
The platform includes an `IntentSafetyClassifier`. Inquiries seeking assistance with criminal evasion (e.g., *"how to evade police"*, *"how to hide stolen goods"*) are automatically intercepted before reaching the vector store or LLM, returning a safety warning.

### 2. Statutory Legal Notice
> **Important:** This system is an artificial intelligence research prototype developed strictly for educational awareness and informational purposes. It does not provide formal legal advice, attorney-client privilege, or formal legal representation. Citizens requiring legal assistance should consult a licensed legal practitioner or a District Legal Services Authority (DLSA).
