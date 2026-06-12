import json
import os
import re
import time
import mimetypes
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Put it in your .env file.")

client = genai.Client(api_key=API_KEY)

MODEL_ID = "gemini-2.5-flash"


TRIAGE_SYSTEM_INSTRUCTION = """
You are HELP (Humanitarian Emergency Liaison Platform), an elite autonomous AI Emergency Triage Agent.

Your singular objective is to maximize the containment and survival of any living entity (human, animal, plant) or the stability of critical non-living infrastructure experiencing a high-urgency crisis.

When analyzing user inputs, your response MUST follow this exact 5-stage layout:

1. 🚨 DISPATCH STATUS & URGENCY REPORT
   - Define the exact scenario category.
   - Assign a priority tier:
     [CRITICAL / SEVERE / MODERATE].

2. ⏱️ IMMEDIATE SECURE & CONTAINMENT INSTRUCTIONS
   - Provide 3 immediate actions the user should take to stabilize the situation safely.

3. 🗺️ CRITICAL METADATA REQUESTS
   - Request any missing information required to guide responders.

4. ⚠️ RISK MITIGATION ADVISORY
   - State one action that should be avoided to prevent worsening the situation.

5. 📡 LIVE DISPATCH ROUTING (RECOMMENDED CONTACTS)
   - Determine the most appropriate responder category.
   - Examples:
     Veterinary Services,
     Animal Rescue NGOs,
     Trauma Centers,
     Ambulance Services,
     Fire Departments,
     Police Departments,
     Utility Emergency Services.
   - Use Google Search grounding when available.
   - Provide:
       • Name
       • Phone Number (if available)
       • Email (if available)
       • Address (if available)
   - Never invent contact details.
   - Clearly state when information cannot be verified.

Additional Rules:
- Be direct and concise.
- Do not diagnose medical conditions.
- Use the image observations, text, audio, and manual notes as context.
- If image analysis was unavailable, continue using the remaining information.
- If location information is missing, explicitly request it.
- If the situation appears dangerous, state that clearly.
- Do not use conversational pleasantries.
- Maintain a calm, authoritative, urgent tone.
- Go directly into the triage blueprint.
"""


IMAGE_OBSERVATION_PROMPT = """
Look at this image and return only observable facts.

Do not diagnose.
Do not explain causes.
Do not write a paragraph.

Return valid JSON only, with these keys:

{
  "status": "ok" or "blocked" or "empty",
  "entity_type": "dog/cat/human/unknown",
  "visible_conditions": ["bleeding", "open_wound", "unable_to_stand", "traffic_hazard", ...],
  "environment_hazards": ["traffic", "road", "fire", "water", "crowd", "unknown", ...],
  "short_observation": "short plain sentence"
}

If the image is too graphic or you cannot analyze it, return:
{
  "status": "blocked",
  "entity_type": "unknown",
  "visible_conditions": [],
  "environment_hazards": [],
  "short_observation": "image analysis unavailable"
}
"""


def _normalize_bytes(file_obj):
    if file_obj is None:
        return None

    if isinstance(file_obj, (bytes, bytearray)):
        return bytes(file_obj)

    if hasattr(file_obj, "getvalue"):
        return file_obj.getvalue()

    if hasattr(file_obj, "read"):
        pos = None
        if hasattr(file_obj, "tell"):
            try:
                pos = file_obj.tell()
            except Exception:
                pos = None

        data = file_obj.read()

        if pos is not None and hasattr(file_obj, "seek"):
            try:
                file_obj.seek(pos)
            except Exception:
                pass

        return data

    raise TypeError(f"Unsupported file type: {type(file_obj)}")


def _guess_mime(filename: str | None, fallback: str) -> str:
    if not filename:
        return fallback
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or fallback


def _clean_json_text(raw_text: str) -> str:
    text = raw_text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _safe_json_loads(raw_text: str):
    try:
        return json.loads(_clean_json_text(raw_text))
    except Exception:
        return None


def _call_gemini_with_retry(contents, config, tries=3, sleep_seconds=2):
    last_error = None
    for attempt in range(tries):
        try:
            return client.models.generate_content(
                model=MODEL_ID,
                contents=contents,
                config=config,
            )
        except Exception as e:
            last_error = e
            if attempt < tries - 1:
                time.sleep(sleep_seconds)
            else:
                raise last_error


def analyze_image_observation(image_bytes, image_mime_type: str = "image/jpeg"):
    """
    Best-effort image observation step.
    Returns a dict even when the model refuses or is overloaded.
    """
    try:
        image_part = types.Part.from_bytes(
            data=_normalize_bytes(image_bytes),
            mime_type=image_mime_type or "image/jpeg",
        )

        response = _call_gemini_with_retry(
            contents=[
                image_part,
                types.Part.from_text(text=IMAGE_OBSERVATION_PROMPT),
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
            ),
        )

        if not response.text:
            return {
                "status": "blocked",
                "entity_type": "unknown",
                "visible_conditions": [],
                "environment_hazards": [],
                "short_observation": "image analysis unavailable",
            }

        parsed = _safe_json_loads(response.text)
        if isinstance(parsed, dict):
            return parsed

        return {
            "status": "empty",
            "entity_type": "unknown",
            "visible_conditions": [],
            "environment_hazards": [],
            "short_observation": response.text.strip()[:300],
        }

    except Exception as e:
        return {
            "status": "blocked",
            "entity_type": "unknown",
            "visible_conditions": [],
            "environment_hazards": [],
            "short_observation": f"image analysis failed: {e}",
        }


def build_triage_report(
    text_input: str,
    image_obs: dict | None,
    audio_bytes=None,
    audio_mime_type: str | None = None,
    manual_image_notes: str = "",
):
    context = {
        "text_input": text_input or "",
        "image_observation": image_obs or {},
        "manual_image_notes": manual_image_notes or "",
        "image_status": (image_obs or {}).get("status", "unknown"),
        "contact_goal": "identify the right kind of help and the next contact step",
    }

    parts = [
        types.Part.from_text(
            text=(
                "Here is the emergency context:\n\n"
                f"{json.dumps(context, indent=2)}\n\n"
                "Now produce the 5-part triage report."
            )
        )
    ]

    if audio_bytes:
        try:
            parts.append(
                types.Part.from_bytes(
                    data=_normalize_bytes(audio_bytes),
                    mime_type=audio_mime_type or "audio/wav",
                )
            )
        except Exception:
            pass

    config = types.GenerateContentConfig(
        system_instruction=TRIAGE_SYSTEM_INSTRUCTION,
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )

    response = _call_gemini_with_retry(
        contents=types.Content(role="user", parts=parts),
        config=config,
    )

    return response.text or "No response text returned."


def process_triage_request(
    text_input: str = "",
    image_bytes=None,
    image_mime_type: str | None = None,
    audio_bytes=None,
    audio_mime_type: str | None = None,
    manual_image_notes: str = "",
):
    """
    Single entry point used by the Streamlit app.
    """
    try:
        image_obs = None

        if image_bytes:
            image_obs = analyze_image_observation(
                image_bytes=image_bytes,
                image_mime_type=image_mime_type or "image/jpeg",
            )

        report = build_triage_report(
            text_input=text_input,
            image_obs=image_obs,
            audio_bytes=audio_bytes,
            audio_mime_type=audio_mime_type,
            manual_image_notes=manual_image_notes,
        )

        return {
            "success": True,
            "image_observation": image_obs,
            "report": report,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Processing failed: {e}",
        }


if __name__ == "__main__":
    print(process_triage_request(text_input="Test request"))