from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # ── Twilio (for escalation SMS) ──────────────────────
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # ── Deepgram (STT) ──────────────────────────────────
    deepgram_api_key: str = ""

    # ── Google Gemini (LLM) ─────────────────────────────
    google_api_key: str = ""
    google_model: str = "gemini-2.0-flash"

    # ── ElevenLabs (TTS) ────────────────────────────────
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    # ── LiveKit ─────────────────────────────────────────
    livekit_url: str = ""
    livekit_api_key: str = ""
    livekit_api_secret: str = ""

    # ── Application ─────────────────────────────────────
    app_base_url: str = "http://localhost:8000"
    escalation_phone: str = ""
    environment: str = "development"

    # ── ChromaDB (RAG) ──────────────────────────────────
    chroma_persist_dir: str = "./data/chroma_db"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
