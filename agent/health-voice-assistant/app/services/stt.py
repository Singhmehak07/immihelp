import httpx
import re
from deepgram import DeepgramClient, PrerecordedOptions
from app.config import get_settings

def _recording_candidate_urls(audio_url: str) -> list[str]:
    # Twilio recording URLs can be requested as different formats; trying both
    # reduces no-audio/no-transcript cases for some calls.
    candidates = []
    if audio_url.endswith(".wav") or audio_url.endswith(".mp3"):
        candidates.append(audio_url)
    else:
        candidates.append(f"{audio_url}.wav")
        candidates.append(f"{audio_url}.mp3")
        candidates.append(audio_url)

    unique = []
    for url in candidates:
        if url not in unique:
            unique.append(url)
    return unique


def _extract_account_sid_from_url(audio_url: str) -> str | None:
    match = re.search(r"/Accounts/(AC[a-fA-F0-9]{32})/", audio_url)
    return match.group(1) if match else None


async def transcribe(audio_url: str, account_sid: str | None = None) -> dict:
    settings = get_settings()
    recording_urls = _recording_candidate_urls(audio_url)
    
    try:
        deepgram = DeepgramClient(settings.deepgram_api_key)
        
        options = PrerecordedOptions(
            model="nova-2",
            smart_format=True,
            punctuate=True,
            detect_language=True
        )

        derived_sid = account_sid or _extract_account_sid_from_url(audio_url)
        primary_sid = derived_sid or settings.twilio_account_sid
        fallback_sid = settings.twilio_account_sid if primary_sid != settings.twilio_account_sid else None

        async with httpx.AsyncClient() as client:
            audio_data = None
            last_error = None
            for recording_url in recording_urls:
                try:
                    response = await client.get(
                        recording_url,
                        auth=(primary_sid, settings.twilio_auth_token),
                        timeout=30.0,
                    )
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code != 401 or not fallback_sid:
                        last_error = exc
                        continue

                    try:
                        response = await client.get(
                            recording_url,
                            auth=(fallback_sid, settings.twilio_auth_token),
                            timeout=30.0,
                        )
                        response.raise_for_status()
                    except Exception as nested_exc:
                        last_error = nested_exc
                        continue
                except Exception as exc:
                    last_error = exc
                    continue

                if response.content:
                    audio_data = response.content
                    break

            if not audio_data:
                if last_error:
                    raise last_error
                raise RuntimeError("Failed to download recording audio")
            
        payload = {"buffer": audio_data}
        res = deepgram.listen.rest.v("1").transcribe_file(payload, options)
        
        channels = res.results.channels
        if not channels or not channels[0].alternatives:
            return {"success": False, "error": "No transcription alternatives returned"}
             
        alt = channels[0].alternatives[0]
        text = (alt.transcript or "").strip()
        confidence = alt.confidence
        language = alt.languages[0] if alt.languages else "en"

        if not text:
            return {"success": False, "error": "empty_transcript", "language": language}
        
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
