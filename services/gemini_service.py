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