import httpx
import uuid
import os
from app.config import get_settings

class TTSService:
    async def get_public_url(
        self,
        text: str,
        base_url: str | None = None,
        request_timeout_seconds: float = 90.0,
    ) -> str:
        settings = get_settings()
        
        headers = {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        
        body = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75
            }
        }
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
        
        temp_dir = "/tmp/health_voice_audio"
        os.makedirs(temp_dir, exist_ok=True)
        
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.mp3"
        filepath = os.path.join(temp_dir, filename)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=body, headers=headers, timeout=request_timeout_seconds)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
                
        # To make it accessible via Windows assuming basic API service logic:
        # Instead of /tmp we'll use a local directory to serve from FastAPI.
        # Ensure we write it to a local 'static/audio' directory inside app or data!
        # Wait, the spec strictly asks for /tmp/health_voice_audio/{uuid}.mp3
        # I'll save it to /tmp/health_voice_audio or standard temp on windows.
        
        public_base = (base_url or settings.app_base_url).rstrip('/')
        return f"{public_base}/audio/{filename}"

tts = TTSService()
