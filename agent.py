import os
import io
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv()

# Initialize the modern Gemini Client
client = genai.Client()

HELP_SYSTEM_INSTRUCTION = """
You are HELP (Humanitarian Emergency Liaison Platform), an elite autonomous AI Emergency Triage Agent.
Your singular objective is to maximize the containment and survival of any living entity (human, animal, plant) or stability of critical non-living infrastructure experiencing a high-urgency crisis.

When analyzing user inputs, your response MUST follow this exact, clinical 5-stage layout:

1. 🚨 DISPATCH STATUS & URGENCY REPORT: Define the exact scenario category and assign a priority tier: [CRITICAL / SEVERE / MODERATE].
2. ⏱️ IMMEDIATE SECURE & CONTAINMENT INSTRUCTIONS: Give 3 lightning-fast step-by-step actions the user must take right now to stabilize the entity safely.
3. 🗺️ CRITICAL METADATA REQUESTS: Ask for precise follow-up information needed to guide rescue entities.
4. ⚠️ RISK MITIGATION ADVISORY: State one distinct action the user must avoid doing to prevent exacerbating the crisis.
5. 📡 LIVE DISPATCH ROUTING (ACTION INITIATED): You MUST use your Google Search tool to find the as many nearest, real-world emergency contacts (e.g., 24/7 Veterinary, Trauma Center, or Civil Authority) based on the user's stated location. Provide their exact Name, Phone Number,email and Address.

Maintain a calm, authoritative, urgent tone. Do not use conversational pleasantries like 'I am sorry to hear that' or 'How can I help you today?'. Go straight into the triage blueprint.
"""


def process_triage_request(text_prompt: str = "", image_bytes: bytes = None, audio_bytes: bytes = None):
    """
    Omni-modal triage processor. Accepts text, image bytes, and audio bytes simultaneously.
    Returns a dictionary with the report and the search queries it used.
    """
    contents_parts = []

    # 1. Process Image Input
    if image_bytes:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=85)
            safe_img_bytes = img_byte_arr.getvalue()

            contents_parts.append(types.Part.from_bytes(data=safe_img_bytes, mime_type="image/jpeg"))
        except Exception as e:
            return {"success": False, "error": f"Image processing failed: {e}"}

    # 2. Process Live Audio Input
    if audio_bytes:
        try:
            contents_parts.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"))
        except Exception as e:
            return {"success": False, "error": f"Audio processing failed: {e}"}

    # 3. Process Text Input
    if text_prompt.strip():
        contents_parts.append(types.Part.from_text(text=text_prompt))

    # Safety Check: Did the user provide ANYTHING?
    if not contents_parts:
        return {"success": False, "error": "No telemetry provided. Please input text, image, or audio."}

    # Compile the final structured payload
    structured_contents = types.Content(role="user", parts=contents_parts)

    # Configure the Search Grounding Tool
    config = types.GenerateContentConfig(
        system_instruction=HELP_SYSTEM_INSTRUCTION,
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )

    try:
        # Ping the Gemini 2.5 Flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=structured_contents,
            config=config
        )

        # --- SAFE RESPONSE PARSING ---
        search_queries = []

        # Safely drill down through the objects using getattr or checking attributes directly
        if response.candidates:
            first_candidate = response.candidates[0]
            if hasattr(first_candidate, 'grounding_metadata') and first_candidate.grounding_metadata:
                metadata = first_candidate.grounding_metadata
                if hasattr(metadata, 'web_search_queries') and metadata.web_search_queries:
                    search_queries = metadata.web_search_queries

        return {
            "success": True,
            "report": response.text if response.text else "No report text returned.",
            "queries": search_queries
        }

    except Exception as e:
        return {"success": False, "error": f"API Connection Exception: {e}"}

# Quick local test block (won't run when imported by app.py)
if __name__ == "__main__":
    print("Testing agent logic...")
    res = process_triage_request(text_prompt="Testing the omni-modal network.")
    print(res)

