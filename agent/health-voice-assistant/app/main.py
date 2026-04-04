import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api import twilio_webhooks
from app.services.session import session_mgr

app = FastAPI(title="Health Voice Assistant")

temp_audio_dir = "/tmp/health_voice_audio"
os.makedirs(temp_audio_dir, exist_ok=True)

# Mount paths
app.mount("/audio", StaticFiles(directory=temp_audio_dir), name="audio")
app.include_router(twilio_webhooks.router, prefix="/api/twilio")

@app.get("/")
def read_root():
    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Hello! Web interface not found. Ensure static/index.html exists."}

@app.get("/api/sessions")
def get_sessions():
    return session_mgr.sessions

@app.get("/health")
def health_check():
    return {"status": "ok"}
