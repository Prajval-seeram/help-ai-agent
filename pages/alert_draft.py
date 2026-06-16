import streamlit as st

from services.gemini_service import (
    generate_email_alert
)

from services.email_service import (
    send_email
)

st.title("📧 AI Emergency Alert")

incident_type = st.text_input(
    "Incident Type"
)

location = st.text_input(
    "Location"
)

description = st.text_area(
    "Description"
)

recipient = st.text_input(
    "Recipient Email"
)

if st.button("Generate Draft"):

    analysis = {
        "severity": "MEDIUM",
        "category": "Emergency",
        "recommended_action":
            "Review immediately"
    }

    with st.spinner(
        "Generating email..."
    ):

        draft = generate_email_alert(
            incident_type,
            description,
            analysis,
            location
        )

    st.session_state["subject"] = (
        draft["subject"]
    )

    st.session_state["body"] = (
        draft["body"]
    )
if (
    "subject" in st.session_state
    and
    "body" in st.session_state
):

    st.subheader(
        "Review Email"
    )

    subject = st.text_input(
        "Subject",
        value=st.session_state["subject"]
    )

    body = st.text_area(
        "Body",
        value=st.session_state["body"],
        height=300
    )

    if st.button(
        "Send Email"
    ):

        try:

            with st.spinner(
                "Sending..."
            ):

                send_email(
                    recipient,
                    subject,
                    body
                )

            st.success(
                "Email sent successfully ✅"
            )

        except Exception as e:

            st.error(
                str(e)
            )