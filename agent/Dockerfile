FROM python:3.11-slim

WORKDIR /app

COPY health-voice-assistant/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY health-voice-assistant/ .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
