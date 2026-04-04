import asyncio
import logging
import time
import json
from urllib.parse import urlparse, quote

from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import StreamingResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.config import get_settings
from app.services.session import session_mgr
from app.services.stt import transcribe
from app.services.rag import rag
from app.services.llm import llm
from app.services.tts import tts
from app.services.escalation import escalation

router = APIRouter()
logger = logging.getLogger(__name__)

WEBHOOK_STT_TIMEOUT_SECONDS = 30
WEBHOOK_LLM_TIMEOUT_SECONDS = 25
WEBHOOK_TTS_TIMEOUT_SECONDS = 15
MIN_RECORDING_SECONDS = 3


def _request_url(request: Request, path: str) -> str:
    settings = get_settings()
    request_base = str(request.base_url).rstrip("/")
    app_base = settings.app_base_url.rstrip("/")

    parsed = urlparse(request_base)
    host = (parsed.hostname or "").lower()
    private_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}

    if not host or host in private_hosts or host.endswith(".local"):
        base = app_base
    else:
        base = request_base

    return f"{base}{path}"


def _lang_family(language: str | None) -> str:
    if not language:
        return "en"
    return str(language).strip().lower().split("-")[0]


def _localized_text(key: str, language: str | None) -> str:
    lang = _lang_family(language)
    texts = {
        "causes_prefix": {
            "en": "Most probable causes based on your symptoms are",
            "hi": "Aapke lakshanon ke adhar par sabse sambhavit karan hain",
        },
        "follow_up_prompt": {
            "en": "Any other questions?",
            "hi": "Kya aapka koi aur sawaal hai?",
        },
        "goodbye": {
            "en": "Goodbye, take care.",
            "hi": "Namaste, apna dhyan rakhiye.",
        },
        "repeat_prompt": {
            "en": "Please repeat your question.",
            "hi": "Kripya apna sawaal dobara boliye.",
        },
    }
    return texts.get(key, {}).get(lang) or texts.get(key, {}).get("en", "")


def _should_prioritize_gemini(query: str | None) -> bool:
    text = (query or "").strip().lower()
    if not text:
        return False
    direct_gemini_markers = [
        "back pain", "pain in back", "pain in my back",
        "lower back", "upper back", "back ache", "backache",
    ]
    return any(marker in text for marker in direct_gemini_markers)


async def append_voice_reply(request: Request, response: VoiceResponse, response_text: str) -> None:
    try:
        audio_url = await asyncio.wait_for(
            tts.get_public_url(
                response_text,
                base_url=str(request.base_url),
                request_timeout_seconds=WEBHOOK_TTS_TIMEOUT_SECONDS,
            ),
            timeout=WEBHOOK_TTS_TIMEOUT_SECONDS + 2,
        )
        response.play(audio_url)
    except Exception:
        logger.exception("TTS failed, falling back to Twilio Say")
        response.say(response_text)


def _compose_response_text(decision_data: dict, language: str | None = None) -> str:
    base_text = decision_data.get("response_text", "I'm having trouble analyzing your request.")
    causes = decision_data.get("probable_causes") or []
    if not isinstance(causes, list):
        causes = []
    causes = [str(c).strip() for c in causes if str(c).strip()]

    if not causes:
        return base_text

    if len(causes) == 1:
        cause_text = causes[0]
    elif len(causes) == 2:
        cause_text = f"{causes[0]} and {causes[1]}"
    else:
        cause_text = f"{causes[0]}, {causes[1]}, and {causes[2]}"

    prefix = _localized_text("causes_prefix", language)
    return f"{base_text} {prefix} {cause_text}."


