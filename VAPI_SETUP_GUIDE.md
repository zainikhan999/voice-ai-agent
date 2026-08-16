# Vapi Voice AI Agent - Setup & Testing Guide

This guide explains step-by-step how to set up the **Vapi Voice AI Agent** so you can test it directly in your browser or dial it via a real US phone number.

---

## Prerequisite: Expose Local Backend to the Internet
Vapi's servers need an internet-accessible HTTPS URL to call your backend REST tools.

1. Download & run [ngrok](https://ngrok.com/):
   ```bash
   ngrok http 8000
   ```
2. Copy your HTTPS URL from the terminal (e.g. `https://a1b2c3.ngrok-free.app`).
3. Your Vapi Server URL will be:
   `https://a1b2c3.ngrok-free.app/patients`

---

## Step 1: Log Into Vapi Dashboard
1. Go to [https://dashboard.vapi.ai](https://dashboard.vapi.ai) (Sign up for a free account if you don't have one).
2. Navigate to **Assistants** on the left menu.
3. Click **Create Assistant** -> Select **Blank Template**.

---

## Step 2: Configure Assistant Settings & Persona
1. **Name**: `Patient Intake Assistant`
2. **Model**: Select `gpt-4o` or `gpt-4o-mini` (Provider: OpenAI).
3. **Voice**: Select any natural voice (e.g., `Ellie - ElevenLabs` or `en-US-Neural`).
4. **First Message**:
   > *"Thank you for calling our clinic! My name is Sarah. I'd be happy to help you get registered today. May I start with your 10-digit phone number?"*
5. **System Prompt**:
   Copy the complete prompt from `voice-agent/system_prompt.md` into the **System Prompt** text field.

---

## Step 3: Configure Server URL (Webhook)
1. In your Assistant configuration page, locate **Server URL**.
2. Paste your ngrok URL:
   `https://a1b2c3.ngrok-free.app/patients`

---

## Step 4: Add Tool Functions to Vapi
In the Assistant page, click on the **Tools** tab and add 3 Function Tools using the JSON definitions in `voice-agent/tool_schemas.json`:

### Tool 1: `check_existing_patient`
- **Name**: `check_existing_patient`
- **Description**: `Checks if a patient already exists in the system by their 10-digit US phone number.`
- **Parameters JSON**:
```json
{
  "type": "object",
  "properties": {
    "phone_number": {
      "type": "string",
      "description": "The 10-digit US phone number (e.g. 5419199216 or (541) 919-9216)."
    }
  },
  "required": ["phone_number"]
}
```

### Tool 2: `create_patient`
- **Name**: `create_patient`
- **Description**: `Registers a new patient with full demographic, contact, and insurance details.`
- **Parameters JSON**:
```json
{
  "type": "object",
  "properties": {
    "first_name": { "type": "string" },
    "last_name": { "type": "string" },
    "date_of_birth": { "type": "string", "description": "YYYY-MM-DD" },
    "sex": { "type": "string", "enum": ["Male", "Female", "Other", "Decline to Answer"] },
    "phone_number": { "type": "string" },
    "email": { "type": "string" },
    "address_line_1": { "type": "string" },
    "address_line_2": { "type": "string" },
    "city": { "type": "string" },
    "state": { "type": "string", "description": "2-letter US state code" },
    "zip_code": { "type": "string" },
    "insurance_provider": { "type": "string" },
    "insurance_member_id": { "type": "string" },
    "preferred_language": { "type": "string" },
    "emergency_contact_name": { "type": "string" },
    "emergency_contact_phone": { "type": "string" }
  },
  "required": ["first_name", "last_name", "date_of_birth", "sex", "phone_number", "address_line_1", "city", "state", "zip_code"]
}
```

### Tool 3: `update_patient`
- **Name**: `update_patient`
- **Description**: `Updates an existing patient's details by their patient_id.`
- **Parameters JSON**:
```json
{
  "type": "object",
  "properties": {
    "patient_id": { "type": "string" },
    "first_name": { "type": "string" },
    "last_name": { "type": "string" },
    "date_of_birth": { "type": "string" },
    "sex": { "type": "string" },
    "phone_number": { "type": "string" },
    "address_line_1": { "type": "string" },
    "city": { "type": "string" },
    "state": { "type": "string" },
    "zip_code": { "type": "string" }
  },
  "required": ["patient_id"]
}
```

---

## Step 5: How to Test the Agent

### Option A: Web Browser Test (Instant & Free)
1. In the Vapi Dashboard Assistant page, click the green **"Test Call"** or **"Talk to Assistant"** button at the bottom right.
2. Grant microphone permissions in your browser.
3. Speak naturally with Sarah!
   - *Say*: *"Hi, my phone number is 541 919 9216."* -> Sarah will trigger `check_existing_patient`, find John Smith, and read back his info!
   - *Say*: *"I'd like to update my street address."* -> Sarah will ask for your address and invoke `update_patient` live!
   - Check your terminal or `logs/calls.log` to see the backend log the activity in real time.

### Option B: Real Phone Call Test (+1 Phone Number)
1. In Vapi Dashboard, navigate to **Phone Numbers** on the left sidebar.
2. Click **Buy / Import Phone Number** (or use Vapi's free test phone number).
3. Under **Inbound Assistant**, select your `Patient Intake Assistant`.
4. Dial the provisioned phone number from your cell phone!
