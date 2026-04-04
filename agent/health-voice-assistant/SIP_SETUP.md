# 📞 SIP Trunk Setup — Twilio → LiveKit → Health Agent

This guide walks you through connecting your **Twilio phone number** to your **LiveKit agent** via a SIP trunk, so callers can speak to the AI health assistant in real-time.

---

## Architecture

```
Caller dials Twilio Number
        │
        ▼
  Twilio SIP Trunk
        │ (SIP INVITE)
        ▼
  LiveKit SIP Server
        │ (Creates Room)
        ▼
  LiveKit Room ←→ Agent Process (agent.py)
        │               │
        │          STT ←─┤ Deepgram (streaming)
        │          LLM ←─┤ Gemini + RAG
        │          TTS ←─┤ ElevenLabs (streaming)
        │               │
        ▼               ▼
  Caller hears AI response in real-time
```

---

## Prerequisites

- [x] Twilio account with a phone number
- [x] LiveKit Cloud account ([sign up free](https://cloud.livekit.io))
- [x] LiveKit CLI installed (`winget install LiveKit.LiveKitCLI`)
- [x] API keys for Deepgram, Google, and ElevenLabs

---

## Step 1: LiveKit Cloud Setup

### 1a. Create a LiveKit Project
1. Go to [LiveKit Cloud](https://cloud.livekit.io)
2. Create a new project (e.g., `immihelp-health`)
3. Note your **API Key**, **API Secret**, and **WebSocket URL**

### 1b. Authenticate CLI
```bash
lk cloud auth
```

---

## Step 2: Configure SIP Inbound Trunk in LiveKit

### 2a. Create a SIP Trunk Configuration File

Create `sip-trunk-inbound.json`:
```json
{
  "trunk": {
    "name": "Twilio Immihelp Trunk",
    "numbers": ["+1YOUR_TWILIO_NUMBER"],
    "auth_username": "",
    "auth_password": ""
  }
}
```

> Replace `+1YOUR_TWILIO_NUMBER` with your actual Twilio phone number.

### 2b. Register the Trunk with LiveKit
```bash
lk sip inbound create sip-trunk-inbound.json
```

This returns a **SIP URI** like:
```
sip:YOUR_TRUNK_ID@sip.livekit.cloud
```

**Save this URI** — you'll need it for the Twilio side.

### 2c. Create a SIP Dispatch Rule

Create `sip-dispatch.json`:
```json
{
  "rule": {
    "dispatchRuleIndividual": {
      "roomPrefix": "health-call-"
    },
    "trunkIds": ["YOUR_TRUNK_ID"]
  }
}
```

Register it:
```bash
lk sip dispatch create sip-dispatch.json
```

This tells LiveKit: *"When a call arrives on this trunk, create a room named `health-call-{random}` and dispatch it to the registered agent."*

---

## Step 3: Configure Twilio SIP Trunk

### 3a. Create Elastic SIP Trunk
1. Go to [Twilio Console → Elastic SIP Trunking](https://console.twilio.com/us1/develop/sip-trunking/trunks)
2. Click **Create new SIP Trunk**
3. Name it `LiveKit Health Agent`

### 3b. Set Origination URI
1. Go to the trunk's **Origination** tab
2. Add a new Origination URI:
   ```
   sip:YOUR_TRUNK_ID@sip.livekit.cloud;transport=tls
   ```
3. Set **Priority** to `10`, **Weight** to `10`

### 3c. Link Your Phone Number
1. Go to the trunk's **Numbers** tab
2. Click **Add a Number**
3. Select your Twilio phone number
4. Save

### 3d. (Optional) Configure Authentication
If you specified credentials in the LiveKit trunk config, add them in Twilio's **General Settings** under **Credential List**.

---

## Step 4: Set Environment Variables

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

Key variables:
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
DEEPGRAM_API_KEY=your-deepgram-key
ELEVENLABS_API_KEY=your-elevenlabs-key
GOOGLE_API_KEY=your-google-key
```

---

## Step 5: Run the Agent

### Development Mode (local testing)
```bash
cd agent/health-voice-assistant
pip install -r requirements.txt
python app/agent.py dev
```

### Production Mode
```bash
python app/agent.py start
```

### Deploy to LiveKit Cloud
```bash
lk agent create
```

---

## Step 6: Test It

1. Make sure the agent is running (you should see `Worker registered` in logs)
2. **Call your Twilio phone number** from any phone
3. You should hear the AI greeting within 1-2 seconds
4. Describe your symptoms — the agent will respond with medical advice
5. **Try interrupting** — speak while the agent is talking. It should stop and listen

### Testing without a phone (Browser)
Use the LiveKit Playground:
1. Go to [agents-playground.livekit.io](https://agents-playground.livekit.io)
2. Enter your LiveKit Cloud project credentials
3. Set Agent Name to `health-assistant`
4. Click Connect and speak

---

## Troubleshooting

### Call doesn't connect
- [ ] Check Twilio SIP trunk is active (Twilio Console → SIP Trunking)
- [ ] Verify the Origination URI matches your LiveKit SIP address
- [ ] Ensure the agent process is running (`python app/agent.py dev`)
- [ ] Check LiveKit Console → Rooms to see if a room was created

### Agent doesn't respond
- [ ] Check agent logs for STT errors (Deepgram API key valid?)
- [ ] Check LLM logs (Google API key valid?)
- [ ] Check TTS logs (ElevenLabs API key valid?)
- [ ] Verify `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` are set

### Audio quality issues
- [ ] The agent uses `BVCTelephony()` noise cancellation for SIP calls automatically
- [ ] For browser: it uses `BVC()` standard noise cancellation
- [ ] Check Deepgram model — `nova-3` with `multi` language gives best results

### RAG not working
- [ ] Check that `data/chroma_db` directory exists and is populated
- [ ] Test RAG directly: `python -c "from app.services.rag import rag; print(rag.retrieve('headache'))"`
- [ ] Check knowledge base documents in `app/knowledge_base/documents/`

---

## Architecture Comparison

| Feature | Old (Twilio Webhooks) | New (LiveKit SIP) |
|---------|----------------------|-------------------|
| Latency | 3-8 seconds | < 500ms |
| Interruption | ❌ Not possible | ✅ Full-duplex |
| Audio flow | Record → Download → Process → Respond | Stream → Process → Stream |
| Turn-taking | Artificial (silence detection) | Natural (VAD) |
| Concurrency | One utterance at a time | Continuous streaming |
| Error recovery | Page-level (whole turn lost) | Graceful (retry per chunk) |
