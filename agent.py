import os
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MODEL_ID, HELP_SYSTEM_INSTRUCTION, IMAGE_OBSERVATION_PROMPT


def run_triage_pipeline(user_prompt, location_data, image_path=None, audio_path=None):
    """
    Decoupled Asynchronous Pipeline.
    Pass 1: Vision (No tools, pure observation)
    Pass 2: Text/Search Dispatch (Vision Text + User Text + Tools)
    """
    if not GEMINI_API_KEY:
        return "System Error: Gemini API Key not found in .env file."

    client = genai.Client(api_key=GEMINI_API_KEY)
    vision_context = ""

    # PASS 1: The Vision Module (Bypasses inline safety blocks via Files API)
    if image_path:
        try:
            uploaded_img = client.files.upload(file=image_path)
            vision_response = client.models.generate_content(
                model=MODEL_ID,
                contents=[uploaded_img, IMAGE_OBSERVATION_PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            vision_context = f"\n[AI Visual Observation Data]: {vision_response.text}\n"
            client.files.delete(name=uploaded_img.name)  # Clean up cloud buffer
        except Exception as e:
            vision_context = f"\n[AI Visual Observation Error]: {str(e)}\n"

    # PASS 2: The Search Dispatcher (Fuses Location + Text + Pass 1 Vision)
    enhanced_prompt = f"User Location: {location_data}\nUser Report: {user_prompt}\n{vision_context}"

    try:
        dispatch_response = client.models.generate_content(
            model=MODEL_ID,
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(
                system_instruction=HELP_SYSTEM_INSTRUCTION,
                tools=[{"google_search": {}}],  # Live Grounding Activated
                temperature=0.2
            )
        )
        return dispatch_response.text
    except Exception as e:
        if "503" in str(e):
            return "HELP Core Connection Exception: 503 UNAVAILABLE. Google's servers are busy. Please wait 10 seconds and press Triage again."
        return f"HELP Core Error: {str(e)}"