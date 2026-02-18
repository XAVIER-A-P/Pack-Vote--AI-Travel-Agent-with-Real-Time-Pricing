import os
from twilio.rest import Client

def send_sms(to_number: str, body: str):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    try:
        message = client.messages.create(
            body=body,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to_number
        )
        return message.sid
    except Exception as e:
        print(f"Failed to send SMS: {e}")