async def _run_full_pipeline(
    user_text: str,
    caller_id: str,
    detected_language: str,
) -> dict:
    """Run RAG → LLM pipeline and return decision_data.
    
    This ALWAYS returns a valid decision_data dict, never raises.
    """
    try:
        # ── RAG ──
        use_direct_gemini = _should_prioritize_gemini(user_text)
        if use_direct_gemini:
            logger.info("Using Gemini-priority mode (KB bypass) for %s", caller_id)
            context = ""
            risk = {
                "max_risk_level": "LOW",
                "requires_escalation": False,
                "relevance_scores": [],
                "sources": [],
            }
        else:
            try:
                protocols, risk = rag.retrieve(user_text)
                context = rag.build_context(protocols)
            except Exception:
                logger.exception("RAG retrieval failed for %s", caller_id)
                context = ""
                # Don't mark as requires_escalation — let LLM use its own knowledge
                risk = {
                    "max_risk_level": "LOW",
                    "requires_escalation": False,
                    "relevance_scores": [],
                    "sources": [],
                }

        # ── LLM ──
        history = session_mgr.get_history(caller_id)
        try:
            decision_data = await asyncio.wait_for(
                llm.analyze(user_text, context, risk, history, user_language=detected_language),
                timeout=WEBHOOK_LLM_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.warning("LLM timed out for %s", caller_id)
            # Give a symptom-aware fallback instead of generic text
            decision_data = {
                "decision": "SAFE_ADVICE",
                "response_text": (
                    f"I understand you're concerned about your symptoms. "
                    f"Here is general advice: rest well, stay hydrated, and monitor how you feel. "
                    f"If symptoms get worse or don't improve in 24 hours, please see a doctor."
                ),
                "probable_causes": [],
                "follow_up_question": "Can you tell me more about when this started?",
            }

        return decision_data

    except Exception:
        logger.exception("Full pipeline failed for %s", caller_id)
        return {
            "decision": "SAFE_ADVICE",
            "response_text": (
                "I understand you're not feeling well. "
                "Please rest, stay hydrated, and monitor your symptoms. "
                "If you feel worse, see a doctor as soon as possible."
            ),
            "probable_causes": [],
            "follow_up_question": "Can you describe what you're feeling in more detail?",
        }


# ──────────────────────────────────────────────────────────────────────────
# INCOMING CALL — greeting + record
# ──────────────────────────────────────────────────────────────────────────
@router.api_route("/incoming-call", methods=["GET", "POST"])
async def incoming_call(request: Request, From: str = Form(None)):
    caller_id = From or request.query_params.get("From") or "unknown-caller"
    session_mgr.get_or_create(caller_id)

    response = VoiceResponse()
    response.say(
        "Welcome to immihelp your Ai Assistant. Please describe your symptoms and how you are feeling."
    )

    record_action = _request_url(request, "/api/twilio/process-recording")
    logger.info("Twilio record action callback URL: %s", record_action)
    response.record(
        action=record_action,
        method="POST",
        max_length=90,
        timeout=8,
        play_beep=True,
        trim="do-not-trim",
        transcribe=False,
    )
    response.say("Didn't hear anything. Please try calling back.")

    return Response(content=str(response), media_type="application/xml")


# ──────────────────────────────────────────────────────────────────────────
# PROCESS RECORDING — the core handler
#
# Strategy: Twilio allows up to ~15s for webhook responses. We do the
# ENTIRE pipeline (STT → RAG → LLM) inline in this handler. If it
# succeeds, we respond with the answer directly.
#
# If something goes wrong at any step, we give a helpful fallback
# rather than a generic error.
#
# The key insight: Twilio's 15s timeout is for the HTTP response,
# not for audio. As long as we return valid TwiML within ~14s, Twilio
# is happy. We use generous timeouts for each step.
# ──────────────────────────────────────────────────────────────────────────
@router.post("/process-recording")
async def process_recording(
    request: Request,
    RecordingUrl: str = Form(...),
    RecordingDuration: str = Form(None),
    From: str = Form(None),
    AccountSid: str = Form(None),
):
    start_time = time.time()
    caller_id = From or request.query_params.get("From") or "unknown-caller"
    response = VoiceResponse()

    try:
        # ── Check minimum duration ──
        duration_seconds = 0.0
        try:
            if RecordingDuration is not None:
                duration_seconds = float(RecordingDuration)
        except Exception:
            duration_seconds = 0.0

        if duration_seconds and duration_seconds < MIN_RECORDING_SECONDS:
            logger.warning("Recording too short for %s: %ss", caller_id, duration_seconds)
            response.say(
                "I could not hear enough speech. After the beep, please speak for at least five seconds."
            )
            response.redirect(_request_url(request, "/api/twilio/incoming-call"), method="POST")
            return Response(content=str(response), media_type="application/xml")

        # ── STEP 1: STT — transcribe the recording ──
        logger.info("Starting STT for %s (recording: %s)", caller_id, RecordingUrl)
        try:
            stt_result = await asyncio.wait_for(
                transcribe(RecordingUrl, AccountSid),
                timeout=WEBHOOK_STT_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.warning("STT timed out for %s after %ss", caller_id, WEBHOOK_STT_TIMEOUT_SECONDS)
            stt_result = {"success": False, "error": "stt_timeout"}
        except Exception as e:
            logger.exception("STT crashed for %s", caller_id)
            stt_result = {"success": False, "error": str(e)}

        if not stt_result.get("success"):
            error_type = stt_result.get("error", "unknown")
            logger.warning("STT failed for %s: %s", caller_id, error_type)
            response.say("I could not hear you clearly. Please try again after the beep.")
            response.record(
                action=_request_url(request, "/api/twilio/process-recording"),
                method="POST",
                max_length=90,
                timeout=8,
                play_beep=True,
                trim="do-not-trim",
                transcribe=False,
            )
            response.say("Did not catch anything. Goodbye.")
            return Response(content=str(response), media_type="application/xml")

        user_text = (stt_result.get("text") or "").strip()
        detected_language = stt_result.get("language", "en")
        session_mgr.set_language(caller_id, detected_language)

        if not user_text:
            logger.warning("Empty STT transcript for %s", caller_id)
            response.say("I could not catch what you said. Please say your symptoms again after the beep.")
            response.record(
                action=_request_url(request, "/api/twilio/process-recording"),
                method="POST",
                max_length=90,
                timeout=8,
                play_beep=True,
                trim="do-not-trim",
                transcribe=False,
            )
            response.say("Did not hear anything. Goodbye.")
            return Response(content=str(response), media_type="application/xml")

        logger.info("STT transcript for %s: '%s' (lang: %s, took %.1fs)",
                     caller_id, user_text, detected_language, time.time() - start_time)
        session_mgr.add_message(caller_id, "user", user_text)

        # ── STEP 2: RAG + LLM — analyze symptoms ──
        decision_data = await _run_full_pipeline(user_text, caller_id, detected_language)

        decision = decision_data.get("decision", "SAFE_ADVICE")
        response_text = _compose_response_text(decision_data, detected_language)
        session_mgr.add_message(caller_id, "assistant", response_text)

        logger.info("Pipeline complete for %s in %.1fs: decision=%s, response='%s'",
                     caller_id, time.time() - start_time, decision, response_text[:80])

        # ── STEP 3: Deliver the response ──
        if decision == "ESCALATE":
            session_mgr.mark_escalated(caller_id)
            # Don't wait for doctor alert — fire and forget
            asyncio.create_task(_safe_alert_doctor(caller_id, user_text))

            twiml = escalation.build_transfer_twiml(first_aid_message=response_text)
            return Response(content=twiml, media_type="application/xml")

        # SAFE_ADVICE — speak the response + gather follow-up
        await append_voice_reply(request, response, response_text)

        # Ask follow-up
        follow_up_q = decision_data.get("follow_up_question")
        gather_prompt = follow_up_q or _localized_text("follow_up_prompt", detected_language)
        
        gather = Gather(
            action=_request_url(request, "/api/twilio/follow-up"),
            input="speech",
            method="POST",
            timeout=6,
            speech_timeout="auto",
        )
        gather.say(gather_prompt)
        response.append(gather)

        # If no speech gathered, say goodbye
        response.say(_localized_text("goodbye", detected_language))

        return Response(content=str(response), media_type="application/xml")

    except Exception:
        logger.exception("Error in /process-recording for %s", caller_id)
        # Even on total failure, give a useful response — never a generic error
        err_response = VoiceResponse()
        err_response.say(
            "I'm sorry, I had trouble processing your request. "
            "Here is general advice: rest well, keep hydrated, and if you feel worse, please visit the nearest health facility."
        )
        gather = Gather(
            action=_request_url(request, "/api/twilio/follow-up"),
            input="speech",
            method="POST",
            timeout=5,
        )
        gather.say("Would you like to try asking again?")
        err_response.append(gather)
        return Response(content=str(err_response), media_type="application/xml")


async def _safe_alert_doctor(caller_id: str, symptoms: str):
    """Fire-and-forget doctor alert — never blocks the main flow."""
    try:
        await escalation.alert_doctor(caller_id, symptoms)
    except Exception:
        logger.exception("Failed to alert doctor for %s", caller_id)


# ──────────────────────────────────────────────────────────────────────────
# FOLLOW-UP — Gather-based speech follow-up
# Uses Twilio's built-in <Gather input="speech"> so we get the text
# directly in SpeechResult — no STT needed.
# ──────────────────────────────────────────────────────────────────────────
@router.post("/follow-up")
async def follow_up(request: Request, From: str = Form(...), SpeechResult: str = Form(None)):
    preferred_language = session_mgr.get_language(From)

    if not SpeechResult or not SpeechResult.strip():
        response = VoiceResponse()
        response.say(_localized_text("goodbye", preferred_language))
        return Response(content=str(response), media_type="application/xml")

    SpeechResult = SpeechResult.strip()
    logger.info("Follow-up from %s: '%s'", From, SpeechResult)

    try:
        session_mgr.add_message(From, "user", SpeechResult)

        # Run RAG + LLM pipeline
        decision_data = await _run_full_pipeline(SpeechResult, From, preferred_language)

        decision = decision_data.get("decision", "SAFE_ADVICE")
        response_text = _compose_response_text(decision_data, preferred_language)
        session_mgr.add_message(From, "assistant", response_text)

        if decision == "ESCALATE":
            session_mgr.mark_escalated(From)
            asyncio.create_task(_safe_alert_doctor(From, SpeechResult))
            twiml = escalation.build_transfer_twiml(first_aid_message=response_text)
            return Response(content=twiml, media_type="application/xml")

        # SAFE_ADVICE
        response = VoiceResponse()
        await append_voice_reply(request, response, response_text)

        follow_up_q = decision_data.get("follow_up_question")
        gather_prompt = follow_up_q or _localized_text("follow_up_prompt", preferred_language)

        gather = Gather(
            action=_request_url(request, "/api/twilio/follow-up"),
            input="speech",
            method="POST",
            timeout=6,
            speech_timeout="auto",
        )
        gather.say(gather_prompt)
        response.append(gather)

        response.say(_localized_text("goodbye", preferred_language))

        return Response(content=str(response), media_type="application/xml")

    except Exception:
        logger.exception("Error in /follow-up for %s", From)
        err_response = VoiceResponse()
        err_response.say(
            "I'm sorry, I had trouble with that. "
            "Please rest, stay hydrated, and if symptoms worsen, visit the nearest health facility."
        )
        gather = Gather(
            action=_request_url(request, "/api/twilio/follow-up"),
            input="speech",
            method="POST",
            timeout=5,
        )
        gather.say("Would you like to try again?")
        err_response.append(gather)
        return Response(content=str(err_response), media_type="application/xml")


@router.post("/recording-status")
async def recording_status(request: Request, RecordingStatus: str = Form(...)):
    logger.info("Recording Status: %s", RecordingStatus)
    return {"status": "ok"}
