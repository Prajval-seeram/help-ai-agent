from twilio.rest import Client

from config.settings import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)


client = Client(
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN
)


def send_sms(
        to_phone,
        message
):

    sms = client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=to_phone
    )

    return sms.sid