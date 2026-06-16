import json
import re
from google import genai
from config.settings import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_incident(
        incident_type,
        description
):
    prompt = f"""
You are an emergency triage AI.

Analyze the incident.

Incident Type:
{incident_type}

Description:
{description}

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

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
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
{analysis}

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
        location
):
    prompt = f"""
Generate an emergency alert email.

Incident Type:
{incident_type}

Description:
{description}

Location:
{location}

Severity:
{analysis["severity"]}

Category:
{analysis["category"]}

Recommended Action:
{analysis["recommended_action"]}

The email should request assistance.

Do NOT include precautions.
Do NOT provide medical advice.

Return ONLY valid JSON.

{{
    "subject": "Emergency Alert",
    "body": "Email content here"
}}
"""

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