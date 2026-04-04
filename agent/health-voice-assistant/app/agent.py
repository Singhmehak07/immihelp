"""
Immihelp AI Health Voice Agent — LiveKit Agents 1.0+
=====================================================

Real-time voice AI health assistant using:
  - Deepgram Nova-3 (STT - streaming)
  - Google Gemini Flash (LLM - with RAG tool calling)
  - ElevenLabs (TTS - streaming)
  - Twilio SIP Trunk → LiveKit Room → This Agent

Architecture:
  Phone → Twilio SIP URI → LiveKit Room (WebRTC) → Agent (streaming loop) → TTS stream

The agent continuously listens, transcribes, reasons (with medical RAG),
and speaks — all in parallel. Users can interrupt at any time.
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment from .env (project root) or .env.local
# ---------------------------------------------------------------------------
load_dotenv(".env.local")
load_dotenv(".env")

from livekit import agents, rtc
from livekit.agents import (
    AgentServer,
    AgentSession,
    Agent,
    RunContext,
    function_tool,
    room_io,
    ChatContext,
    ChatMessage,
)
from livekit.plugins import deepgram, google, elevenlabs, silero, noise_cancellation

# ---------------------------------------------------------------------------
# Import existing RAG service from the project
# ---------------------------------------------------------------------------
# Add parent directory so we can import app.services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag import rag as rag_service
from app.services.escalation import escalation as escalation_service

logger = logging.getLogger("health-agent")
logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Medical system prompt — adapted from the existing SYSTEM_PROMPT for
# conversational voice (no JSON output, natural speech).
# ---------------------------------------------------------------------------
VOICE_SYSTEM_PROMPT = """You are Immihelp, a caring and knowledgeable health voice assistant \
for rural India. You speak naturally on a phone call. You are NOT a doctor.

