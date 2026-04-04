import os

BASE_DIR = r"c:\Users\Mehakpreet Singh\Documents\iimihelp\immihelp\health-voice-assistant"

def create_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created {path}")

create_file("app/knowledge_base/loader.py", """
import os
import re
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(docs_dir: str) -> list[Document]:
    documents = []
    path = Path(docs_dir)
    for file_path in path.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        risk_match = re.search(r"RISK_LEVEL:\\s*(LOW|HIGH|CRITICAL)", content)
        doc_risk = risk_match.group(1) if risk_match else "UNKNOWN"
        category = file_path.stem
        
        doc = Document(
            page_content=content,
            metadata={
                "source": file_path.name,
                "risk_level": doc_risk,
                "category": category
            }
        )
        documents.append(doc)
    return documents

def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\\n---\\n", "\\n## ", "\\n### ", "\\n\\n", "\\n", " "]
    )
    chunks = splitter.split_documents(docs)
    
    for chunk in chunks:
        risk_match = re.search(r"RISK_LEVEL:\\s*(LOW|HIGH|CRITICAL)", chunk.page_content)
        chunk_risk = risk_match.group(1) if risk_match else chunk.metadata.get("risk_level", "UNKNOWN")
        
        es_match = re.search(r"Escalation_Required:\\s*(TRUE|FALSE)", chunk.page_content, re.IGNORECASE)
        requires_escalation = False
        if es_match and es_match.group(1).upper() == "TRUE":
            requires_escalation = True
            
        chunk.metadata["chunk_risk"] = chunk_risk
        chunk.metadata["requires_escalation"] = requires_escalation
        
    return chunks
""")

create_file("app/knowledge_base/store.py", """
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import get_settings
from app.knowledge_base.loader import load_documents, split_documents
import os

class VectorStore:
    _instance = None

    def __init__(self):
        settings = get_settings()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.google_api_key
        )
        self.db = Chroma(
            collection_name="medical_protocols",
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir
        )
        
        if self.db._collection.count() == 0:
            kb_dir = os.path.join(os.path.dirname(__file__), "documents")
            docs = load_documents(kb_dir)
            chunks = split_documents(docs)
            if chunks:
                self.db.add_documents(chunks)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def search(self, query: str, k: int = 4):
        return self.db.similarity_search_with_relevance_scores(query, k=k)
""")

create_file("app/services/session.py", """
import time

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_or_create(self, caller_id: str) -> dict:
        now = time.time()
        self._cleanup(now)
        
        if caller_id not in self.sessions:
            self.sessions[caller_id] = {
                "caller_id": caller_id,
                "created_at": now,
                "last_active": now,
                "conversation_history": [],
                "escalated": False
            }
        else:
            self.sessions[caller_id]["last_active"] = now
            
        return self.sessions[caller_id]

    def add_message(self, caller_id: str, role: str, content: str):
        if caller_id in self.sessions:
            self.sessions[caller_id]["conversation_history"].append({"role": role, "content": content})
            self.sessions[caller_id]["last_active"] = time.time()

    def get_history(self, caller_id: str) -> list:
        if caller_id in self.sessions:
            return self.sessions[caller_id]["conversation_history"]
        return []

    def mark_escalated(self, caller_id: str):
        if caller_id in self.sessions:
            self.sessions[caller_id]["escalated"] = True
            
    def _cleanup(self, now: float):
        expired = [cid for cid, sess in self.sessions.items() if now - sess["last_active"] > 1800]
        for cid in expired:
            del self.sessions[cid]

session_mgr = SessionManager()
""")

create_file("app/services/stt.py", """
import httpx
from deepgram import DeepgramClient, PrerecordedOptions
from app.config import get_settings

async def transcribe(audio_url: str) -> dict:
    settings = get_settings()
    wav_url = f"{audio_url}.wav"
    
    try:
        deepgram = DeepgramClient(settings.deepgram_api_key)
        
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            punctuate=True,
            detect_language=True
        )
        
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)
        async with httpx.AsyncClient() as client:
            response = await client.get(wav_url, auth=auth, timeout=30.0)
            response.raise_for_status()
            audio_data = response.content
            
        payload = {"buffer": audio_data}
        res = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        
        channels = res.results.channels
        if not channels or not channels[0].alternatives:
            return {"success": False, "error": "No transcription alternatives returned"}
             
        alt = channels[0].alternatives[0]
        text = alt.transcript
        confidence = alt.confidence
        language = alt.languages[0] if alt.languages else "en"
        
        return {
            "text": text,
            "confidence": confidence,
            "language": language,
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
""")

