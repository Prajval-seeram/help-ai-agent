import streamlit as st

from services.twilio_service import (
    send_sms
)

st.title("📱 Twilio SMS Test")

phone = st.text_input(
    "Phone Number",
    placeholder="+91XXXXXXXXXX"
)

message = st.text_area(
    "Message"
)

if st.button("Send SMS"):

    try:

        with st.spinner(
            "Sending SMS..."
        ):

            sid = send_sms(
                phone,
                message
            )

        st.success(
            f"SMS sent successfully\n\nSID: {sid}"
        )

    except Exception as e:

        st.error(
            f"Failed: {e}"
        )