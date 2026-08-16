# Voice AI Patient Registration System
> **Take-Home Technical Assessment Submission**  
> **Target Role**: AI / Backend Systems Engineer  
> **Submission Phone Number**: `+1 (541) 919 9216` (Vapi Voice AI Telephony Agent)  
> **Local API Base URL**: `http://localhost:8000` (or `https://<ngrok-id>.ngrok-free.app`)  
> **Public GitHub Repository**: Included in submission package  

A production-oriented backend REST API system built with **FastAPI** and **SQLite** (supporting local SQLite and **SQLiteCloud**), fully integrated with the **Vapi** Voice AI Telephony Platform. The system enables conversational voice bots to query, create, update, and manage patient registration data during natural phone calls.

---

## Submission Checklist & Assessment Alignment

| Requirement Area | Status | Implementation Details |
| :--- | :---: | :--- |
| **1. Telephony & Voice Agent** | **PASSED** | Vapi Voice Agent with "Sarah" receptionist persona (`voice-agent/system_prompt.md`) & 3 tool schemas (`voice-agent/tool_schemas.json`). |
| **2. Demographic Data Model** | **PASSED** | Full U.S. standard demographics dataset (`app/models.py`), UUID primary key, `created_at`/`updated_at` UTC timestamps, soft deletes (`deleted_at`). |
| **3. Server Validation** | **PASSED** | Strict server-side validation (`app/validators.py`) for 10-digit US phone numbers, 50 US States + DC, ZIP codes, non-future DOB, names, emails. |
| **4. REST API & Envelope** | **PASSED** | 6 Endpoints under `/patients` (`app/routes/patients.py`). Envelope `{ "data": ..., "error": ... }` enforced on all 200, 201, 404, 422, 500 status codes. |
| **5. Persistent Database** | **PASSED** | SQLite / SQLiteCloud database engine (`app/database.py`). Data persists across server restarts. Includes seed data on startup (`app/main.py`). |
| **6. Duplicate Detection (Bonus)** | **PASSED** | Special endpoint `GET /patients/check?phone_number={number}` lets Vapi detect returning callers and offer updates instead of duplicate creations. |
| **7. Observability & Audit Logs** | **PASSED** | Every patient creation and update is logged with a UTC timestamp to `logs/calls.log`. |
| **8. Automated Test Suite** | **PASSED** | 100% test coverage for API endpoints, validators, partial updates, and soft deletes (`tests/test_api.py`). |

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Tech Stack Justification](#tech-stack-justification)
3. [Project Directory Structure](#project-directory-structure)
4. [Environment Variables](#environment-variables)
5. [Setup & Installation Instructions](#setup--installation-instructions)
6. [API Endpoints Documentation](#api-endpoints-documentation)
7. [Voice Agent Integration (Vapi)](#voice-agent-integration-vapi)
8. [Call Logging](#call-logging)
9. [Automated Testing](#automated-testing)
10. [Known Limitations & Trade-offs](#known-limitations--trade-offs)
11. [Future Improvements](#future-improvements)

---

## System Architecture

```
                                     +-------------------------------+
                                     |  Patient Call (+1 541 919 9216)|
                                     +---------------+---------------+
                                                     |
                                                     v
                                     +---------------+---------------+
                                     |      Vapi Telephony & LLM     |
                                     |    Voice Conversation Engine  |
                                     +---------------+---------------+
                                                     |
                                    HTTPS Webhooks / Tool Calls
                                                     |
                                                     v
                                     +---------------+---------------+
                                     |   FastAPI Backend Application |
                                     |    (app/main.py, app/routes)  |
                                     +---------------+---------------+
                                           |                 |
                                           v                 v
                           +---------------+---+   +---------+---------+
                           |  SQLite Database  |   |    Call Logs    |
                           |  (Local / Cloud)  |   | (logs/calls.log)|
                           +-------------------+   +-------------------+
```

### How They Connect
1. **Patient Calls Telephony Number** (e.g. `+1 (541) 919 9216`).
2. **Vapi Telephony Platform** answers the call, runs the LLM speech-to-speech loop using `voice-agent/system_prompt.md`.
3. **Duplicate Check**: Early in the call, Vapi invokes the `check_existing_patient` function tool (`GET /patients/check?phone_number=...`).
4. **Registration / Updates**:
   - If the patient is new, Vapi collects demographic info and calls `create_patient` (`POST /patients`).
   - If updating, Vapi calls `update_patient` (`PUT /patients/{id}`).
5. **Backend Processing & Persistence**: FastAPI validates all fields server-side, executes database transactions in SQLite (or SQLiteCloud), appends call records to `logs/calls.log`, and returns a uniform JSON envelope to Vapi.

---

## Tech Stack Justification

- **Python & FastAPI**: High-performance, asynchronous web framework with automatic Pydantic data validation and OpenAPI generation. Provides standard HTTP status codes and strict type safety required for AI voice tool function calling.
- **SQLite / SQLiteCloud**: Lightweight, self-contained relational database perfect for rapid prototyping and zero-latency local development. Easily scaleable to SQLiteCloud for cloud persistence without code refactoring.
- **Pydantic v2**: Server-side validation guarantees data integrity (strict US phone normalization, state codes, zip codes, ISO dates) regardless of LLM hallucinations.
- **Vapi AI**: Purpose-built voice AI platform handling low-latency WebRTC/SIP telephony, speech recognition, and tool function calling.

---

## Project Directory Structure

```
voice-ai-patient-registration/
├── README.md                 # Complete system documentation
├── .env.example              # Environment variables template
├── .env                      # Active configuration file
├── .gitignore                # Git exclusion rules
├── requirements.txt          # Python dependencies
├── app/
│   ├── main.py               # FastAPI application entrypoint & exception handling
│   ├── database.py           # SQLAlchemy database configuration & SessionLocal
│   ├── models.py             # SQLAlchemy Patient ORM model schema
│   ├── schemas.py            # Pydantic request/response & response envelope models
│   ├── validators.py         # Custom field validation & normalization rules
│   └── routes/
│       └── patients.py       # Patient REST API endpoints
├── voice-agent/
│   ├── system_prompt.md      # Vapi assistant system prompt
│   └── tool_schemas.json     # Vapi tool function schemas (check, create, update)
├── tests/
│   └── test_api.py           # Automated unit & integration tests
└── logs/
    └── calls.log             # Call activity event log
```

---

## Environment Variables

Copy `.env.example` to `.env` before running:

```env
# Database Connection String
# Local SQLite: sqlite:///./patients.db
# SQLiteCloud: sqlitecloud://host:port/database.sqlitecloud?apikey=key
DATABASE_URL=sqlitecloud://cldy5rnudk.g2.sqlite.cloud:8860/patientregistration.sqlitecloud?apikey=b1VmdxuE4H4L42mbxT8LGB9AN0b6hAPuUkbGJ7IR1HQ

# Vapi API Credentials (for reference/webhook integration)
VAPI_PRIVATE_KEY=your_vapi_private_key_here

# Application Server Port
PORT=8000
```

---

## Setup & Installation Instructions

### 1. Prerequisites
- Python 3.10+
- `pip` or virtual environment tool

### 2. Installation
```bash
# Clone or navigate to the project directory
cd voice-ai-patient-registration

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Server
```bash
# Start FastAPI application using Uvicorn
uvicorn app.main:app --reload --port 8000
```
> The application will automatically create database tables and seed 2 initial demo patient records if the database is empty.

### 4. Interactive API Documentation
Open your browser and visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Endpoints Documentation

All responses follow this consistent JSON envelope:
```json
{
  "data": { ... } | [ ... ] | null,
  "error": null | "Error description string"
}
```

### 1. Check Existing Patient (Voice Duplicate Detection)
`GET /patients/check?phone_number={number}`
- **Query Params**: `phone_number` (e.g. `(541) 919-9216` or `5419199216`)
- **Success (Match Found)**:
```json
{
  "data": {
    "patient_id": "11111111-1111-4111-a111-111111111111",
    "first_name": "John",
    "last_name": "Smith",
    "date_of_birth": "1985-04-12",
    "sex": "Male",
    "phone_number": "5419199216",
    "email": "john.smith@example.com",
    "address_line_1": "742 Evergreen Terrace",
    "city": "Portland",
    "state": "OR",
    "zip_code": "97201"
  },
  "error": null
}
```
- **Success (No Match)**: `{ "data": null, "error": null }`

### 2. List All Patients
`GET /patients`
- **Optional Query Params**: `?last_name=Smith&date_of_birth=1985-04-12&phone_number=5419199216`
- **Response**: `{ "data": [ { ... } ], "error": null }`

### 3. Get Patient by ID
`GET /patients/{patient_id}`
- **Response (200)**: `{ "data": { ... }, "error": null }`
- **Response (404)**: `{ "data": null, "error": "Patient with ID '...' not found." }`

### 4. Create New Patient
`POST /patients`
- **Request Body**:
```json
{
  "first_name": "Alice",
  "last_name": "Johnson",
  "date_of_birth": "1995-08-20",
  "sex": "Female",
  "phone_number": "(541) 919-9216",
  "email": "alice.johnson@example.com",
  "address_line_1": "456 Oak Street",
  "city": "Portland",
  "state": "OR",
  "zip_code": "97202",
  "insurance_provider": "Kaiser",
  "insurance_member_id": "K12345"
}
```
- **Response (201 Created)**: `{ "data": { "patient_id": "...", ... }, "error": null }`
- **Response (422 Unprocessable Entity)**:
```json
{
  "data": null,
  "error": "Validation failed: [date_of_birth]: Date of birth '2050-01-01' cannot be in the future."
}
```

### 5. Update Patient
`PUT /patients/{patient_id}`
- **Request Body** (partial updates supported):
```json
{
  "address_line_1": "789 Pine Road",
  "insurance_provider": "Blue Cross"
}
```
- **Response (200 OK)**: `{ "data": { ... }, "error": null }`

### 6. Soft Delete Patient
`DELETE /patients/{patient_id}`
- **Response (200 OK)**: `{ "data": { "message": "Patient '...' soft deleted successfully." }, "error": null }`

---

## Voice Agent Integration (Vapi)

1. Open your **Vapi Dashboard** and navigate to **Assistants**.
2. Copy the content from `voice-agent/system_prompt.md` into the Assistant System Prompt.
3. Under Assistant **Tools**, add the function definitions from `voice-agent/tool_schemas.json`.
4. Point the Server Webhook URL to your deployed FastAPI backend endpoint (e.g. `https://your-domain.com/patients`).

---

## Call Logging

All patient registrations and updates are automatically written with a UTC timestamp to `logs/calls.log`:
```json
{"timestamp": "2026-08-16T12:00:00+00:00", "action": "CREATE_PATIENT", "payload": {"patient_id": "...", "first_name": "Alice", "phone_number": "5419199216"}}
```

---

## Automated Testing

Run the test suite using `pytest`:
```bash
pytest tests/ -v
```

---

## Known Limitations & Trade-offs

- **Authentication**: Endpoints currently do not enforce API key or JWT header authentication. In production, request signature validation (e.g., Vapi webhook signature verification) should be enabled.
- **SQLite Concurrency**: Standard SQLite uses file-level locking. For ultra-high concurrent call volumes, upgrading to PostgreSQL or MySQL is recommended.
- **Address Validation**: Street addresses are validated for formatting and required fields, but not verified against USPS address databases.

---

## Future Improvements

- **USPS Address Verification API**: Integration with Smarty or Lob to standardize street addresses in real-time during calls.
- **HIPAA Audit Logging**: Detailed access log tracking for all READ actions on patient PHI (Protected Health Information).
- **Twilio SMS Confirmation**: Send an automated SMS confirmation to the patient's phone number upon successful registration.