create_file("app/services/rag.py", """
from app.knowledge_base.store import VectorStore

class RAGService:
    def __init__(self):
        self.vector_store = None

    def get_store(self):
        if not self.vector_store:
            self.vector_store = VectorStore.get_instance()
        return self.vector_store

    def retrieve(self, query: str):
        store = self.get_store()
        results = store.search(query, k=4)
        
        documents = []
        max_risk_level = "UNKNOWN"
        requires_escalation = False
        relevance_scores = []
        sources = []
        
        risk_priority = {"LOW": 1, "UNKNOWN": 2, "HIGH": 3, "CRITICAL": 4}
        current_max_priority = 0
        
        for doc, score in results:
            documents.append(doc)
            relevance_scores.append(score)
            sources.append(doc.metadata.get("source", "Unknown"))
            
            chunk_risk = doc.metadata.get("chunk_risk", "UNKNOWN")
            priority = risk_priority.get(chunk_risk.upper(), 2)
            if priority > current_max_priority:
                current_max_priority = priority
                max_risk_level = chunk_risk.upper()
                
            if doc.metadata.get("requires_escalation") is True:
                requires_escalation = True

        risk_analysis = {
            "max_risk_level": max_risk_level,
            "requires_escalation": requires_escalation,
            "relevance_scores": relevance_scores,
            "sources": sources
        }
        
        return documents, risk_analysis

    def build_context(self, documents: list) -> str:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            risk = doc.metadata.get("chunk_risk", "UNKNOWN")
            content = doc.page_content.strip()
            context_parts.append(f"--- PROTOCOL #{i} (Source: {source}, Risk: {risk}) ---\\n{content}\\n")
        return "\\n".join(context_parts)

rag = RAGService()
""")

create_file("app/services/llm.py", """
import json
import google.generativeai as genai
from app.config import get_settings
from app.prompts.system import SYSTEM_PROMPT

class LLMService:
    def __init__(self):
        self.settings = get_settings()
        genai.configure(api_key=self.settings.google_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=dict(
                temperature=0.3,
                top_p=0.8,
                max_output_tokens=1024
            )
        )

    async def analyze(self, query: str, context: str, risk_analysis: dict, history: list = None) -> dict:
        try:
            history = history[-6:] if history else []
            hist_str = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            
            risk_summary = (
                f"Max Risk Level: {risk_analysis['max_risk_level']}\\n"
                f"Requires Escalation: {risk_analysis['requires_escalation']}"
            )
            
            prompt = (
                f"{SYSTEM_PROMPT}\\n\\n"
                f"RETRIEVED PROTOCOLS:\\n{context}\\n\\n"
                f"RISK SUMMARY:\\n{risk_summary}\\n\\n"
                f"RECENT HISTORY:\\n{hist_str}\\n\\n"
                f"USER QUERY: {query}"
            )

            response = self.model.generate_content(prompt)
            output = response.text.strip()
            
            if output.startswith("```json"):
                output = output.replace("```json", "", 1)
            if output.endswith("```"):
                output = output[: -3]
                
            result = json.loads(output.strip())
            
            # SAFETY OVERRIDE
            if risk_analysis.get("requires_escalation", False) and result.get("decision") == "SAFE_ADVICE":
                result["decision"] = "ESCALATE"
                
            return result
            
        except Exception as e:
            return {
                "decision": "ESCALATE",
                "risk_level": "UNKNOWN",
                "response_text": "Having trouble analyzing. Connecting you with a healthcare worker.",
                "follow_up_question": None,
                "confidence": 0.0
            }

llm = LLMService()
""")

create_file("app/services/tts.py", """
import httpx
import uuid
import os
from app.config import get_settings

class TTSService:
    async def get_public_url(self, text: str) -> str:
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
            response = await client.post(url, json=body, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            with open(filepath, "wb") as f:
                f.write(response.content)
                
        # To make it accessible via Windows assuming basic API service logic:
        # Instead of /tmp we'll use a local directory to serve from FastAPI.
        # Ensure we write it to a local 'static/audio' directory inside app or data!
        # Wait, the spec strictly asks for /tmp/health_voice_audio/{uuid}.mp3
        # I'll save it to /tmp/health_voice_audio or standard temp on windows.
        
        base_url = settings.app_base_url.rstrip('/')
        return f"{base_url}/audio/{filename}"

tts = TTSService()
""")

create_file("app/services/escalation.py", """
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from app.config import get_settings

class EscalationService:
    def __init__(self):
        self.settings = get_settings()
        self.twilio_client = Client(self.settings.twilio_account_sid, self.settings.twilio_auth_token)

    async def alert_doctor(self, caller: str, symptoms: str) -> bool:
        try:
            message = f"🚨 HEALTH ALERT\\nPatient: {caller}\\nSymptoms: {symptoms}"
            self.twilio_client.messages.create(
                body=message,
                from_=self.settings.twilio_phone_number,
                to=self.settings.escalation_phone
            )
            return True
        except Exception as e:
            return False

    def build_transfer_twiml(self, first_aid_message: str = "Connecting you...") -> str:
        response = VoiceResponse()
        response.say(first_aid_message)
        response.dial(self.settings.escalation_phone, timeout=30)
        response.say("Doctor unavailable. They've been notified. Please head to the nearest facility if urgent.")
        return str(response)

escalation = EscalationService()
""")

