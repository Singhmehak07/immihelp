import os

BASE_DIR = r"c:\Users\Mehakpreet Singh\Documents\iimihelp\immihelp\health-voice-assistant"

def create_file(path, content):
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created {path}")

# 1. requirements.txt
create_file("requirements.txt", """
fastapi==0.115.0
uvicorn[standard]==0.30.0
twilio==9.3.0
deepgram-sdk==3.7.0
google-generativeai==0.8.0
langchain==0.3.0
langchain-google-genai==2.0.0
langchain-community==0.3.0
chromadb==0.5.0
python-dotenv==1.0.1
pydantic-settings==2.5.0
httpx==0.27.0
python-multipart==0.0.12
aiofiles==24.1.0
""")

# 2. .env
create_file(".env", """
TWILIO_ACCOUNT_SID=placeholder
TWILIO_AUTH_TOKEN=placeholder
TWILIO_PHONE_NUMBER=+10000000000
DEEPGRAM_API_KEY=placeholder
GOOGLE_API_KEY=placeholder
ELEVENLABS_API_KEY=placeholder
ELEVENLABS_VOICE_ID=placeholder
APP_BASE_URL=https://placeholder.ngrok.io
ESCALATION_PHONE=+10000000000
ENVIRONMENT=development
""")

# 3. .gitignore
create_file(".gitignore", """
__pycache__/
*.pyc
.env
data/
""")

# 4. Dockerfile
create_file("Dockerfile", """
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""")

# 5. init files
for path in ["app/__init__.py", "app/api/__init__.py", "app/services/__init__.py", "app/knowledge_base/__init__.py", "app/prompts/__init__.py", "tests/__init__.py"]:
    create_file(path, "")

# tests/test_pipeline.py
create_file("tests/test_pipeline.py", """
def test_pipeline():
    pass
""")

# app/config.py
create_file("app/config.py", """
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    deepgram_api_key: str
    google_api_key: str
    elevenlabs_api_key: str
    elevenlabs_voice_id: str
    app_base_url: str
    escalation_phone: str
    environment: str = "development"

    chroma_persist_dir: str = "./data/chroma_db"
    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
""")

# app/prompts/system.py
create_file("app/prompts/system.py", r'''
SYSTEM_PROMPT = """You are a health assistant, NOT a doctor.
ONLY use the retrieved medical protocols provided to you. NEVER invent medical information.
If there is no relevant protocol for the user's symptoms, you MUST ESCALATE.
If the user mentions any danger sign or critical symptom, you MUST ESCALATE.
Never diagnose conditions; only provide symptom-based guidance.
Keep your responses under 150 words as they will be spoken aloud over the phone.
Use simple, easy-to-understand language. Avoid medical jargon.

Escalation triggers include, but are not limited to: chest pain, cant breathe, unconscious, severe bleeding, infant <3 months, pregnancy complications, seizures, fever >39.5C, suicidal thoughts, uncertainty.

Tone: warm, calm, numbered steps if providing advice, end with "when to seek help".

Respond ONLY in JSON format:
{
  "decision": "SAFE_ADVICE" or "ESCALATE",
  "risk_level": "LOW", "HIGH", or "CRITICAL",
  "response_text": "Spoken response text",
  "follow_up_question": "string or null",
  "confidence": 0.95
}"""
''')

# documents
create_file("app/knowledge_base/documents/01_emergency_signs.md", """
## RISK_LEVEL: CRITICAL
### Condition: General Emergency Signs
**Symptoms:** Adults: chest pain, stroke, severe bleeding, poisoning, unconsciousness. Children <5: unable to drink, convulsions, chest indrawing. Pregnant: vaginal bleeding, eclampsia.
**Home Care Advice:**
1. Keep the patient safe and still.
**When to seek help:** Immediately.
**DO NOT:** Wait.
**Escalation_Required:** TRUE
---
""")

create_file("app/knowledge_base/documents/02_fever.md", """
## RISK_LEVEL: LOW
### Condition: Mild Fever in Adults
**Symptoms:** elevated temperature 37.5-38.5C, mild body aches
**Home Care Advice:**
1. Rest and drink fluids
2. Paracetamol 500mg every 6 hours, max 4 doses per day
3. Lukewarm cloth on forehead
4. Monitor temperature every 4 hours
**When to seek help:** fever persists beyond 3 days or exceeds 39C
**DO NOT:** give aspirin to children under 16
**Escalation_Required:** FALSE
---
## RISK_LEVEL: LOW
### Condition: Mild Fever in Children
**Symptoms:** mild fever, >3mo
**Home Care Advice:**
1. Hydrate well.
**When to seek help:** >2 days.
**DO NOT:** overdress.
**Escalation_Required:** FALSE
---
## RISK_LEVEL: HIGH
### Condition: High Fever
**Symptoms:** >39C
**Home Care Advice:**
1. Cool the person.
**When to seek help:** Now.
**DO NOT:** ignore.
**Escalation_Required:** TRUE
---
## RISK_LEVEL: CRITICAL
### Condition: Infant Fever
**Symptoms:** fever infant <3mo
**Home Care Advice:**
1. Seek urgent help.
**When to seek help:** Immediately.
**DO NOT:** give unprescribed medicine.
**Escalation_Required:** TRUE
---
""")

