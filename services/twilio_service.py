# FILE: services/twilio_service.py
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from xml.sax.saxutils import escape

from config.settings import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)


def get_twilio_client():
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        raise ValueError("Twilio credentials are not configured in settings.")

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    # Add timeout protection safely
    if hasattr(client, 'http_client'):
        client.http_client.timeout = 15.0

    return client


def send_sms(phone_number, message):
    if not phone_number:
        raise ValueError("Phone number is required to send an SMS.")
    if not message:
        raise ValueError("Message content is required to send an SMS.")

    client = get_twilio_client()

    try:
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return msg.sid
    except TwilioRestException as e:
        raise Exception(f"Twilio API Error: {e.msg}")
    except Exception as e:
        raise Exception(f"Failed to send SMS: {str(e)}")


def make_call(phone_number, message):
    if not phone_number:
        raise ValueError("Phone number is required to make a call.")
    if not message:
        raise ValueError("Message content is required for the call.")

    client = get_twilio_client()

    # Safely escape message content to prevent invalid XML / TwiML injection
    safe_message = escape(message, {"'": "&apos;", '"': "&quot;"})
    twiml_content = f"<Response><Say>{safe_message}</Say></Response>"

    try:
        call = client.calls.create(
            twiml=twiml_content,
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER
        )
        return call.sid
    except TwilioRestException as e:
        raise Exception(f"Twilio API Error: {e.msg}")
    except Exception as e:
        raise Exception(f"Failed to make call: {str(e)}")