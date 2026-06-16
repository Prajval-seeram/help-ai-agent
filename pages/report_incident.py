# FILE: pages/report_incident.py
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
from services.twilio_service import (
    send_sms,
    make_call
)
from services.location_service import (
    get_user_location,
    geocode_location,
    reverse_geocode
)
from config.settings import (
    TEST_EMAIL,
    TEST_PHONE
)


def initialize_state():
    state_defaults = {
        "audio_transcript": "",
        "email_sent": False,
        "last_audio_hash": None,
        "location_name": "No location selected",
        "latitude": None,
        "longitude": None,
        "search_query": "",
        "manual_text_input": "",
        "incident_type": "Accident"
    }
    for key, default in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def clear_form_data():
    keys_to_remove = [
        "audio_transcript",
        "last_audio_hash",
        "manual_text_input",
        "search_query",
        "analysis",
        "responders",
        "email_subject",
        "email_body"
    ]

    for key in keys_to_remove:
        st.session_state.pop(key, None)
    st.session_state["incident_type"] = "Accident"
    st.session_state["email_sent"] = False


initialize_state()

st.title("🚨 Report Incident")

col_main, col_side = st.columns([2, 1])

with col_side:
    st.subheader("📍 Incident Location")

    has_location = st.session_state["latitude"] is not None and st.session_state["longitude"] is not None

    if has_location:
        st.success("✅ Location already selected")
        st.write(f"**Current:** {st.session_state['location_name']}")
        loc_btn_label = "🔄 Refresh Current Location"
    else:
        loc_btn_label = "📡 Use Current Location"

    if st.button(loc_btn_label, use_container_width=True):
        with st.spinner("Detecting current location..."):
            user_loc = get_user_location()
            if user_loc and user_loc.get("latitude"):
                lat = user_loc["latitude"]
                lon = user_loc["longitude"]
                st.session_state["latitude"] = lat
                st.session_state["longitude"] = lon

                rev_loc_name = reverse_geocode(lat, lon)
                if rev_loc_name:
                    st.session_state["location_name"] = rev_loc_name
                else:
                    st.session_state["location_name"] = f"Current Location ({lat:.6f}, {lon:.6f})"

                st.success("Location detected successfully!")
                st.rerun()
            else:
                st.error("Failed to detect location. Please try again or search manually.")

    st.markdown("<div style='text-align: center; margin: 10px 0;'><b>OR</b></div>", unsafe_allow_html=True)

    st.text_input("Search Location", key="search_query")
    if st.button("🔍 Search", use_container_width=True):
        query = st.session_state["search_query"]
        if query:
            with st.spinner("Searching for location..."):
                geocoded_loc = geocode_location(query)
                if geocoded_loc:
                    st.session_state["latitude"] = geocoded_loc["latitude"]
                    st.session_state["longitude"] = geocoded_loc["longitude"]
                    st.session_state["location_name"] = geocoded_loc["address"]
                    st.success("Location found!")
                    st.rerun()
                else:
                    st.error("Location not found. Please try a different search term.")
        else:
            st.warning("Please enter a location to search.")

    st.divider()

    if not has_location:
        st.warning("No location selected. Please establish a location before submitting.")
    else:
        with st.container():
            st.success(
                f"**📍 {st.session_state['location_name']}**\n\n"
                f"**Latitude:** {st.session_state['latitude']:.6f}\n\n"
                f"**Longitude:** {st.session_state['longitude']:.6f}"
            )

