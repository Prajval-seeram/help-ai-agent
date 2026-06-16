import streamlit as st

from services.incident_service import (
    create_incident,
    update_incident
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

st.title("🚨 Report Incident")

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

description = st.text_area(
    "Describe the situation"
)

uploaded_image = st.file_uploader(
    "Upload Image (Optional)",
    type=["jpg", "jpeg", "png"]
)

st.subheader("Selected Location")

location_name = st.session_state.get(
    "location_name",
    "No location selected"
)

st.write(location_name)

if st.button("Create Incident"):

    if not description:

        st.error(
            "Please provide a description."
        )

    elif location_name == "No location selected":

        st.error(
            "Please select a location first."
        )

    else:

        incident_data = {
            "user_id": st.session_state.get("user_id"),
            "incident_type": incident_type,
            "description": description,
            "location_name": location_name,
            "latitude": st.session_state.get("latitude"),
            "longitude": st.session_state.get("longitude"),
            "status": "Pending"
        }

        try:

            result = create_incident(
                incident_data
            )

            incident_id = result.data[0]["id"]

            with st.spinner(
                "🤖 Analyzing incident..."
            ):

                analysis = analyze_incident(
                    incident_type,
                    description
                )

                responders = suggest_responders(
                    incident_type,
                    description,
                    location_name
                )

                draft = generate_email_alert(
                    incident_type,
                    description,
                    analysis,
                    location_name
                )

            update_incident(
                incident_id,
                {
                    "severity":
                        analysis["severity"],

                    "confidence":
                        analysis["confidence"],

                    "category":
                        analysis["category"],

                    "recommended_action":
                        analysis["recommended_action"]
                }
            )

            st.session_state["analysis"] = analysis

            st.session_state["responders"] = responders

            st.session_state["email_subject"] = (
                draft["subject"]
            )

            st.session_state["email_body"] = (
                draft["body"]
            )

            st.success(
                "Incident saved and analyzed successfully ✅"
            )

        except Exception as e:

            st.error(
                f"Failed: {e}"
            )

# ==========================
# AI Assessment
# ==========================

if "analysis" in st.session_state:

    analysis = st.session_state["analysis"]

    st.subheader(
        "AI Assessment"
    )

    st.write(
        f"Severity: {analysis['severity']}"
    )

    st.write(
        f"Category: {analysis['category']}"
    )

    st.write(
        f"Confidence: {analysis['confidence']}%"
    )

    st.write(
        "Recommended Action:"
    )

    st.info(
        analysis["recommended_action"]
    )

    st.subheader(
        "Precautions"
    )

    for precaution in analysis[
        "precautions"
    ]:

        st.write(
            f"• {precaution}"
        )

# ==========================
# Suggested Responders
# ==========================

if "responders" in st.session_state:

    st.divider()

    st.subheader(
        "🚑 Suggested Responders"
    )

    for responder in st.session_state[
        "responders"
    ]["responders"]:

        st.write(
            f"**{responder['name']}**"
        )

        st.write(
            f"Type: {responder['type']}"
        )

        st.write(
            f"Phone: {responder['phone']}"
        )

        st.write(
            f"Email: {responder['email']}"
        )

        st.write("---")

# ==========================
# Email Draft
# ==========================

if (
    "email_subject" in st.session_state
    and
    "email_body" in st.session_state
):

    st.divider()

    st.subheader(
        "📧 AI Email Draft"
    )

    subject = st.text_input(
        "Subject",
        value=st.session_state[
            "email_subject"
        ]
    )

    body = st.text_area(
        "Body",
        value=st.session_state[
            "email_body"
        ],
        height=300
    )

    st.write(
        f"Recipient: {TEST_EMAIL}"
    )

    if st.button(
        "📨 Send Email"
    ):

        try:

            with st.spinner(
                "Sending email..."
            ):

                send_email(
                    TEST_EMAIL,
                    subject,
                    body
                )

            st.success(
                "Email sent successfully ✅"
            )

        except Exception as e:

            st.error(
                f"Email failed: {e}"
            )