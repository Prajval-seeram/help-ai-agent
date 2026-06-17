# FILE: report_incident.py
import hashlib
import folium
import streamlit as st
from streamlit_folium import st_folium

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
        "incident_type": "Accident",
        "reporter_name": "",
        "reporter_phone": "",
        "uploader_key": 0,
        "m_center": [20.5937, 78.9629]  # Default view centered broadly on India
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
    st.session_state["uploader_key"] += 1


initialize_state()

st.title("🚨 Report Incident")

col_main, col_side = st.columns([2, 1])

with col_side:
    st.subheader("📍 Incident Location")

    st.text_input("Search Location", key="search_query")
    if st.button("🔍 Search", use_container_width=True):
        query = st.session_state.get("search_query", "")
        if query:
            with st.spinner("Searching for location..."):
                geocoded_loc = geocode_location(query)
                if geocoded_loc:
                    st.session_state["latitude"] = geocoded_loc["latitude"]
                    st.session_state["longitude"] = geocoded_loc["longitude"]
                    st.session_state["location_name"] = geocoded_loc["address"]
                    st.session_state["m_center"] = [geocoded_loc["latitude"], geocoded_loc["longitude"]]
                    st.session_state["m_marker"] = [geocoded_loc["latitude"], geocoded_loc["longitude"]]
                    st.rerun()
                else:
                    st.error("Location not found. Please try a different search term.")
        else:
            st.warning("Please enter a location to search.")

    mc = st.session_state.get("m_center")
    m = folium.Map(location=mc, zoom_start=12)

    if "m_marker" in st.session_state:
        folium.Marker(st.session_state["m_marker"]).add_to(m)

    map_data = st_folium(m, height=350, use_container_width=True, key="incident_map")

    if map_data and map_data.get("last_clicked"):
        click_lat = map_data["last_clicked"]["lat"]
        click_lon = map_data["last_clicked"]["lng"]

        with st.spinner("Identifying location..."):
            addr = reverse_geocode(click_lat, click_lon)
            loc_name = addr if addr else f"Lat: {click_lat:.6f}, Lon: {click_lon:.6f}"

            st.session_state["latitude"] = click_lat
            st.session_state["longitude"] = click_lon
            st.session_state["location_name"] = loc_name
            st.session_state["m_center"] = [click_lat, click_lon]
            st.session_state["m_marker"] = [click_lat, click_lon]
            st.rerun()

    st.divider()

    has_location = st.session_state.get("latitude") is not None and st.session_state.get("longitude") is not None

    if not has_location:
        st.warning("No location selected. Please establish a location before submitting.")
    else:
        with st.container():
            st.success("✅ Location Selected Successfully")
            st.write(
                f"**Selected Location:** {st.session_state.get('location_name', 'Unknown')}\n\n"
                f"**Latitude:** {st.session_state.get('latitude', 0.0):.6f}\n\n"
                f"**Longitude:** {st.session_state.get('longitude', 0.0):.6f}"
            )


with col_main:
    st.subheader("👤 Reporter Information")
    st.text_input("Reporter Name (Optional)", key="reporter_name")
    st.text_input("Reporter Phone Number (Optional)", key="reporter_phone")

    st.subheader("📋 Incident Details")
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

        if st.session_state.get("last_audio_hash") != audio_hash:
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
        type=["jpg", "jpeg", "png"],
        key=f"image_uploader_{st.session_state.get('uploader_key', 0)}"
    )

    if uploaded_image:
        file_size_kb = len(uploaded_image.getvalue()) / 1024
        st.image(uploaded_image, caption="Uploaded Image Preview")
        st.caption(f"**File:** {uploaded_image.name} | **Size:** {file_size_kb:.2f} KB")

st.markdown("---")

