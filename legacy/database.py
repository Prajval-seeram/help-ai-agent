import streamlit as st
from config import SUPABASE_URL, SUPABASE_KEY


def log_incident(user_id, prompt, response, location, severity="UNKNOWN"):
    """Logs the emergency incident to Supabase."""
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        # Just return silently if DB isn't fully hooked up yet
        return False

    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        data = {
            "user_id": user_id,
            "prompt": prompt,
            "response": response,
            "location": location,
            "severity": severity
        }

        supabase.table("incidents").insert(data).execute()
        return True
    except Exception as e:
        print(f"Database Logging Failed: {str(e)}")
        return False