create_file("app/api/twilio_webhooks.py", """
from fastapi import APIRouter, Request, Form, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.services.session import session_mgr
from app.services.stt import transcribe
from app.services.rag import rag
from app.services.llm import llm
from app.services.tts import tts
from app.services.escalation import escalation

router = APIRouter()

@router.post("/incoming-call")
async def incoming_call(request: Request, From: str = Form(...)):
    session = session_mgr.get_or_create(From)
    
    response = VoiceResponse()
    response.say("Welcome to the Health Voice Assistant. Please describe your symptoms and how you are feeling.")
    
    response.record(
        action="/api/twilio/process-recording",
        max_length=60,
        play_beep=True,
        trim="trim-silence",
        transcribe=False
    )
    response.say("Didn't hear anything. Please try calling back.")
    
    return Response(content=str(response), media_type="application/xml")

@router.post("/process-recording")
async def process_recording(request: Request, RecordingUrl: str = Form(...), From: str = Form(...)):
    try:
        response = VoiceResponse()
        
        # STT
        stt_result = await transcribe(RecordingUrl)
        if not stt_result.get("success"):
            response.say("Sorry, I could not hear you clearly.")
            response.redirect("/api/twilio/incoming-call")
            return Response(content=str(response), media_type="application/xml")
            
        user_text = stt_result["text"]
        session_mgr.add_message(From, "user", user_text)
        
        # RAG
        protocols, risk = rag.retrieve(user_text)
        context = rag.build_context(protocols)
        
        # LLM
        history = session_mgr.get_history(From)
        decision_data = await llm.analyze(user_text, context, risk, history)
        
        decision = decision_data.get("decision")
        response_text = decision_data.get("response_text", "I'm having trouble analyzing your request.")
        
        session_mgr.add_message(From, "assistant", response_text)
        
        if decision == "SAFE_ADVICE":
            audio_url = await tts.get_public_url(response_text)
            response.play(audio_url)
            
            # Follow-up
            gather = Gather(action="/api/twilio/follow-up", input="speech", timeout=5)
            gather.say("Any other questions?")
            response.append(gather)
            
        else:
            # ESCALATE
            session_mgr.mark_escalated(From)
            await escalation.alert_doctor(From, user_text)
            
            twiml = escalation.build_transfer_twiml(first_aid_message=response_text)
            return Response(content=twiml, media_type="application/xml")
            
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        err_response = VoiceResponse()
        err_response.say("Technical issues. Visit nearest facility.")
        return Response(content=str(err_response), media_type="application/xml")

@router.post("/follow-up")
async def follow_up(request: Request, From: str = Form(...), SpeechResult: str = Form(None)):
    if not SpeechResult:
        response = VoiceResponse()
        response.say("Goodbye, take care.")
        return Response(content=str(response), media_type="application/xml")
        
    try:
        session_mgr.add_message(From, "user", SpeechResult)
        
        protocols, risk = rag.retrieve(SpeechResult)
        context = rag.build_context(protocols)
        
        history = session_mgr.get_history(From)
        decision_data = await llm.analyze(SpeechResult, context, risk, history)
        
        decision = decision_data.get("decision")
        response_text = decision_data.get("response_text", "I'm having trouble analyzing your request.")
        session_mgr.add_message(From, "assistant", response_text)
        
        if decision == "SAFE_ADVICE":
            audio_url = await tts.get_public_url(response_text)
            response = VoiceResponse()
            response.play(audio_url)
            
            gather = Gather(action="/api/twilio/follow-up", input="speech", timeout=5)
            gather.say("Any other questions?")
            response.append(gather)
            return Response(content=str(response), media_type="application/xml")
        else:
            session_mgr.mark_escalated(From)
            await escalation.alert_doctor(From, SpeechResult)
            twiml = escalation.build_transfer_twiml(first_aid_message=response_text)
            return Response(content=twiml, media_type="application/xml")
            
    except Exception as e:
        err_response = VoiceResponse()
        err_response.say("Technical issues. Visit nearest facility.")
        return Response(content=str(err_response), media_type="application/xml")

@router.post("/recording-status")
async def recording_status(request: Request, RecordingStatus: str = Form(...)):
    print(f"Recording Status: {RecordingStatus}")
    return {"status": "ok"}
""")

create_file("app/main.py", """
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import twilio_webhooks
import os

app = FastAPI(title="Health Voice Assistant")

# We mount the /tmp/health_voice_audio to serve TTS audio
# On Windows, /tmp doesn't exist naturally on the root, but the TTS service 
# creates the directory. Wait, we should use a relative directory instead, 
# but the TTS spec required "/tmp/health_voice_audio". Let's handle it resiliently.
temp_audio_dir = "/tmp/health_voice_audio"
os.makedirs(temp_audio_dir, exist_ok=True)

app.mount("/audio", StaticFiles(directory=temp_audio_dir), name="audio")

app.include_router(twilio_webhooks.router, prefix="/api/twilio")

@app.get("/health")
def health_check():
    return {"status": "ok"}
""")
