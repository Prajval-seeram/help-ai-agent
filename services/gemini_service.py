import json
import re
import streamlit as st
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY

def get_gemini_client():
    api_key = (
            st.session_state.get("USER_GEMINI_KEY")
            or GEMINI_API_KEY
    )

    return genai.Client(
        api_key=api_key
    )

def analyze_incident(
        incident_type,
        description,
        image_bytes=None,
        mime_type=None
):
    prompt = f"""
You are an emergency triage AI.

Analyze the incident based on the description and any provided image evidence.
If image evidence is available, prioritize visible evidence over vague user descriptions.

Use the image to estimate:
- severity
- injuries
- visible hazards
- environmental dangers

Increase your confidence score when image evidence is clear.
Compare the image evidence with the user description. If they conflict, mention the conflict in your recommended action or category.

Incident Type:
{incident_type}

Description:
{description if description else "No text description provided. Rely entirely on visual evidence."}

Return ONLY valid JSON.

{{
  "severity": "INFORMATIONAL|LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": 0-100,
  "category": "string",
  "recommended_action": "string",
  "precautions": [
    "string",
    "string"
  ],
  "requires_emergency_dispatch": true
}}

Do not return markdown.
Do not return explanations.
Return JSON only.
"""
    contents = [prompt]
    if image_bytes and mime_type:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )
        contents.append(image_part)
    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents
    )

    text = response.text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)

def suggest_responders(
        incident_type,
        description,
        location,
        analysis
):
    prompt = f"""
You are an emergency response coordinator.

Incident Type:
{incident_type}

Description:
{description}

Location:
{location}

Analysis:
{json.dumps(analysis)}

For animal incidents:
Prefer veterinary clinics,
animal rescue organizations,
government veterinary hospitals.

For medical emergencies:
Prefer hospitals,
ambulance services,
emergency medical responders.

For fires:
Prefer fire departments,
disaster response teams.

Suggest 3 responders.

For EACH responder generate:

- name
- type
- phone
- email

Return ONLY valid JSON.

Example:

{{
  "responders": [
    {{
      "name": "ABC Hospital",
      "type": "Hospital",
      "phone": "+91XXXXXXXXXX",
      "email": "contact@abchospital.com"
    }}
  ]
}}
"""
    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)

def generate_email_alert(
        incident_type,
        description,
        analysis,
        location,
        reporter_name,
        reporter_phone
):
    prompt = f"""
Generate an emergency alert email.

Incident Type:
{incident_type}

Description:
{description}

Location:
{location}

Reporter Name:
{reporter_name}

Reporter Phone:
{reporter_phone}

Severity:
{analysis.get("severity", "Unknown")}

Category:
{analysis.get("category", "Unknown")}

Recommended Action:
{analysis.get("recommended_action", "No specific action recommended.")}

The email must request assistance and explicitly include the reporter's name, reporter's phone, incident type, location, severity, category, and recommended action.

Do NOT include precautions.
Do NOT provide medical advice.

Return ONLY valid JSON.

{{
    "subject": "Emergency Alert",
    "body": "Email content here"
}}
"""
    client = get_gemini_client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            f"Invalid Gemini response:\n{text}"
        )

    return json.loads(
        match.group()
    )