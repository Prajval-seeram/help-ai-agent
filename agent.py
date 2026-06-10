import os
from google import genai
from dotenv import load_dotenv

# Load security environment variables from local vault
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key or api_key == "AIzaSyYourActualSecretKeyHere":
    print("\n[!] CRITICAL ERROR: GEMINI_API_KEY is missing or invalid in your .env file.")
    print("Please ensure an exact file named '.env' exists in your project folder with a valid key.\n")
    client = None
else:
    # Modern SDK client initialization standard
    client = genai.Client(api_key=api_key)


def generate_triage_response(user_input: str) -> str:
    """
    Sends raw input to the HELP core brain using the current flagship model.
    """
    if not client:
        return "HELP System Engine Error: Core API client is unconfigured."
    try:
        # Utilizing flagship high-speed real-time processing model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
        )
        return response.text
    except Exception as e:
        return f"HELP System Engine Error connecting to core: {str(e)}"


# Isolated execution handshake check
if __name__ == "__main__":
    print("=== HELP AI Core: Initializing Modern System Handshake Check ===")
    test_prompt = "System check protocol. Confirm your active engine identity."
    print(f"Sending Probe: '{test_prompt}'")

    analysis = generate_triage_response(test_prompt)

    print("\n=== Core Response Received ===")
    print(analysis)
    print("=========================================================")