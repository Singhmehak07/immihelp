# 🏥 ImmiHelp — AI Health Voice Assistant

> An AI-powered voice assistant that provides real-time symptom analysis and medical guidance over phone calls, built with FastAPI, Twilio, Deepgram, Google Gemini, and ElevenLabs.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Knowledge Base](#knowledge-base)
- [Services](#services)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**ImmiHelp** is a voice-based AI health assistant that callers can reach via a phone number. It listens to their symptoms, analyzes them using a RAG (Retrieval-Augmented Generation) pipeline backed by a curated medical knowledge base, and provides:

- **Personalized home-care advice** for mild/manageable conditions
- **Automatic escalation** (SMS alerts + call transfer to healthcare providers) for critical/emergency situations
- **Multilingual support** — English and Hindi with auto-detection
- **Follow-up conversations** to gather more symptom details
- **Natural-sounding speech** via ElevenLabs text-to-speech

---

## Architecture

```
┌──────────────┐       ┌──────────────────────────────────────────────────┐
│   Caller's   │       │              FastAPI Backend                     │
│    Phone     │       │                                                  │
│              │◄─────►│  Twilio Webhooks                                 │
│              │ TwiML │    │                                             │
└──────────────┘       │    ├── /incoming-call    → Greeting + Record     │
                       │    ├── /process-recording → Full Pipeline        │
                       │    └── /follow-up         → Gather-based Q&A     │
                       │                                                  │
                       │  Pipeline:                                       │
                       │    ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐       │
                       │    │ STT │──►│ RAG │──►│ LLM │──►│ TTS │       │
                       │    └─────┘   └─────┘   └─────┘   └─────┘       │
                       │   Deepgram   ChromaDB   Gemini   ElevenLabs     │
                       │              + Gemini    Flash                   │
                       │              Embeddings                          │
                       └──────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | Async web server & API |
| **Telephony** | Twilio Voice | Call handling, recording, TwiML |
| **Speech-to-Text** | Deepgram Nova-2 | Transcription with language detection |
| **LLM** | Google Gemini (Flash) | Symptom analysis & medical reasoning |
| **Embeddings** | Gemini Embedding 001 | Document vectorization |
| **Vector Store** | ChromaDB | Semantic search over medical protocols |
| **Text-to-Speech** | ElevenLabs Multilingual v2 | Natural voice responses |
| **Orchestration** | LangChain | RAG pipeline & document processing |

---

## Project Structure

```
immihelp/
├── Dockerfile                          # Root Dockerfile (for Railway)
├── railway.toml                        # Railway deployment config
└── health-voice-assistant/
    ├── .env                            # Environment variables
    ├── .gitignore
    ├── Dockerfile                      # App-level Dockerfile
    ├── requirements.txt                # Python dependencies
    ├── static/
    │   └── index.html                  # Web dashboard
    ├── data/
    │   └── chroma_db/                  # Persisted vector store
    ├── tests/                          # Test suite
    └── app/
        ├── __init__.py
        ├── main.py                     # FastAPI app entry point
        ├── config.py                   # Pydantic settings & config
        ├── api/
        │   └── twilio_webhooks.py      # Twilio webhook endpoints
        ├── services/
        │   ├── stt.py                  # Speech-to-Text (Deepgram)
        │   ├── rag.py                  # RAG retrieval service
        │   ├── llm.py                  # LLM analysis (Gemini)
        │   ├── tts.py                  # Text-to-Speech (ElevenLabs)
        │   ├── escalation.py           # Emergency escalation (SMS + call transfer)
        │   └── session.py              # In-memory session management
        ├── prompts/
        │   └── system.py               # System prompt for Gemini
        └── knowledge_base/
            ├── loader.py               # Document loader & chunker
            ├── store.py                # ChromaDB vector store
            └── documents/              # 23 medical protocol files
                ├── 01_emergency_signs.md
                ├── 02_fever.md
                ├── 03_diarrhea.md
                ├── ...
                └── otc.md
```

---

## How It Works

### Call Flow

1. **Caller dials the Twilio number** → Twilio hits `/api/twilio/incoming-call`
2. **Greeting is played** → "Welcome to ImmiHelp..." → Recording starts after beep
3. **Caller describes symptoms** → Recording is sent to `/api/twilio/process-recording`
4. **Pipeline executes inline** (all within Twilio's webhook timeout):
   - **STT**: Deepgram transcribes the audio + detects language
   - **RAG**: ChromaDB retrieves relevant medical protocols
   - **LLM**: Gemini analyzes symptoms against protocols + its own knowledge
   - **TTS**: ElevenLabs generates natural speech audio
5. **Response is delivered**:
   - `SAFE_ADVICE` → Speaks home-care advice + asks follow-up question
   - `ESCALATE` → Speaks first-aid, sends SMS to doctors, transfers call
6. **Follow-up loop** via Twilio `<Gather>` speech → `/api/twilio/follow-up`

### Decision Logic

| Decision | Trigger | Action |
|----------|---------|--------|
| `SAFE_ADVICE` | Mild/common symptoms (headache, cold, body ache, mild fever ≤102°F) | Numbered home-care steps, probable causes, follow-up question |
| `ESCALATE` | Life-threatening symptoms (chest pain, breathing difficulty, severe bleeding, high fever >102°F) | First-aid instructions, SMS alert to healthcare providers, call transfer |

### Special Policies

- **Fever Policy**: Temperatures >102°F automatically escalate; ≤102°F get home-care advice
- **Common Safety**: Known safe scenarios (e.g., accidentally swallowed chewing gum) return pre-built responses
- **Language Softening**: Words like "severe" and "emergency" are softened for phone delivery
- **Response Limits**: Max 80 words / 5 sentences for phone playback clarity

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- A [Twilio](https://www.twilio.com/) account with a phone number
- A [Deepgram](https://deepgram.com/) API key
- A [Google AI Studio](https://aistudio.google.com/) API key (for Gemini)
- An [ElevenLabs](https://elevenlabs.io/) API key + voice ID
- [ngrok](https://ngrok.com/) (for local development)

### Install Dependencies

```bash
cd health-voice-assistant
pip install -r requirements.txt
```

### Dependencies

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
twilio==9.3.0
deepgram-sdk==3.7.0
google-generativeai==0.7.2
langchain==0.3.0
langchain-google-genai==2.0.0
langchain-community==0.3.0
chromadb==0.5.0
python-dotenv==1.0.1
pydantic-settings==2.5.0
httpx==0.27.0
python-multipart==0.0.12
aiofiles==24.1.0
```

---

## Environment Variables

Create a `.env` file inside `health-voice-assistant/`:

```env
# Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX

# Deepgram (Speech-to-Text)
DEEPGRAM_API_KEY=your_deepgram_api_key

# Google Gemini (LLM + Embeddings)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL=gemini-3-flash

# ElevenLabs (Text-to-Speech)
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_voice_id

# App Configuration
APP_BASE_URL=https://your-ngrok-url.ngrok-free.dev
ESCALATION_PHONE=+1XXXXXXXXXX,+1YYYYYYYYYY
ENVIRONMENT=development
```

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number (E.164 format) |
| `DEEPGRAM_API_KEY` | Deepgram API key for speech transcription |
| `GOOGLE_API_KEY` | Google API key for Gemini LLM & embeddings |
| `GOOGLE_MODEL` | Gemini model name (default: `gemini-3-flash`) |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for TTS |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID for the assistant's voice |
| `APP_BASE_URL` | Public URL where the app is accessible (ngrok or deployed URL) |
| `ESCALATION_PHONE` | Comma-separated list of healthcare provider phone numbers for emergency SMS |
| `ENVIRONMENT` | `development` or `production` |

---

## Running Locally

### 1. Start the FastAPI Server

```bash
cd health-voice-assistant
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Expose with ngrok

```bash
ngrok http 8000
```

Copy the ngrok HTTPS URL and update:
- `APP_BASE_URL` in your `.env`
- Twilio Voice webhook URL → `https://your-url.ngrok-free.dev/api/twilio/incoming-call`

### 3. Configure Twilio Webhook

In your [Twilio Console](https://console.twilio.com/):
1. Go to **Phone Numbers** → Select your number
2. Under **Voice & Fax** → **A Call Comes In**:
   - Set to **Webhook**
   - URL: `https://your-ngrok-url.ngrok-free.dev/api/twilio/incoming-call`
   - Method: **HTTP POST**

### 4. Test

Call your Twilio phone number and describe your symptoms!

---

## Deployment

### Railway

The project includes a `railway.toml` and root `Dockerfile` for one-click Railway deployment:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

**Steps:**
1. Push to GitHub
2. Connect your repo to [Railway](https://railway.app/)
3. Set all environment variables in Railway dashboard
4. Update `APP_BASE_URL` to your Railway deployment URL
5. Update the Twilio webhook to your Railway URL

### Docker

```bash
# From the repo root
docker build -t immihelp .
docker run -p 8000:8000 --env-file health-voice-assistant/.env immihelp
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web dashboard (serves `static/index.html`) |
| `GET` | `/health` | Health check (`{"status": "ok"}`) |
| `GET` | `/api/sessions` | View active call sessions |
| `GET/POST` | `/api/twilio/incoming-call` | Twilio webhook — greeting + start recording |
| `POST` | `/api/twilio/process-recording` | Twilio webhook — full STT → RAG → LLM → TTS pipeline |
| `POST` | `/api/twilio/follow-up` | Twilio webhook — handle follow-up speech via Gather |
| `POST` | `/api/twilio/recording-status` | Twilio webhook — recording status callback |

---

## Knowledge Base

The RAG pipeline is powered by **23 curated medical protocol documents** covering:

| # | Document | Topics |
|---|----------|--------|
| 01 | Emergency Signs | Red-flag symptoms requiring immediate care |
| 02 | Fever | Fever assessment, temperature thresholds, home care |
| 03 | Diarrhea | Dehydration, ORS, when to seek help |
| 04 | Wounds | Wound care, bleeding control, infection signs |
| 05 | Respiratory | Cough, cold, breathing difficulty |
| 06 | Maternal | Pregnancy-related concerns |
| 07 | Child Health | Pediatric symptoms and care |
| 08 | Back Pain | Back pain causes, home care, red flags |
| 09 | Urinary Issues | UTI symptoms, kidney concerns |
| 10 | Ear/Nose/Throat | ENT conditions and care |
| 11 | Skin Conditions | Rashes, infections, allergic reactions |
| 12 | Joint & Muscle | Sprains, arthritis, muscle pain |
| 13 | Digestive (Advanced) | Gastric issues, GERD, food poisoning |
| 14 | Mental Health | Anxiety, stress, crisis signs |
| 15 | Eye Conditions | Eye infections, vision concerns |
| 16 | Dental/Oral | Toothache, gum issues |
| 17 | Common Infections | Viral/bacterial infections |
| 18 | Metabolic/Nutritional | Diabetes signs, deficiencies |
| 19 | Respiratory (Advanced) | Asthma, bronchitis, pneumonia signs |
| 20 | Women's Health | Menstrual issues, reproductive health |
| — | Home Remedies | Natural/home treatment protocols |
| — | OTC Medicines | Over-the-counter medication guidance |
| — | Non-OTC Medicines | Prescription medication awareness |

### How Documents Are Processed

1. **Loading**: Markdown files are parsed with risk-level metadata extraction
2. **Chunking**: Split into 500-character chunks with 50-character overlap using `RecursiveCharacterTextSplitter`
3. **Embedding**: Vectorized using `gemini-embedding-001`
4. **Storage**: Persisted in ChromaDB with automatic re-indexing when new documents are detected
5. **Retrieval**: Top 4 most relevant chunks are retrieved per query via similarity search

---

## Services

### STT Service (`stt.py`)
- Uses **Deepgram Nova-2** for transcription
- Automatic language detection (English/Hindi)
- Handles multiple Twilio recording URL formats (.wav/.mp3)
- Fallback authentication for recording downloads

### RAG Service (`rag.py`)
- Retrieves top-4 relevant medical protocol chunks
- Extracts risk levels (`LOW`, `HIGH`, `CRITICAL`) from metadata
- Builds formatted context for the LLM

### LLM Service (`llm.py`)
- Auto-discovers available Gemini models with graceful fallback
- Structured JSON output with decision, risk level, response text, probable causes
- Built-in fever policy (102°F threshold)
- Common safety policies (e.g., swallowed chewing gum)
- Language-aware responses (English/Hindi)
- Softens alarming language for phone delivery
- Response normalization: max 80 words, 5 sentences

### TTS Service (`tts.py`)
- Uses **ElevenLabs Multilingual v2** for natural speech
- Generates MP3 audio files served via FastAPI static mount
- Falls back to Twilio's built-in Say on failure

### Escalation Service (`escalation.py`)
- Sends SMS alerts to multiple healthcare providers
- Builds TwiML for call transfer to primary provider
- Graceful fallback if doctor is unavailable

### Session Manager (`session.py`)
- In-memory session tracking per caller
- Conversation history for context-aware follow-ups
- Language preference persistence
- Auto-cleanup after 30 minutes of inactivity

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is for educational and humanitarian purposes. Please consult with licensed healthcare professionals for actual medical advice.

---

<p align="center">
  Built with ❤️ by the ImmiHelp Team
</p>
