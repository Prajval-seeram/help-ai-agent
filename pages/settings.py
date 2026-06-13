import streamlit as st

st.title("⚙️ System Configuration")
st.caption("Manage API keys, User Profile, and Alert Preferences.")

st.header("1. Bring Your Own Key (BYOK)")
st.write("To prevent hitting global rate limits, users can override the default server key.")

user_api_key = st.text_input("Google Gemini API Key", type="password", placeholder="AIzaSy...")
if st.button("Save API Key"):
    st.session_state["USER_GEMINI_KEY"] = user_api_key
    st.success("API Key activated for this session.")

st.header("2. Emergency Contact Setup")
emergency_phone = st.text_input("Emergency SMS Target Phone Number", placeholder="+1234567890")
if st.button("Save Phone"):
    st.session_state["EMERGENCY_PHONE"] = emergency_phone
    st.success("Target phone saved.")

st.divider()
st.warning("Note: Full Supabase authentication is required to persist these settings between server reboots.")