import streamlit as st

from services.email_service import (
    send_email
)

st.title("📧 Email Test")

recipient = st.text_input(
    "Recipient Email"
)

subject = st.text_input(
    "Subject"
)

body = st.text_area(
    "Message"
)

if st.button(
    "Send Email"
):

    try:

        with st.spinner(
            "Sending Email..."
        ):

            send_email(
                recipient,
                subject,
                body
            )

        st.success(
            "Email sent successfully."
        )

    except Exception as e:

        st.error(
            str(e)
        )