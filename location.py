import requests
import streamlit as st

@st.cache_data(ttl=3600)  # Caches for 1 hour to prevent API rate limits
def get_auto_location():
    """Fetches coarse location via IP Address silently."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                city = data.get("city", "Unknown City")
                region = data.get("regionName", "Unknown Region")
                country = data.get("country", "Unknown Country")
                return f"{city}, {region}, {country}"
    except Exception:
        pass
    return "Location unavailable. Require manual input."