create_file("app/knowledge_base/documents/03_diarrhea.md", """
## RISK_LEVEL: LOW
### Condition: Mild Diarrhea Adults
**Symptoms:** <3 days without severe dehydration
**Home Care Advice:**
1. Drink ORS: 6tsp sugar + 1/2tsp salt + 1L water
**When to seek help:** >3 days or dehydration signs
**DO NOT:** take anti-diarrheals without advice
**Escalation_Required:** FALSE
---
## RISK_LEVEL: HIGH
### Condition: Diarrhea with Dehydration
**Symptoms:** dehydration signs
**Home Care Advice:**
1. Sip ORS continuously.
**When to seek help:** Go to clinic.
**DO NOT:** stop fluids.
**Escalation_Required:** TRUE
---
## RISK_LEVEL: CRITICAL
### Condition: Bloody or Infant
**Symptoms:** bloody diarrhea or infant
**Home Care Advice:**
1. Hospital immediately.
**When to seek help:** Now.
**DO NOT:** wait.
**Escalation_Required:** TRUE
---
""")

create_file("app/knowledge_base/documents/04_wounds.md", """
## RISK_LEVEL: LOW
### Condition: Minor Wounds
**Symptoms:** clean cuts, minor scrapes
**Home Care Advice:**
1. Wash hands, clean wound gently. Apply pressure, then bandage.
**When to seek help:** signs of infection
**DO NOT:** apply dirty materials
**Escalation_Required:** FALSE
---
## RISK_LEVEL: HIGH
### Condition: Deep Wounds
**Symptoms:** deep/animal bite
**Home Care Advice:**
1. Clean gently and cover.
**When to seek help:** Medical care for stitches/rabies
**DO NOT:** attempt to close yourself
**Escalation_Required:** TRUE
---
## RISK_LEVEL: CRITICAL
### Condition: Severe Bleeding
**Symptoms:** uncontrolled bleeding
**Home Care Advice:**
1. Apply continuous firm pressure. Elevate.
**When to seek help:** Call emergency services immediately.
**DO NOT:** remove pressure pad if soaked
**Escalation_Required:** TRUE
---
""")

create_file("app/knowledge_base/documents/05_respiratory.md", """
## RISK_LEVEL: LOW
### Condition: Mild Cough
**Symptoms:** mild cough
**Home Care Advice:**
1. Warm fluids, honey not <1yr.
**When to seek help:** >2 weeks
**DO NOT:** give honey to babies
**Escalation_Required:** FALSE
---
## RISK_LEVEL: HIGH
### Condition: Persistent Cough
**Symptoms:** cough >2wks
**Home Care Advice:**
1. Be seen by doctor.
**When to seek help:** Next available appointment.
**DO NOT:** ignore
**Escalation_Required:** TRUE
---
## RISK_LEVEL: CRITICAL
### Condition: Breathing Difficulty
**Symptoms:** difficulty breathing, blue lips
**Home Care Advice:**
1. Keep the person calm.
**When to seek help:** Immediately.
**DO NOT:** lay flat if struggling to breathe.
**Escalation_Required:** TRUE
---
""")

create_file("app/knowledge_base/documents/06_maternal.md", """
## RISK_LEVEL: LOW
### Condition: Normal Pregnancy Symptoms
**Symptoms:** morning sickness, swelling, back pain
**Home Care Advice:**
1. Rest. Small meals.
**When to seek help:** Severe vomiting.
**DO NOT:** take unprescribed drugs.
**Escalation_Required:** FALSE
---
## RISK_LEVEL: HIGH
### Condition: Pregnancy Complications
**Symptoms:** bleeding, headache, blurred vision
**Home Care Advice:**
1. Prep to go to clinic.
**When to seek help:** Promptly.
**DO NOT:** delay.
**Escalation_Required:** TRUE
---
## RISK_LEVEL: CRITICAL
### Condition: Severe Emergency
**Symptoms:** eclampsia, water breaking <37wks
**Home Care Advice:**
1. Transport immediately.
**When to seek help:** Emergency.
**DO NOT:** wait at home.
**Escalation_Required:** TRUE
---
""")

create_file("app/knowledge_base/documents/07_child_health.md", """
## RISK_LEVEL: LOW
### Condition: Minor child symptoms
**Symptoms:** rash, teething
**Home Care Advice:**
1. Keep comfortable.
**When to seek help:** fever develops.
**DO NOT:** give aspirin.
**Escalation_Required:** FALSE
---
## RISK_LEVEL: HIGH
### Condition: Sick child
**Symptoms:** not eating, persistent vomiting
**Home Care Advice:**
1. Small sips of fluid.
**When to seek help:** Seek evaluation.
**DO NOT:** force feed.
**Escalation_Required:** TRUE
---
## RISK_LEVEL: CRITICAL
### Condition: Critical Signs
**Symptoms:** convulsions, unconscious
**Home Care Advice:**
1. Side position. Protect airway.
**When to seek help:** Emergency.
**DO NOT:** put fingers in mouth.
**Escalation_Required:** TRUE
---
""")
