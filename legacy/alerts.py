import streamlit as st
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE


def send_emergency_sms(to_number, message_body):
    """Sends an SMS alert via Twilio if configured."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE]):
        st.warning("Twilio credentials missing in .env. SMS skipped.")
        return False

    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_FROM_PHONE,
            to=to_number
        )
        return True
    except Exception as e:
        st.error(f"SMS Dispatch Failed: {str(e)}")
        return False