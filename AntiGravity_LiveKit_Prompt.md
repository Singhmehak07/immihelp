# 🚀 AntiGravity × LiveKit: Real-Time Voice Agent Hackathon Build

## Context
AntiGravity has designed a **LiveKit SIP Trunk Agent** architecture to replace Twilio's turn-based webhook model with **true real-time, full-duplex conversational AI** for a health voice assistant.

**Goal:** In a hackathon timeframe, build a working demo that showcases:
1. ✅ Sub-500ms first response latency
2. ✅ Natural conversational interruption (barge-in)
3. ✅ Medical knowledge base integration via RAG
4. ✅ Production-ready event streaming architecture (not request/response)

---

## The Ask

**Build a working LiveKit SIP voice agent that:**

### Core Requirements
- [ ] Accepts inbound calls via **Twilio SIP trunk → LiveKit Room → Agent Process**
- [ ] Uses **Deepgram for STT** (streaming, low-latency)
- [ ] Uses **Gemini (Google) for LLM** with RAG function calling
- [ ] Uses **ElevenLabs or Google TTS** for speech synthesis
- [ ] Registers the existing **RAG pipeline** (`app.services.rag.retrieve`) as an LLM tool
- [ ] **Agent loop runs continuously** (not request/response) while room is active
- [ ] User can **interrupt mid-sentence** and agent responds to new input immediately

### Stretch Goals (if time permits)
- [ ] Voice quality A/B test (ElevenLabs vs. Google TTS)
- [ ] Error recovery (STT fails, LLM timeout, RAG returns empty)
- [ ] Session state persistence (multi-turn context)
- [ ] Sentiment detection (agent tone shifts based on user distress level)

### What's Already Done
- ✅ Twilio account + SIP trunk concept
- ✅ RAG service (`app.services.rag`) with medical knowledge base
- ✅ Basic FastAPI scaffold
- ✅ Deepgram, Google, ElevenLabs API accounts ready

