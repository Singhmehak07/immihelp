import json
import logging
import re
import asyncio

import google.generativeai as genai

from app.config import get_settings
from app.prompts.system import SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.model = None
        self.model_name = None

    def _get_model(self):
        if self.model is None:
            settings = get_settings()
            genai.configure(api_key=settings.google_api_key)
            candidates = [settings.google_model]

            discovered = []
            try:
                for model_info in genai.list_models():
                    methods = getattr(model_info, "supported_generation_methods", []) or []
                    if "generateContent" not in methods:
                        continue

                    name = getattr(model_info, "name", "") or ""
                    if name.startswith("models/"):
                        name = name.split("/", 1)[1]
                    if name.startswith("gemini"):
                        discovered.append(name)
            except Exception:
                logger.exception("Failed to discover Gemini models from list_models")

            discovered.sort(key=lambda n: (0 if "flash" in n.lower() else 1, n))
            candidates.extend(discovered)
            candidates.extend(["gemini-pro", "gemini-1.0-pro"])

            seen = set()
            ordered_candidates = []
            for name in candidates:
                if name and name not in seen:
                    seen.add(name)
                    ordered_candidates.append(name)

            generation_config = {
                "temperature": 0.3,
                "top_p": 0.8,
                "max_output_tokens": 1024,
            }

            last_error = None
            for candidate in ordered_candidates:
                try:
                    model = genai.GenerativeModel(
                        model_name=candidate,
                        generation_config=generation_config,
                    )
                    model.generate_content('{"ping":"ok"}')
                    self.model = model
                    self.model_name = candidate
                    logger.info("Using Gemini model: %s", candidate)
                    break
                except Exception as exc:
                    last_error = exc
                    logger.warning("Gemini model unavailable: %s", candidate)

            if self.model is None and last_error is not None:
                raise last_error

        return self.model

    def _extract_json_object(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "", 1).replace("```", "").strip()

        if cleaned.startswith("{") and cleaned.endswith("}"):
            return cleaned

        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return match.group(0)

        raise ValueError("No JSON object found in model response")

    def _response_to_text(self, response) -> str:
        direct_text = getattr(response, "text", None)
        if isinstance(direct_text, str) and direct_text.strip():
            return direct_text.strip()

        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            collected = []
            for part in parts:
                txt = getattr(part, "text", None)
                if isinstance(txt, str) and txt.strip():
                    collected.append(txt.strip())
            if collected:
                return "\n".join(collected)

        return ""

    def _generate_content_sync(self, prompt: str):
        return self._get_model().generate_content(prompt)

    def _extract_fever_fahrenheit(self, query: str) -> float | None:
        text = (query or "").lower()
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:\u00b0|degrees?|deg)?\s*(f|fahrenheit|c|celsius)?", text)
        candidates = []

        for value_str, unit in matches:
            try:
                value = float(value_str)
            except Exception:
                continue

            if unit in {"c", "celsius"}:
                candidates.append((value * 9 / 5) + 32)
            elif unit in {"f", "fahrenheit"}:
                candidates.append(value)
            else:
                if 34 <= value <= 43:
                    candidates.append((value * 9 / 5) + 32)
                elif 90 <= value <= 110:
                    candidates.append(value)

        return max(candidates) if candidates else None

    def _soften_language(self, text: str) -> str:
        softened = text
        softened = re.sub(r"\bserious\b", "important", softened, flags=re.IGNORECASE)
        softened = re.sub(r"\bsevere\b", "strong", softened, flags=re.IGNORECASE)
        softened = re.sub(r"\bemergency\b", "urgent care", softened, flags=re.IGNORECASE)
        return softened

    def _lang_family(self, language: str | None) -> str:
        if not language:
            return "en"
        return str(language).strip().lower().split("-")[0]

    def _localized_text(self, key: str, language: str | None) -> str:
        lang = self._lang_family(language)
        texts = {
            "fallback_escalate": {
                "en": "Based on what you described, please seek medical attention soon. Meanwhile, rest and stay hydrated. When to seek help: as soon as possible.",
                "hi": "Aapne jo bataya uske adhar par, jaldi doctor se milein. Tab tak aaram karein aur paani piyen. Madad kab leni hai: jald se jald.",
            },
            "fallback_safe": {
                "en": "Here is some general advice: rest well, stay hydrated, and monitor your symptoms closely. If they get worse, see a doctor.",
                "hi": "Yeh kuch general salah hai: aaram karein, paani peete rahen, aur apne symptoms par nazar rakhein. Agar bigde toh doctor se milein.",
            },
            "fallback_safe_follow_up": {
                "en": "Can you describe your symptoms in more detail? For example, when did they start and how severe is the pain?",
                "hi": "Kya aap apne symptoms aur detail mein bata sakte hain? Jaise ki kab se shuru hua aur dard kitna tez hai?",
            },
            "fever_high": {
                "en": "Your temperature is above 102 degrees. Please consult a doctor as soon as possible today. Until then, rest, drink fluids, and use paracetamol only within safe dose limits. When to seek help: now if fever keeps rising or you feel worse.",
                "hi": "Aapka temperature 102 se upar hai. Kripya aaj hi jaldi doctor se salah lein. Tab tak aaram karein, zyada paani piyen, aur paracetamol sirf safe dose mein lein. Madad kab leni hai: agar bukhar badhta rahe ya tabiyat aur kharab ho to turant.",
            },
            "fever_low": {
                "en": "Your fever is at or below 102 degrees. You can start home care: 1) rest, 2) drink plenty of water or ORS, 3) take paracetamol within safe dose limits, 4) use a lukewarm sponge. When to seek help: if fever goes above 102, lasts more than 2 to 3 days, or new symptoms appear.",
                "hi": "Aapka bukhar 102 ya usse kam hai. Aap ghar par care shuru kar sakte hain: 1) aaram, 2) paani ya ORS zyada piyen, 3) paracetamol safe dose mein lein, 4) halki gunguni patti karein. Madad kab leni hai: agar bukhar 102 se upar chala jaye, 2-3 din se zyada rahe, ya naye symptoms aayein.",
            },
            "fever_low_follow_up": {
                "en": "Do you also have cough, vomiting, rash, or breathing trouble?",
                "hi": "Kya aapko khansi, ulti, rash, ya saans lene mein takleef bhi hai?",
            },
        }
        return texts.get(key, {}).get(lang) or texts.get(key, {}).get("en", "")

    def _localized_causes(self, key: str, language: str | None) -> list[str]:
        lang = self._lang_family(language)
        causes = {
            "high": {
                "en": ["serious infection", "high-risk fever illness"],
                "hi": ["tez sankraman", "high-risk bukhar se judi bimari"],
            },
            "low": {
                "en": ["viral fever", "mild throat or respiratory infection", "dehydration or heat-related fever"],
                "hi": ["viral bukhar", "halki gale ya saans ki infection", "dehydration ya garmi se bukhar"],
            },
        }
        return causes.get(key, {}).get(lang) or causes.get(key, {}).get("en", [])

    def _fallback_decision(self, risk_analysis: dict, user_language: str | None = None) -> dict:
        max_risk = (risk_analysis.get("max_risk_level") or "UNKNOWN").upper()

        # Only escalate for truly critical situations, NOT for unknown/general cases
        if max_risk == "CRITICAL":
            return {
                "decision": "ESCALATE",
                "risk_level": max_risk,
                "response_text": self._localized_text("fallback_escalate", user_language),
                "probable_causes": self._localized_causes("high", user_language),
                "follow_up_question": None,
                "confidence": 0.4,
            }

        # Default to safe advice — ask for more details rather than panic-escalating
        return {
            "decision": "SAFE_ADVICE",
            "risk_level": max_risk if max_risk != "UNKNOWN" else "LOW",
            "response_text": self._localized_text("fallback_safe", user_language),
            "probable_causes": self._localized_causes("low", user_language),
            "follow_up_question": self._localized_text("fallback_safe_follow_up", user_language),
            "confidence": 0.4,
        }

    def _normalize_probable_causes(self, causes) -> list[str]:
        if not isinstance(causes, list):
            return []
        normalized = []
        for cause in causes:
            text = str(cause).strip()
            if text:
                normalized.append(text)
        return normalized[:3]

    def _normalize_result(self, result: dict, risk_analysis: dict) -> dict:
        normalized = {
            "decision": str(result.get("decision", "")).upper(),
            "risk_level": str(result.get("risk_level", "UNKNOWN")).upper(),
            "response_text": str(result.get("response_text", "")).strip(),
            "probable_causes": self._normalize_probable_causes(result.get("probable_causes", [])),
            "follow_up_question": result.get("follow_up_question"),
            "confidence": result.get("confidence", 0.0),
        }

        if normalized["decision"] not in {"SAFE_ADVICE", "ESCALATE"}:
            raise ValueError("Invalid decision value from model")

        if not normalized["response_text"]:
            raise ValueError("Empty response_text from model")

        # ONLY override to ESCALATE when risk is truly CRITICAL
        # Do NOT override for requires_escalation alone — trust the LLM's judgment
        # since many KB docs have Escalation_Required=TRUE even for mild conditions
        max_risk = (risk_analysis.get("max_risk_level") or "UNKNOWN").upper()
        if max_risk == "CRITICAL" and normalized["decision"] != "ESCALATE":
            normalized["decision"] = "ESCALATE"

        # Allow up to 80 words for phone playback — enough for useful advice
        words = normalized["response_text"].split()
        if len(words) > 80:
            normalized["response_text"] = " ".join(words[:80]).rstrip(" ,.;") + "."

        # Allow up to 5 sentences — numbered advice needs multiple sentences
        sentence_parts = re.split(r"(?<=[.!?])\s+", normalized["response_text"].strip())
        sentence_parts = [p for p in sentence_parts if p]
        if len(sentence_parts) > 5:
            normalized["response_text"] = " ".join(sentence_parts[:5]).rstrip(" ,.;") + "."

        if normalized["decision"] == "ESCALATE" and "when to seek help" not in normalized["response_text"].lower():
            normalized["response_text"] = normalized["response_text"].rstrip(" .") + ". When to seek help: as soon as possible."

        try:
            normalized["confidence"] = float(normalized["confidence"])
        except Exception:
            normalized["confidence"] = 0.5
        normalized["confidence"] = max(0.0, min(1.0, normalized["confidence"]))

        if normalized["follow_up_question"] is not None:
            normalized["follow_up_question"] = str(normalized["follow_up_question"]).strip() or None

        # Don't inject hardcoded causes — prefer empty over misleading
        # The LLM should provide relevant causes; if not, we leave it empty

        normalized["response_text"] = self._soften_language(normalized["response_text"])
        return normalized

    def _apply_fever_policy(self, normalized: dict, query: str, risk_analysis: dict, user_language: str | None = None) -> dict:
        fever_f = self._extract_fever_fahrenheit(query)
        if fever_f is None:
            return normalized

        if fever_f > 102:
            normalized["decision"] = "ESCALATE"
            normalized["risk_level"] = "HIGH" if normalized["risk_level"] == "LOW" else normalized["risk_level"]
            normalized["probable_causes"] = self._localized_causes("high", user_language)
            normalized["response_text"] = self._localized_text("fever_high", user_language)
            normalized["follow_up_question"] = None
            return normalized

        if not risk_analysis.get("requires_escalation", False):
            normalized["decision"] = "SAFE_ADVICE"
            normalized["risk_level"] = "LOW"
            normalized["probable_causes"] = self._localized_causes("low", user_language)
            normalized["response_text"] = self._localized_text("fever_low", user_language)
            if not normalized.get("follow_up_question"):
                normalized["follow_up_question"] = self._localized_text("fever_low_follow_up", user_language)

        return normalized

    def _coerce_from_plain_text(self, text: str, risk_analysis: dict, user_language: str | None = None) -> dict:
        if not text or not text.strip():
            raise ValueError("Cannot coerce empty model output")

        cleaned = re.sub(r"```[a-zA-Z]*", "", text).replace("```", "").strip()
        if (
            not cleaned
            or len(cleaned.split()) < 4
            or '"decision"' in cleaned.lower()
            or cleaned.lstrip().startswith("{")
        ):
            return self._fallback_decision(risk_analysis, user_language)

        max_risk = (risk_analysis.get("max_risk_level") or "UNKNOWN").upper()
        # Only escalate for genuinely CRITICAL risk, default to safe advice
        decision = "ESCALATE" if max_risk == "CRITICAL" else "SAFE_ADVICE"
        candidate = {
            "decision": decision,
            "risk_level": max_risk if max_risk != "UNKNOWN" else "LOW",
            "response_text": cleaned,
            "probable_causes": [],
            "follow_up_question": None,
            "confidence": 0.7,
        }
        return self._normalize_result(candidate, risk_analysis)

    def _apply_common_safety_policy(self, query: str, user_language: str | None = None) -> dict | None:
        text = (query or "").strip().lower()
        if not text:
            return None

        gum_markers = [
            "chewing gum",
            "chewingam",
            "swallowed gum",
            "ate gum",
            "gum by accident",
            "swallow gum",
        ]

        if any(marker in text for marker in gum_markers):
            if self._lang_family(user_language) == "hi":
                msg = (
                    "Aksar chewing gum galti se nigalne se nuksan nahi hota. Paani piyen aur normal khana kha sakte hain. "
                    "Agar tez pet dard, ulti, saans ki dikkat, ya bachcha ho aur symptom ho to turant doctor se milen."
                )
            else:
                msg = (
                    "Usually, accidentally swallowing chewing gum is not harmful. Drink water and continue normal meals. "
                    "Seek urgent care only if there is severe stomach pain, vomiting, breathing trouble, or symptoms in a small child."
                )

            return {
                "decision": "SAFE_ADVICE",
                "risk_level": "LOW",
                "response_text": msg,
                "probable_causes": [],
                "follow_up_question": None,
                "confidence": 0.95,
            }

        return None

    async def analyze(
        self,
        query: str,
        context: str,
        risk_analysis: dict,
        history: list = None,
        user_language: str | None = None,
    ) -> dict:
        try:
            common_policy_result = self._apply_common_safety_policy(query, user_language)
            if common_policy_result is not None:
                return common_policy_result

            history = history[-6:] if history else []
            hist_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

            risk_summary = (
                f"Max Risk Level: {risk_analysis['max_risk_level']}\n"
                f"Requires Escalation: {risk_analysis['requires_escalation']}"
            )

            target_language = (user_language or "en").strip()

            prompt = (
                f"{SYSTEM_PROMPT}\n\n"
                f"RETRIEVED PROTOCOLS:\n{context}\n\n"
                f"RISK SUMMARY:\n{risk_summary}\n\n"
                f"RECENT HISTORY:\n{hist_str}\n\n"
                f"USER QUERY: {query}\n\n"
                f"RESPONSE LANGUAGE: {target_language} (Use the same language as the caller.)\n\n"
                "Keep response_text short for phone playback: max 35 words, at most 2 short sentences, and no long paragraph. "
                "Return exactly one JSON object and no extra text."
            )

            response = await asyncio.to_thread(self._generate_content_sync, prompt)
            raw_output = self._response_to_text(response).strip()

            if not raw_output:
                retry_prompt = (
                    f"{SYSTEM_PROMPT}\n\n"
                    "Respond in one short plain-text answer for phone call playback. "
                    "Do not use markdown. Limit response to max 35 words and at most 2 short sentences.\n\n"
                    f"USER QUERY: {query}\n"
                    f"RISK SUMMARY: {risk_summary}\n"
                    f"RESPONSE LANGUAGE: {target_language}\n"
                )
                retry_response = await asyncio.to_thread(self._generate_content_sync, retry_prompt)
                retry_text = self._response_to_text(retry_response).strip()
                if retry_text:
                    normalized = self._coerce_from_plain_text(retry_text, risk_analysis, user_language)
                    return self._apply_fever_policy(normalized, query, risk_analysis, user_language)

            try:
                parsed = json.loads(self._extract_json_object(raw_output))
                normalized = self._normalize_result(parsed, risk_analysis)
                return self._apply_fever_policy(normalized, query, risk_analysis, user_language)
            except Exception:
                if raw_output:
                    normalized = self._coerce_from_plain_text(raw_output, risk_analysis, user_language)
                    return self._apply_fever_policy(normalized, query, risk_analysis, user_language)
                raise

        except Exception:
            logger.exception("LLM analyze failed; applying deterministic fallback")
            normalized = self._fallback_decision(risk_analysis, user_language)
            return self._apply_fever_policy(normalized, query, risk_analysis, user_language)


llm = LLMService()
