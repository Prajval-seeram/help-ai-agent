import streamlit as st
from services.auth_service import (
    get_user_profile,
    accept_terms,
    sign_out
)

st.set_page_config(
    page_title="HELP",
    page_icon="🚨",
    layout="wide"
)


# ==================================================
# TERMS OF USE POPUP
# ==================================================
@st.dialog("🚨 Terms of Use & Safety Acknowledgement")
def terms_popup(user_id):
    st.write("HELP is an educational and demonstration project.")
    st.markdown(
        """
        • HELP does not replace emergency services.
        • Contact emergency responders immediately during real emergencies.
        • AI-generated recommendations, assessments, responder suggestions, emails, SMS messages, and call content may contain inaccuracies.
        • Location data, uploaded images, audio recordings, incident descriptions, contact information, and generated communications may be stored and processed by the platform.
        • Users are responsible for verifying information before acting on recommendations.
        • HELP is provided without guarantees regarding accuracy, availability, reliability, or emergency response outcomes.
        """
    )

    agreed = st.checkbox("I have read and agree to these terms.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue", type="primary"):
            if agreed:
                accept_terms(user_id)
                st.session_state["accepted_terms"] = True
                st.rerun()
            else:
                st.error("You must agree to the terms to continue.")
    with col2:
        if st.button("Logout"):
            sign_out()
            st.session_state.clear()
            st.rerun()


# Check authentication state and terms acceptance
user_id = st.session_state.get("user_id")

if user_id:

    if user_id and not st.session_state.get("accepted_terms", False):
        try:
            profile_response = get_user_profile(user_id)
            user_data = profile_response.data if hasattr(profile_response, 'data') else profile_response

            if user_data and not user_data.get("accepted_terms", False):
                terms_popup(user_id)
            else:
                st.session_state["accepted_terms"] = True
        except Exception as e:
                st.error(
                    f"Failed to load profile: {e}"
                )

st.title("🚨 HELP")
st.subheader("Humanitarian Emergency Liaison Platform")

st.markdown(
    """
AI-powered emergency incident reporting and response assistance.

HELP combines Artificial Intelligence, Incident Reporting,
Image Analysis, Voice Transcription, and Emergency Communication
into a single platform designed to assist during critical situations.
"""
)

st.divider()

# ==================================================
# OVERVIEW
# ==================================================

st.header("🌍 What is HELP?")

st.write(
    """
HELP is an AI-powered emergency assistance platform that helps users:

- Report incidents quickly
- Analyze emergency situations using AI
- Upload images for visual assessment
- Record voice reports
- Find appropriate responders
- Send emergency notifications
- Track incidents through a dashboard

The goal is to make emergency reporting faster, clearer, and more actionable.
"""
)

st.divider()

# ==================================================
# FEATURES
# ==================================================

st.header("🌟 Core Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(
        """
📍 Location Selection

Search locations and pinpoint incidents using an interactive map.
"""
    )

    st.info(
        """
🎤 Voice Reports

Record emergency reports and automatically convert speech into text.
"""
    )

    st.info(
        """
📝 Text Reporting

Submit detailed incident descriptions manually.
"""
    )

with col2:
    st.info(
        """
🖼️ Image Analysis

Upload images and let Gemini Vision analyze visible hazards and risks.
"""
    )

    st.info(
        """
🤖 AI Incident Assessment

Automatically determine severity, category, confidence, and recommended actions.
"""
    )

    st.info(
        """
🚑 Responder Recommendations

Receive suggested hospitals, emergency responders, and support services.
"""
    )

with col3:
    st.info(
        """
📧 Email Alerts

Generate and send structured emergency reports.
"""
    )

    st.info(
        """
📱 SMS Notifications

Send concise emergency summaries through Twilio.
"""
    )

    st.info(
        """
📞 Voice Call Alerts

Generate emergency call notifications for rapid communication.
"""
    )

st.divider()

# ==================================================
# PAGES OVERVIEW
# ==================================================

st.header("🧭 Pages Overview")

st.markdown(
    """
### 🚨 Report Incident

Create emergency reports using:

- Text
- Voice
- Images
- Interactive Location Selection

Generate AI assessments and contact responders.

---

### 📊 Dashboard

View:

- Reported incidents
- Severity distribution
- Incident history
- Analytics and summaries

---

### ⚙️ Settings

Manage:

- Gemini API Key (BYOK)
- Account Settings
- Logout

---

### 🔄 Create New Incident

After submitting an incident:

- Clear previous report data
- Start a fresh report
- Keep saved location and reporter details
"""
)

st.divider()

# ==================================================
# BYOK
# ==================================================

st.header("🔑 Bring Your Own Key (BYOK)")

st.write(
    """
Advanced users can optionally provide their own Gemini API key
through the Settings page.

Benefits:

- Uses your personal Gemini quota
- Reduces dependence on shared API limits
- Useful during high usage periods

If no personal key is provided, HELP automatically uses the default server key.
"""
)

st.divider()

# ==================================================
# HOW TO USE
# ==================================================

st.header("📖 How To Use HELP")

st.info(
    """
1️⃣ Open Report Incident

2️⃣ Search and select a location on the map

3️⃣ Add incident information using:
   • Text
   • Voice Recording
   • Images

4️⃣ Click Create Incident

5️⃣ Review the AI-generated assessment

6️⃣ Contact responders using:
   • Email
   • SMS
   • Voice Call

7️⃣ Monitor incidents through the Dashboard
"""
)

st.divider()

# ==================================================
# TECHNOLOGY STACK
# ==================================================

st.header("🛠️ Technology Stack")

col1, col2, col3, col4 = st.columns(4)

col1.metric("AI", "Gemini")
col2.metric("Database", "Supabase")
col3.metric("Notifications", "Twilio")
col4.metric("Frontend", "Streamlit")

st.divider()

# ==================================================
# STATUS
# ==================================================

st.header("✅ System Status")

st.success(
    """
HELP is operational and ready for incident reporting,
AI analysis, responder recommendations, and emergency communications.
"""
)

st.divider()

# ==================================================
# DISCLAIMER
# ==================================================

st.warning(
    """
⚠️ DISCLAIMER

HELP is an educational and demonstration platform.

The system assists with:

• Emergency reporting
• Incident analysis
• Communication support
• Responder recommendations

HELP does not replace official emergency services.

Always contact local emergency responders immediately in real emergencies.
"""
)