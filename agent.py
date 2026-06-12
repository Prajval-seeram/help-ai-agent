import os
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

HELP_SYSTEM_INSTRUCTION = """
You are HELP (Humanitarian Emergency Liaison Platform), an emergency triage agent.

Follow this exact 5-stage layout:

1. 🚨 DISPATCH STATUS & URGENCY REPORT
   - Classify the situation as CRITICAL, SEVERE, or MODERATE.

2. ⏱️ IMMEDIATE SECURE & CONTAINMENT INSTRUCTIONS
   - Give 3 clear, immediate actions.

3. 🗺️ CRITICAL METADATA REQUESTS
   - Ask for the exact missing details needed for rescue/dispatch.

4. ⚠️ RISK MITIGATION ADVISORY
   - State one dangerous action to avoid.

5. 📡 LIVE DISPATCH ROUTING
   - If location is present, use Google Search grounding to find relevant nearby emergency contacts when possible.
   - Provide name, phone number, and address when available.

Rules:
- Be direct and urgent.
- Do not add fluff.
- If the situation sounds life-threatening, tell the user to call local emergency services immediately.
- If a detail is missing, ask for it clearly.
"""


def _normalize_bytes(file_obj):
    """Return raw bytes from bytes / UploadedFile / file-like objects."""
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


def process_triage_request(
    text_input: str = "",
    image_bytes=None,
    image_mime_type: str | None = None,
    audio_bytes=None,
    audio_mime_type: str | None = None,
):
    """
    Multimodal triage processor for text, image, and audio.
    Returns dict with: success, report, queries, error
    """
    parts = []

    if image_bytes:
        try:
            raw_img = _normalize_bytes(image_bytes)
            if raw_img:
                parts.append(
                    types.Part.from_bytes(
                        data=raw_img,
                        mime_type=image_mime_type or "image/jpeg",
                    )
                )
        except Exception as e:
            return {"success": False, "error": f"Image processing failed: {e}"}

    if audio_bytes:
        try:
            raw_audio = _normalize_bytes(audio_bytes)
            if raw_audio:
                parts.append(
                    types.Part.from_bytes(
                        data=raw_audio,
                        mime_type=audio_mime_type or "audio/wav",
                    )
                )
        except Exception as e:
            return {"success": False, "error": f"Audio processing failed: {e}"}

    if text_input and text_input.strip():
        parts.append(types.Part.from_text(text=text_input.strip()))

    if not parts:
        return {"success": False, "error": "No input provided. Add text, image, or audio."}

    config = types.GenerateContentConfig(
        system_instruction=HELP_SYSTEM_INSTRUCTION,
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=types.Content(role="user", parts=parts),
            config=config,
        )

        search_queries = []
        try:
            candidate = response.candidates[0] if response.candidates else None
            if candidate and getattr(candidate, "grounding_metadata", None):
                md = candidate.grounding_metadata
                if getattr(md, "web_search_queries", None):
                    search_queries = list(md.web_search_queries)
        except Exception:
            pass

        return {
            "success": True,
            "report": response.text if response.text else "No response text returned.",
            "queries": search_queries,
        }

    except Exception as e:
        return {"success": False, "error": f"Gemini API error: {e}"}


if __name__ == "__main__":
    print(process_triage_request(text_input="Test triage request"))