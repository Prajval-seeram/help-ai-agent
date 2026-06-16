import hashlib
import streamlit as st

from services.incident_service import (
    create_incident,
    update_incident
)

from services.audio_service import (
    transcribe_audio
)

from services.gemini_service import (
    analyze_incident,
    generate_email_alert,
    suggest_responders
)

from services.email_service import (
    send_email
)

from config.settings import (
    TEST_EMAIL
)

# Initialize Session State
if "audio_transcript" not in st.session_state:
    st.session_state["audio_transcript"] = ""

if "email_sent" not in st.session_state:
    st.session_state["email_sent"] = False

if "last_audio_hash" not in st.session_state:
    st.session_state["last_audio_hash"] = None

st.title("🚨 Report Incident")

# Improved Top-level UI Layout
col_main, col_side = st.columns([2, 1])

with col_side:
    st.subheader("📍 Location Context")
    location_name = st.session_state.get("location_name", "No location selected")
    if location_name == "No location selected":
        st.warning("No location selected. Please establish a location before submitting.")
    else:
        st.info(f"**Assigned Location:**\n\n{location_name}")

with col_main:
    incident_type = st.selectbox(
        "Incident Type",
        [
            "Accident",
            "Medical Emergency",
            "Fire",
            "Flood",
            "Violence",
            "Missing Person",
            "Other"
        ]
    )

    st.subheader("🎤 Voice Report")

    # Native Streamlit audio input widget
    audio_value = st.audio_input(
        "Record emergency incident report"
    )

    # Automatic Transcription Trigger
    if audio_value:
        current_audio_bytes = audio_value.getvalue()
        audio_hash = hashlib.md5(current_audio_bytes).hexdigest()

        # Only transcribe if the audio hash has actually changed
        if st.session_state["last_audio_hash"] != audio_hash:
            st.session_state["last_audio_hash"] = audio_hash

            with st.spinner("🎙️ Auto-transcribing voice report..."):
                try:
                    transcript = transcribe_audio(current_audio_bytes, audio_value.type)
                    st.session_state["audio_transcript"] = transcript
                    st.success("Voice report transcribed automatically.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    # Description Field (Bound to session state to sync with audio automatically)
    description = st.text_area(
        "Describe the situation (Editable)",
        key="audio_transcript",
        help="You can manually type here, or record audio above to auto-fill this field.",
        height=150
    )

    uploaded_image = st.file_uploader(
        "Upload Image (Optional)",
        type=["jpg", "jpeg", "png"]
    )

st.markdown("---")

if st.button("Create Incident", type="primary", use_container_width=True):
    # Fallback to check the actively synced transcript state
    final_description = st.session_state.get("audio_transcript", "").strip()

    if not final_description and not audio_value:
        st.error("Please provide a text description or record a voice report.")
    elif location_name == "No location selected":
        st.error("Please select a location first.")
    else:
        incident_data = {
            "user_id": st.session_state.get("user_id"),
            "incident_type": incident_type,
            "description": final_description,
            "location_name": location_name,
            "latitude": st.session_state.get("latitude"),
            "longitude": st.session_state.get("longitude"),
            "status": "Pending"
        }

        try:
            result = create_incident(incident_data)

            if not result.data:
                st.error("Database failed to create the incident. Please try again.")
                st.stop()

            incident_id = result.data[0]["id"]

            # Reset email flag strictly upon NEW incident generation
            st.session_state["email_sent"] = False

            with st.spinner("🤖 Analyzing incident and structuring response..."):
                analysis = analyze_incident(
                    incident_type,
                    final_description
                )

                responders = suggest_responders(
                    incident_type,
                    final_description,
                    location_name,
                    analysis
                )

                draft = generate_email_alert(
                    incident_type,
                    final_description,
                    analysis,
                    location_name
                )

            update_incident(
                incident_id,
                {
                    "severity": analysis["severity"],
                    "confidence": analysis["confidence"],
                    "category": analysis["category"],
                    "recommended_action": analysis["recommended_action"]
                }
            )

            st.session_state["analysis"] = analysis
            st.session_state["responders"] = responders
            st.session_state["email_subject"] = draft["subject"]
            st.session_state["email_body"] = draft["body"]

            st.success("Incident saved and analyzed successfully ✅")

        except Exception as e:
            st.error(f"Failed: {e}")

# ==========================
# AI Assessment
# ==========================

if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]

    st.subheader("AI Assessment")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Severity", analysis['severity'])
    col_b.metric("Category", analysis['category'])
    col_c.metric("Confidence", f"{analysis['confidence']}%")

    st.write("**Recommended Action:**")
    st.info(analysis["recommended_action"])

    st.write("**Precautions:**")
    for precaution in analysis["precautions"]:
        st.write(f"• {precaution}")

# ==========================
# Suggested Responders
# ==========================

if "responders" in st.session_state:
    st.divider()
    st.subheader("🚑 Suggested Responders")

    for responder in st.session_state["responders"]["responders"]:
        with st.expander(f"Contact: {responder['name']}"):
            st.write(f"**Type:** {responder['type']}")
            st.write(f"**Phone:** {responder['phone']}")
            st.write(f"**Email:** {responder['email']}")

# ==========================
# Email Draft
# ==========================

if "email_subject" in st.session_state and "email_body" in st.session_state:
    st.divider()
    st.subheader("📧 AI Email Draft")

    subject = st.text_input(
        "Subject",
        value=st.session_state["email_subject"]
    )

    body = st.text_area(
        "Body",
        value=st.session_state["email_body"],
        height=250
    )

    st.write(f"**Recipient:** {TEST_EMAIL}")

    if st.session_state["email_sent"]:
        st.warning("⚠️ Email already sent for this incident. Create a new incident to send another alert.")
    else:
        if st.button("📨 Send Email", type="secondary"):
            try:
                with st.spinner("Sending email..."):
                    send_email(
                        TEST_EMAIL,
                        subject,
                        body
                    )
                st.session_state["email_sent"] = True
                st.success("Email sent successfully ✅")
                st.rerun()

            except Exception as e:
                st.error(f"Email failed: {e}")