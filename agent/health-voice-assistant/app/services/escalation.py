from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from app.config import get_settings

class EscalationService:
    def __init__(self):
        self.settings = None
        self.twilio_client = None

    def _get_client(self):
        if self.settings is None:
            self.settings = get_settings()
        if self.twilio_client is None:
            self.twilio_client = Client(self.settings.twilio_account_sid, self.settings.twilio_auth_token)
        return self.twilio_client

    def _escalation_numbers(self) -> list[str]:
        if self.settings is None:
            self.settings = get_settings()
        raw = self.settings.escalation_phone or ""
        return [n.strip() for n in raw.split(",") if n.strip()]

    async def alert_doctor(self, caller: str, symptoms: str) -> bool:
        try:
            client = self._get_client()
            message = f"🚨 HEALTH ALERT\nPatient: {caller}\nSymptoms: {symptoms}"
            recipients = self._escalation_numbers()
            if not recipients:
                return False

            sent_any = False
            for recipient in recipients:
                try:
                    client.messages.create(
                        body=message,
                        from_=self.settings.twilio_phone_number,
                        to=recipient,
                    )
                    sent_any = True
                except Exception:
                    continue
            if not sent_any:
                return False
            return True
        except Exception as e:
            return False

    def build_transfer_twiml(self, first_aid_message: str = "Connecting you...") -> str:
        if self.settings is None:
            self.settings = get_settings()
        response = VoiceResponse()
        recipients = self._escalation_numbers()
        primary_number = recipients[0] if recipients else None

        response.say(first_aid_message)
        if primary_number:
            response.dial(primary_number, timeout=30)
        response.say("Doctor unavailable. They've been notified. Please head to the nearest facility if urgent.")
        return str(response)

escalation = EscalationService()