if st.button("Create Incident", type="primary", use_container_width=True):
    audio_text = st.session_state.get("audio_transcript", "").strip()
    manual_text = st.session_state.get("manual_text_input", "").strip()

    r_name = st.session_state.get("reporter_name", "").strip()
    r_phone = st.session_state.get("reporter_phone", "").strip()

    combined_parts = []
    if manual_text:
        combined_parts.append(f"Manual Input:\n{manual_text}")
    if audio_text:
        combined_parts.append(f"Voice Transcript:\n{audio_text}")

    final_description = "\n\n".join(combined_parts)

    if not final_description and not uploaded_image:
        st.error("Please provide a text description, record a voice report, or upload an image.")
    elif st.session_state.get("latitude") is None or st.session_state.get("longitude") is None:
        st.error("Please select a location first.")
    else:
        incident_data = {
            "user_id": st.session_state.get("user_id"),
            "reporter_name": r_name if r_name else None,
            "reporter_phone": r_phone if r_phone else None,
            "incident_type": st.session_state.get("incident_type", "Accident"),
            "description": final_description,
            "location_name": st.session_state.get("location_name", "Unknown"),
            "latitude": st.session_state.get("latitude"),
            "longitude": st.session_state.get("longitude"),
            "status": "Pending"
        }

        try:
            result = create_incident(incident_data)

            if not result or not getattr(result, "data", None) or len(result.data) == 0:
                st.error("Database failed to create the incident. Please try again.")
                st.stop()

            incident_id = result.data[0].get("id")
            if not incident_id:
                st.error("Database returned an invalid incident ID.")
                st.stop()

            st.session_state["email_sent"] = False

            with st.spinner("🤖 Analyzing incident and structuring response..."):
                image_bytes = None
                mime_type = None

                if uploaded_image:
                    image_bytes = uploaded_image.getvalue()
                    mime_type = uploaded_image.type

                analysis = analyze_incident(
                    st.session_state.get("incident_type", "Unknown"),
                    final_description,
                    image_bytes,
                    mime_type
                )

                responders = suggest_responders(
                    st.session_state.get("incident_type", "Unknown"),
                    final_description,
                    st.session_state.get("location_name", "Unknown"),
                    analysis
                )

                r_name_display = r_name if r_name else "Not Provided"
                r_phone_display = r_phone if r_phone else "Not Provided"

                draft = generate_email_alert(
                    st.session_state.get("incident_type", "Unknown"),
                    final_description,
                    analysis,
                    st.session_state.get("location_name", "Unknown"),
                    r_name_display,
                    r_phone_display
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


if "analysis" in st.session_state or "responders" in st.session_state:
    st.button(
        "➕ Create New Incident",
        use_container_width=True,
        on_click=clear_form_data
    )


if "analysis" in st.session_state:
    analysis = st.session_state.get("analysis", {})

    if isinstance(analysis, dict):
        st.subheader("AI Assessment")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Severity", analysis.get('severity', 'Unknown'))
        col_b.metric("Category", analysis.get('category', 'Unknown'))
        col_c.metric("Confidence", f"{analysis.get('confidence', 0)}%")

        st.write("**Recommended Action:**")
        st.info(analysis.get("recommended_action", "No recommendation provided."))

        precautions = analysis.get("precautions", [])
        if precautions and isinstance(precautions, list):
            st.write("**Precautions:**")
            for precaution in precautions:
                st.write(f"• {precaution}")


if "responders" in st.session_state:
    st.divider()
    st.subheader("🚑 Suggested Responders")

    responders_data = st.session_state.get("responders", {})
    if isinstance(responders_data, dict) and "responders" in responders_data:
        responders_list = responders_data.get("responders", [])
    else:
        responders_list = []

    for idx, responder in enumerate(responders_list):
        if not isinstance(responder, dict):
            continue

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
                                i_type = st.session_state.get("incident_type", "Unknown")
                                a_data = st.session_state.get("analysis", {})
                                a_sev = a_data.get("severity", "Unknown") if isinstance(a_data, dict) else "Unknown"
                                a_act = a_data.get("recommended_action", "Unknown") if isinstance(a_data, dict) else "Unknown"
                                a_loc = st.session_state.get("location_name", "Unknown")

                                rep_p = st.session_state.get("reporter_phone", "").strip()
                                rep_p_display = rep_p if rep_p else "Not Provided"

                                short_act = a_act[:60] + "..." if len(a_act) > 60 else a_act
                                sms_message = f"EMERGENCY: {i_type}\nSev: {a_sev}\nLoc: {a_loc}\nRep: {rep_p_display}\nAct: {short_act}"
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
                                a_data = st.session_state.get("analysis", {})
                                a_sev = a_data.get("severity", "Unknown") if isinstance(a_data, dict) else "Unknown"
                                a_loc = st.session_state.get("location_name", "Unknown Location")

                                rep_p = st.session_state.get("reporter_phone", "").strip()
                                phone_text = f" Reporter phone {rep_p}." if rep_p else ""

                                call_message = f"Emergency reported. Severity {a_sev}. Location: {a_loc}.{phone_text} Immediate assistance required."
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