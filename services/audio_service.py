from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def transcribe_audio(
        audio_bytes,
        mime_type="audio/wav"
):

    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=mime_type
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe this emergency incident report accurately. Return only the spoken words.",
            audio_part
        ]
    )

    return response.text.strip()