### What You Need to Build
- 🔨 **LiveKit agent entrypoint** (`agent/health-voice-assistant/app/agent.py`)
- 🔨 **SIP inbound routing** (LiveKit Room naming, SIP URI config)
- 🔨 **RAG function tool integration** (wrap `rag_service.retrieve` as LLM callable)
- 🔨 **Error handling & timeouts** (don't let STT/LLM block the loop)
- 🔨 **Demo script** (show call → response latency → interruption)

---

## Implementation Strategy (AntiGravity's Vision)

### 1. **The Core Architecture**
Instead of:
```
Phone → Twilio → HTTP POST → FastAPI handler → wait for response → play TTS
```

Build:
```
Phone → Twilio SIP URI → LiveKit Room (WebRTC) → Agent process (streaming loop) → TTS stream
```

**Why?** The agent is always listening. No waiting. No turn-based delays.

### 2. **The Agent Loop (Pseudocode)**
```python
async with VoicePipelineAgent(
    stt=Deepgram(),        # Streaming input
    llm=Gemini(),          # With RAG tool
    tts=ElevenLabs(),      # Streaming output
) as agent:
    agent.start(room)      # Subscribe to room audio
    await agent.say("Hi, I'm your health assistant.")
    
    # Now the agent continuously:
    # 1. Listens to user audio stream
    # 2. Detects speech endpoint (VAD)
    # 3. Sends transcript to LLM
    # 4. LLM calls RAG if needed ("What is type 2 diabetes?")
    # 5. TTS streams response back
    # 6. User can interrupt at any point
```

**That's it.** The magic is in the streaming—no HTTP round trips, no recording+download.

### 3. **RAG as an LLM Tool (The Integrator)**
```python
@agents.llm.FunctionContext
def lookup_medical_condition(query: str) -> str:
    """User asked about a medical condition. Fetch from knowledge base."""
    results = rag_service.retrieve(query, top_k=3)
    return "\n".join(results) if results else "I don't have specific info on that."

# Register with LLM:
llm = google.LLM(
    model="gemini-2.0-flash",
    tools=[lookup_medical_condition]  # <-- Agent can call this mid-response
)
```

When the user says "What's type 2 diabetes?":
- Gemini sees the query
- **Gemini itself decides** to call `lookup_medical_condition`
- RAG retrieves relevant info
- Gemini synthesizes a response
- TTS streams it

**No hardcoded if/then logic. Pure LLM reasoning.**

### 4. **SIP Trunking (The Bridge)**
Twilio side:
- Create Elastic SIP trunk pointing to: `sip://your-livekit-server.com`
- Route incoming calls to that SIP URI

LiveKit side:
- Create SIP inbound rule: when call arrives, create Room named `health-call-{id}`
- Spawn agent process for that room
- Agent joins as participant, serves as the "other end" of the call

**The user talks to the agent like they're on a regular phone call.**

---

## Dependencies to Add

```txt
# requirements.txt
livekit>=0.12.0
livekit-agents>=0.11.2
livekit-plugins-deepgram>=0.11.0
livekit-plugins-google>=0.11.0
livekit-plugins-elevenlabs>=0.11.0
```

## Environment Variables

```bash
# Existing
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# New
LIVEKIT_URL=wss://your-livekit-cloud.livekit.cloud  # or self-hosted
LIVEKIT_API_KEY=devkey...
LIVEKIT_API_SECRET=...

DEEPGRAM_API_KEY=...
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=adam  # or your choice

# Optional fallback
GOOGLE_API_KEY=...
```

---

## Judging Criteria (Why This Wins)

### 1. **Live Demo Power**
```
Judge: "Make a call to your system."
You: [Dial Twilio number]
Agent: [Responds in <500ms, sounds natural]
Judge: "Now interrupt it mid-sentence."
You: "Wait, what about side effects?"
Agent: [Stops, re-listens, answers new question immediately]
Judge: 😲 "How is this possible with webhooks?"
You: "It's not. We're using WebRTC + streaming."
```

**That 5-second interaction sells the entire project.**

### 2. **Technical Novelty**
- Most teams build chatbots with pre-recorded responses
- You're building **real-time streaming AI** with **natural interruption**
- You integrated a **medical knowledge base dynamically**
- You showed **sub-500ms latency** (not possible with HTTP webhooks)

### 3. **Clear Problem Statement**
- Problem: Twilio webhooks = artificial turn-taking, long delays, poor UX
- Solution: LiveKit WebRTC agents = natural conversation
- Impact: Users get better healthcare info faster

### 4. **Working Code**
- Not theoretical. Not a deck. A **functioning demo** that runs on stage.
- Judges can call your number. They experience the magic.

---

## Hackathon Day Timeline

### **Hour 0–2: Setup**
- [ ] Fork `livekit-agents` repo, explore examples
- [ ] Set up LiveKit Cloud account (free tier)
- [ ] Configure Twilio SIP trunk (5 min, follow `SIP_SETUP.md`)
- [ ] Set all env vars

### **Hour 2–6: Agent Loop**
- [ ] Write minimal `agent.py` (copy from livekit examples)
- [ ] Get one test call to work (just STT→TTS, no LLM)
- [ ] Verify latency is acceptable

### **Hour 6–10: RAG Integration**
- [ ] Wrap `rag_service.retrieve()` as `@agents.llm.FunctionContext`
- [ ] Pass it to Gemini LLM
- [ ] Test: ask agent a medical question, verify RAG is called

### **Hour 10–12: Polish & Error Handling**
- [ ] Try interrupting the agent (should work already)
- [ ] Add timeouts to STT/LLM (don't block forever)
- [ ] Handle edge cases (no internet, RAG returns empty, etc.)

### **Hour 12–14: Demo & Slides**
- [ ] Record a ~2min demo video showing:
  - Call connects and responds in <500ms
  - Agent answers medical question using RAG
  - Interrupt mid-sentence works
- [ ] Write 5-bullet pitch
- [ ] Practice 1-min explanation

### **Hour 14–16: Sleep & Final Check**
- [ ] Run final demo at least once
- [ ] Make sure Twilio number works
- [ ] Charge your phone (for demo call)
- [ ] Sleep

---

## The Pitch (What to Say)

> "We replaced Twilio's turn-based webhook model with LiveKit's real-time WebRTC agents. 
> 
> Instead of recording audio, waiting for STT, waiting for LLM response, generating TTS, and playing it back—which takes 3+ seconds—our agent **streams everything** in parallel. 
> 
> The user gets a response in under 500ms. And if they want to interrupt? They can. Right now. Mid-sentence. Because WebRTC is full-duplex.
> 
> We integrated a medical knowledge base as an LLM function tool, so when users ask about conditions, the agent dynamically retrieves and synthesizes the answer.
> 
> [Demo call]
> 
> This matters for health apps. Users want instant, natural conversation. Not artificial pauses."

---

## Success Metrics (Hackathon Edition)

✅ **You win if:**
- Judges can call your number and get a response
- Response latency is visibly fast (<1 second)
- Agent can interrupt naturally
- RAG integration works (agent answers medical question correctly)
- Your pitch is clear (judges understand the problem and solution)

❌ **You lose if:**
- SIP trunk doesn't route calls (debug: check LiveKit logs + Twilio logs)
- STT/LLM timeouts kill the call (add error handling)
- Agent crashes mid-demo (run it in a screen/tmux session, restart if needed)
- Your pitch is too technical (focus on UX, not architecture)

---

## Troubleshooting Checklists

### "Call isn't connecting"
- [ ] Twilio SIP trunk is active (check Twilio console)
- [ ] LiveKit Room is created (check LiveKit logs)
- [ ] Agent process is running (`python agent.py start`)
- [ ] Correct SIP URI in Twilio (should match your LiveKit server)

### "Agent doesn't respond"
- [ ] Is STT listening? (Add debug logs: `print(f"Heard: {text}")`)
- [ ] Is LLM generating? (Add logs: `print(f"LLM response: {response}")`)
- [ ] Is TTS playing? (Should hear audio in call)

### "Interruption doesn't work"
- [ ] Is VAD (voice activity detection) enabled? (It should be auto)
- [ ] Try speaking louder/clearer
- [ ] Check agent's interrupt handling (livekit-agents should handle it)

### "RAG function not being called"
- [ ] Check if LLM sees the tool definition (log tool list)
- [ ] Ask a question that *requires* RAG (e.g., "What is type 2 diabetes?")
- [ ] Check if RAG service itself works (test `rag_service.retrieve()` directly)

---

## References & Links

- **LiveKit Agents Docs:** https://docs.livekit.io/agents/overview/
- **LiveKit SIP Inbound:** https://docs.livekit.io/sip/overview/
- **Deepgram Streaming STT:** https://developers.deepgram.com/
- **Google Gemini API:** https://ai.google.dev/
- **ElevenLabs TTS:** https://elevenlabs.io/

---

## Final Notes

**AntiGravity's genius here:** They realized that **the problem isn't the LLM, it's the I/O model.** 

Webhooks are request/response. Phone calls are streams. By switching to WebRTC agents (which are streaming-first), they unlocked:
- Real-time responsiveness
- Natural interruption
- Better user experience

This is a **fundamental architectural improvement**, not just a feature bump.

For a hackathon, this is **exactly** the kind of insight that wins. You're solving a real problem with a clever architectural shift.

---

## TL;DR for Busy Devs

1. Write `agent.py` that runs a `VoicePipelineAgent` loop
2. Wrap RAG as an LLM function tool
3. Point Twilio SIP trunk to LiveKit
4. Make a test call
5. Interrupt mid-sentence to flex
6. Demo on stage
7. Win 🏆

**Estimated dev time: 8–12 hours.** Very doable for a hackathon.

---

**Good luck, AntiGravity team! 🚀**