KEY RULES:
1. Use the lookup_medical_protocols tool when users describe symptoms or ask about conditions.
2. Give 2-4 numbered home-care steps specific to their symptoms.
3. Mention specific medicines with dosage when appropriate (e.g., "Paracetamol 500mg every 6 hours").
4. Keep responses under 60 words — they will be spoken aloud.
5. Use simple, everyday language. No medical jargon.
6. Frame possible causes as possibilities, never diagnoses.
7. End advice with brief "when to seek help" guidance.
8. For truly dangerous symptoms (chest pain, can't breathe, unconscious, severe bleeding, seizures) — \
   tell the user to go to the nearest hospital IMMEDIATELY.
9. For common symptoms (headache, cold, mild fever, body aches) — give practical home-care.
10. Speak in the same language the caller uses. If they speak Hindi, respond in Hindi.
11. Be warm, calm, and reassuring. Never panic the caller.
12. Never mention internal systems, model names, or technical details."""


# ═══════════════════════════════════════════════════════════════════════════
# Health Assistant Agent
# ═══════════════════════════════════════════════════════════════════════════

class HealthAssistant(Agent):
    """LiveKit voice agent for medical health assistance with RAG."""

    def __init__(self) -> None:
        super().__init__(
            instructions=VOICE_SYSTEM_PROMPT,
        )

    # ─── RAG Tool ───────────────────────────────────────────────────────
    @function_tool()
    async def lookup_medical_protocols(
        self,
        context: RunContext,
        query: str,
    ) -> str:
        """Search the medical knowledge base for protocols, emergency procedures,
        and treatment guidelines related to the user's symptoms or condition.

        Args:
            query: The medical condition, symptom, or health question to search for.
        """
        logger.info("RAG lookup triggered: %s", query)

        try:
            documents, risk_analysis = rag_service.retrieve(query)
            context_text = rag_service.build_context(documents)

            risk_level = risk_analysis.get("max_risk_level", "UNKNOWN")
            requires_escalation = risk_analysis.get("requires_escalation", False)

            result_parts = []

            if context_text.strip():
                result_parts.append(f"MEDICAL PROTOCOL RESULTS:\n{context_text}")
            else:
                result_parts.append("No specific protocols found. Use your general medical knowledge.")

            result_parts.append(f"\nRISK ASSESSMENT: {risk_level}")

            if requires_escalation or risk_level == "CRITICAL":
                result_parts.append(
                    "⚠️ HIGH RISK — Advise the caller to seek immediate medical attention. "
                    "Be clear but calm."
                )

            return "\n".join(result_parts)

        except Exception as e:
            logger.exception("RAG lookup failed for query: %s", query)
            return (
                "Knowledge base temporarily unavailable. "
                "Use your general medical knowledge to help the caller. "
                "If symptoms sound serious, advise them to visit a hospital."
            )

    # ─── Escalation Tool ────────────────────────────────────────────────
    @function_tool()
    async def escalate_to_specialist(
        self,
        context: RunContext,
        caller_phone: str,
        symptoms_summary: str,
    ) -> str:
        """Send an urgent SMS alert to the on-call specialist when the caller
        has critical/life-threatening symptoms.

        Only use this for genuine emergencies: chest pain, breathing difficulty,
        unconsciousness, severe bleeding, seizures, high fever in infants.

        Args:
            caller_phone: The caller's phone number or identifier.
            symptoms_summary: Brief summary of the critical symptoms.
        """
        logger.warning("ESCALATION triggered for %s: %s", caller_phone, symptoms_summary)

        try:
            success = await escalation_service.alert_doctor(caller_phone, symptoms_summary)
            if success:
                return (
                    "Specialist has been alerted via SMS. "
                    "Tell the caller that a specialist has been notified and will reach out. "
                    "Continue to provide first-aid guidance while they wait."
                )
            else:
                return (
                    "Could not reach the specialist right now. "
                    "Advise the caller to go to the nearest hospital immediately."
                )
        except Exception:
            logger.exception("Escalation failed for %s", caller_phone)
            return "Escalation failed. Advise the caller to visit the nearest hospital."

    # ─── RAG injection on every user turn ────────────────────────────────
    async def on_user_turn_completed(
        self,
        turn_ctx: ChatContext,
        new_message: ChatMessage,
    ) -> None:
        """Automatically inject RAG context before LLM generates a response.
        This runs on every user turn in addition to the tool-based RAG."""
        user_text = new_message.text_content
        if not user_text or len(user_text.strip()) < 5:
            return

        try:
            documents, risk_analysis = rag_service.retrieve(user_text)
            context_text = rag_service.build_context(documents)

            if context_text.strip():
                risk_level = risk_analysis.get("max_risk_level", "UNKNOWN")
                turn_ctx.add_message(
                    role="assistant",
                    content=(
                        f"[Internal — relevant medical protocols for this query, "
                        f"risk level: {risk_level}]\n{context_text}"
                    ),
                )
        except Exception:
            logger.debug("Background RAG injection failed, continuing without it")


# ═══════════════════════════════════════════════════════════════════════════
# Agent Server & Session Setup
# ═══════════════════════════════════════════════════════════════════════════

server = AgentServer()


@server.rtc_session(agent_name="health-assistant")
async def health_agent_session(ctx: agents.JobContext):
    """
    Called whenever a new participant joins a LiveKit room dispatched to
    the "health-assistant" agent. For SIP calls, LiveKit automatically
    creates a room when a call arrives on the SIP trunk.
    """

    logger.info(
        "New health agent session — room: %s, job: %s",
        ctx.room.name,
        ctx.job.id,
    )

    # ── Configure the voice pipeline ─────────────────────────────────
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language="multi",              # auto-detect Hindi/English/etc.
        ),
        llm=google.LLM(
            model="gemini-2.0-flash",
            temperature=0.3,
        ),
        tts=elevenlabs.TTS(
            model="eleven_turbo_v2_5",
            voice=os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM"),
        ),
        vad=silero.VAD.load(),
    )

    # ── Start the agent ──────────────────────────────────────────────
    await session.start(
        room=ctx.room,
        agent=HealthAssistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                # Use telephony noise cancellation for SIP calls,
                # regular BVC for browser/WebRTC participants
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    # ── Greet the caller ─────────────────────────────────────────────
    await session.generate_reply(
        instructions=(
            "Greet the caller warmly. Say: "
            "'Namaste! Main Immihelp AI hoon, aapka health assistant. "
            "Aap mujhe apni tabiyet ke baare mein bata sakte hain.' "
            "Then switch to English: "
            "'Hello! I am Immihelp, your AI health assistant. "
            "Please tell me how you are feeling today.'"
        )
    )


# ═══════════════════════════════════════════════════════════════════════════
# CLI entrypoint
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    agents.cli.run_app(server)