with col_main:
    incident_types = [
        "Accident",
        "Medical Emergency",
        "Fire",
        "Flood",
        "Violence",
        "Missing Person",
        "Other"
    ]

    st.selectbox(
        "Incident Type",
        options=incident_types,
        key="incident_type"
    )

    st.subheader("🎤 Voice Report")

    audio_value = st.audio_input(
        "Record emergency incident report"
    )

    if audio_value:
        current_audio_bytes = audio_value.getvalue()
        audio_hash = hashlib.md5(current_audio_bytes).hexdigest()

        if st.session_state["last_audio_hash"] != audio_hash:
            with st.spinner("🎙️ Auto-transcribing voice report..."):
                try:
                    transcript = transcribe_audio(current_audio_bytes, audio_value.type)
                    st.session_state["audio_transcript"] = transcript
                    st.session_state["last_audio_hash"] = audio_hash
                    st.success("Voice report transcribed automatically.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Transcription failed: {e}")

    if st.session_state.get("audio_transcript"):
        st.text_area(
            "Voice Transcript",
            value=st.session_state["audio_transcript"],
            height=100,
            disabled=True
        )

    st.text_area(
        "Text Description",
        key="manual_text_input",
        help="You can manually type here. If you also recorded audio, both will be combined when you submit.",
        height=150
    )

    uploaded_image = st.file_uploader(
        "Upload Image (Optional)",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_image:
        file_size_kb = len(uploaded_image.getvalue()) / 1024
        st.image(uploaded_image, caption="Uploaded Image Preview")
        st.caption(f"**File:** {uploaded_image.name} | **Size:** {file_size_kb:.2f} KB")

st.markdown("---")

if st.button("Create Incident", type="primary", use_container_width=True):
    audio_text = st.session_state.get("audio_transcript", "").strip()
    manual_text = st.session_state.get("manual_text_input", "").strip()

    combined_parts = []
    if manual_text:
        combined_parts.append(f"Manual Input:\n{manual_text}")
    if audio_text:
        combined_parts.append(f"Voice Transcript:\n{audio_text}")

    final_description = "\n\n".join(combined_parts)

    if not final_description and not uploaded_image:
        st.error("Please provide a text description, record a voice report, or upload an image.")
    elif st.session_state["latitude"] is None or st.session_state["longitude"] is None:
        st.error("Please select a location first.")
    else:
        incident_data = {
            "user_id": st.session_state.get("user_id"),
            "incident_type": st.session_state.get("incident_type", "Accident"),
            "description": final_description,
            "location_name": st.session_state.get("location_name", "Unknown"),
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
            st.session_state["email_sent"] = False

            with st.spinner("🤖 Analyzing incident and structuring response..."):
                image_bytes = None
                mime_type = None

                if uploaded_image:
                    image_bytes = uploaded_image.getvalue()
                    mime_type = uploaded_image.type

                analysis = analyze_incident(
                    st.session_state["incident_type"],
                    final_description,
                    image_bytes,
                    mime_type
                )

                responders = suggest_responders(
                    st.session_state["incident_type"],
                    final_description,
                    st.session_state["location_name"],
                    analysis
                )

                draft = generate_email_alert(
                    st.session_state["incident_type"],
                    final_description,
                    analysis,
                    st.session_state["location_name"]
                )

            update_incident(
                incident_id,
                {
                    "severity": analysis.get("severity", "Unknown"),
                    "confidence": analysis.get("confidence", 0),
                    "category": analysis.get("category", "Unknown"),
                    "recommended_action": analysis.get("recommended_action", "Pending")
                }
            )

            st.session_state["analysis"] = analysis
            st.session_state["responders"] = responders
            st.session_state["email_subject"] = draft.get("subject", "Emergency Alert")
            st.session_state["email_body"] = draft.get("body", "Please review the incident details.")

            st.success("Incident saved and analyzed successfully ✅")
            st.info(f"**Incident ID:** {incident_id}")
            st.info("You may review the submitted report below or create a new incident.")

        except Exception as e:
            st.error(f"Failed: {e}")

# ==========================
# New Incident
# ==========================

if "analysis" in st.session_state or "responders" in st.session_state:
    st.button(
        "➕ Create New Incident",
        use_container_width=True,
        on_click=clear_form_data
    )

if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]

    if isinstance(analysis, dict):
        st.subheader("AI Assessment")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Severity", analysis.get('severity', 'Unknown'))
        col_b.metric("Category", analysis.get('category', 'Unknown'))
        col_c.metric("Confidence", f"{analysis.get('confidence', 0)}%")

        st.write("**Recommended Action:**")
        st.info(analysis.get("recommended_action", "No recommendation provided."))

        precautions = analysis.get("precautions", [])
        if precautions:
            st.write("**Precautions:**")
            for precaution in precautions:
                st.write(f"• {precaution}")

if "responders" in st.session_state:
    st.divider()
    st.subheader("🚑 Suggested Responders")

    responders_data = st.session_state["responders"]
    if isinstance(responders_data, dict) and "responders" in responders_data:
        responders_list = responders_data["responders"]
    else:
        responders_list = []

    for idx, responder in enumerate(responders_list):
        responder_name = responder.get('name', 'Unknown Responder')
        responder_type = responder.get('type', 'Unknown Type')
        responder_phone = responder.get('phone', 'N/A')
        responder_email = responder.get('email', 'N/A')

        with st.expander(f"Contact: {responder_name}"):
            st.write(f"**Type:** {responder_type}")
            st.write(f"**Phone:** {responder_phone}")
            st.write(f"**Email:** {responder_email}")

            action_col1, action_col2, action_col3 = st.columns(3)

            with action_col1:
                if st.button("📧 Email", key=f"email_{idx}", use_container_width=True):
                    try:
                        if not TEST_EMAIL:
                            st.error("TEST_EMAIL is not configured.")
                        else:
                            with st.spinner(f"Sending email to {TEST_EMAIL}..."):
                                subject = f"Emergency Alert for {responder_name}"
                                body = st.session_state.get("email_body", "An emergency has been reported.")
                                send_email(TEST_EMAIL, subject, body)
                            st.success(f"Email successfully routed to testing address ({TEST_EMAIL}).")
                    except Exception as e:
                        st.error(f"Email failed: {e}")

            with action_col2:
                if st.button("📱 SMS", key=f"sms_{idx}", use_container_width=True):
                    try:
                        if not TEST_PHONE:
                            st.error("TEST_PHONE is not configured.")
                        else:
                            with st.spinner(f"Sending SMS to {TEST_PHONE}..."):
                                incident_type = st.session_state.get("incident_type", "Unknown")
                                analysis_data = st.session_state.get("analysis", {})
                                severity = analysis_data.get("severity", "Unknown") if isinstance(analysis_data,
                                                                                                  dict) else "Unknown"
                                loc = st.session_state.get("location_name", "Unknown Location")

                                desc_full = st.session_state.get("manual_text_input", "") or st.session_state.get(
                                    "audio_transcript", "")
                                desc_snippet = desc_full[:100] + "..." if len(desc_full) > 100 else desc_full
                                if not desc_snippet.strip():
                                    desc_snippet = "No text description provided."

                                sms_message = f"EMERGENCY: {incident_type}\nSeverity: {severity}\nLocation: {loc}\nDetails: {desc_snippet}"
                                send_sms(TEST_PHONE, sms_message)
                            st.success(f"SMS successfully routed to testing number ({TEST_PHONE}).")
                    except Exception as e:
                        st.error(f"SMS failed: {e}")

            with action_col3:
                if st.button("📞 Call", key=f"call_{idx}", use_container_width=True):
                    try:
                        if not TEST_PHONE:
                            st.error("TEST_PHONE is not configured.")
                        else:
                            with st.spinner(f"Calling {TEST_PHONE}..."):
                                incident_type = st.session_state.get("incident_type", "Unknown")
                                analysis_data = st.session_state.get("analysis", {})
                                severity = analysis_data.get("severity", "Unknown") if isinstance(analysis_data,
                                                                                                  dict) else "Unknown"
                                loc = st.session_state.get("location_name", "Unknown Location")

                                call_message = f"Attention. An emergency has been reported. Incident type: {incident_type}. Severity: {severity}. Location: {loc}. Please respond immediately."
                                make_call(TEST_PHONE, call_message)
                            st.success(f"Call successfully initiated to testing number ({TEST_PHONE}).")
                    except Exception as e:
                        st.error(f"Call failed: {e}")

if "email_subject" in st.session_state and "email_body" in st.session_state:
    st.divider()
    st.subheader("📧 AI Email Draft")

    subject = st.text_input(
        "Subject",
        value=st.session_state.get("email_subject", "")
    )

    body = st.text_area(
        "Body",
        value=st.session_state.get("email_body", ""),
        height=250
    )

    st.write(f"**Recipient:** {TEST_EMAIL}")

    if st.session_state.get("email_sent", False):
        st.warning("⚠️ Email already sent for this incident. Create a new incident to send another alert.")
    else:
        if st.button("📨 Send Email", type="secondary"):
            try:
                if not TEST_EMAIL:
                    st.error("TEST_EMAIL is not configured.")
                else:
                    with st.spinner("Sending email..."):
                        send_email(TEST_EMAIL, subject, body)
                    st.session_state["email_sent"] = True
                    st.success("Email sent successfully ✅")
                    st.rerun()
            except Exception as e:
                st.error(f"Email failed: {e}")