import json

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

    return json.loads(text)
import json
import re

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

Analysis:
{analysis}

Return ONLY valid JSON.

Example:

{{
    "subject": "Emergency Alert",
    "body": "Email content here"
}}

Do not use markdown.
Do not add explanations.
Return JSON only.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    print("\n===== GEMINI RESPONSE =====")
    print(text)
    print("===========================\n")

    # Remove markdown if Gemini adds it
    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    # Extract JSON object
    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if not match:
        raise ValueError(
            f"Gemini returned invalid JSON:\n{text}"
        )

    return json.loads(
        match.group()
    )