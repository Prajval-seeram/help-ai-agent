import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load credentials from hidden vault
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("\n[!] CRITICAL ERROR: GEMINI_API_KEY is missing from your .env file.\n")
    client = None
else:
    client = genai.Client(api_key=api_key)

# The Core Engineering Directive (Recruiters look closely at this style)
HELP_SYSTEM_INSTRUCTION = """
You are HELP (Humanitarian Emergency Liaison Platform), an elite autonomous AI Emergency Triage Agent.
Your singular objective is to maximize the containment and survival of any living entity (human, animal, plant) or stability of critical non-living infrastructure experiencing a high-urgency crisis.

When analyzing user inputs, your response MUST follow this exact, clinical 4-stage layout:

1. 🚨 DISPATCH STATUS & URGENCY REPORT: Define the exact scenario category (e.g., Canine Medical Crisis, Structural Hazard, Human Trauma) and assign a priority tier: [CRITICAL / SEVERE / MODERATE].
2. ⏱️ IMMEDIATE SECURE & CONTAINMENT INSTRUCTIONS: Give 3 lightning-fast step-by-step actions the user must take *right now* to stabilize the entity safely without causing harm or taking legal risks.
3. 🗺️ CRITICAL METADATA REQUESTS: Ask for precise follow-up information needed to guide rescue or civic support entities (e.g., current visible injuries, environmental threats, approximate geographic landmarks).
4. ⚠️ RISK MITIGATION ADVISORY: State one distinct action the user must avoid doing under any circumstances to prevent exacerbating the crisis.

Maintain a calm, authoritative, urgent tone. Do not use conversational pleasantries like 'I am sorry to hear that' or 'How can I help you today?'. Go straight into the triage blueprint.
"""


def generate_triage_response(user_input: str) -> str:
    """
    Processes a crisis statement and routes it through the anchored HELP triage guidelines.
    """
    if not client:
        return "HELP System Core Error: Local client is unconfigured."
    try:
        # Injecting the system layout instructions dynamically via the GenerateContentConfig object
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=HELP_SYSTEM_INSTRUCTION,
                temperature=0.2  # Low variance for strict compliance with emergency rules
            )
        )
        return response.text
    except Exception as e:
        return f"HELP Core Connection Exception: {str(e)}"


if __name__ == "__main__":
    print("\n=== HELP AI Platform: Initializing Triage Stress Test ===")

    # Simulating your core concept: A street animal needing emergency stabilization
    test_crisis = "I just found a stray dog on the side of the road. It looks like it was hit by a car, it is bleeding heavily from its hind leg and crying, I do not know what to do."

    print(f"\n[Incoming Simulation Prompt]:\n'{test_crisis}'")

    triage_output = generate_triage_response(test_crisis)

    print("\n=== SYSTEM TRIAGE REASONING MATRIX GENERATED ===")
    print(triage_output)
    print("=========================================================")