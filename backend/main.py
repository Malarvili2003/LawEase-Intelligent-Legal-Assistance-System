from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import io
from fastapi import FastAPI, UploadFile, File
import pdfplumber
import docx
from app.llm import generate_with_ollama_http



# --------------------
# Ollama Config
# --------------------
OLLAMA_HTTP = "http://127.0.0.1:11434/api"
OLLAMA_MODEL = "qwen2.5:1.5b"

# --------------------
# FastAPI Init
# --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Global Document Memory
# --------------------
DOCUMENT_MEMORY = ""   # stores extracted doc text


# --------------------
# Pydantic Models
# --------------------
class ChatRequest(BaseModel):
    prompt: str

class TranslateRequest(BaseModel):
    text: str
    from_lang: str
    to_lang: str

class DocumentUpload(BaseModel):
    content: str   # extracted text from PDF/DOCX


# --------------------
# Helpers
# --------------------



def is_legal_query(prompt: str) -> bool:
    """Recognize legal intent using keyword-based detection."""
    keywords = [

    # ------------------ GENERAL LAW ------------------
    "law", "legal", "lawyer", "advocate", "attorney", "counsel",
    "lawsuit", "litigation", "jurisdiction", "appeal", "tribunal",
    "hearing", "petition", "motion", "judgment", "order", "decree",
    "injunction", "trial", "case", "case law", "precedent",
    "statute", "regulation", "compliance", "bylaw", "fine",
    "violation", "offence", "legal rights", "remedy", "legal action",

    # ------------------ CRIMINAL LAW ------------------
    "crime", "criminal", "ipc", "crpc", "arrest", "bail", "custody",
    "charge sheet", "fir", "complaint", "police", "accused",
    "witness", "evidence", "testimony", "statement", "investigation",
    "charges", "sections", "forensic", "remand", "cognizable",
    "non-cognizable", "summons", "warrant", "detention",
    "cross examination",

    # ------------------ CIVIL LAW ------------------
    "civil", "damages", "negligence", "compensation", "tort",
    "liability", "nuisance", "defamation", "harassment",
    "injury", "loss", "suit", "cause of action",

    # ------------------ CONTRACT & BUSINESS LAW ------------------
    "contract", "agreement", "breach", "lease", "mou", "nda",
    "consideration", "terms", "conditions", "indemnity", "clause",
    "liquidated damages", "purchase order", "service agreement",
    "commercial", "agency", "partnership", "llp",

    # ------------------ CORPORATE & TAX LAW ------------------
    "company", "corporate", "gst", "tax", "director", "shareholder",
    "roc", "mca", "compliance", "audit", "insolvency", "bankruptcy",
    "ibc", "liquidator", "esop", "startup india", "msme",

    # ------------------ PROPERTY LAW ------------------
    "property", "ownership", "eviction", "rent", "tenant",
    "landlord", "mortgage", "possession", "occupancy", "sale deed",
    "gift deed", "partition", "ancestral", "encroachment",
    "land registration", "patta", "chitta", "fmb", "mutation",

    # ------------------ FAMILY LAW ------------------
    "marriage", "divorce", "custody", "alimony", "498a", "domestic",
    "dowry", "maintenance", "child support", "guardianship",
    "family court", "adoption", "matrimonial",

    # ------------------ LABOUR & EMPLOYMENT LAW ------------------
    "labour", "employee", "wages", "salary", "bonus",
    "gratuity", "pf", "esi", "termination", "retrenchment",
    "posh", "sexual harassment", "workplace", "employment contract",

    # ------------------ INTELLECTUAL PROPERTY LAW ------------------
    "copyright", "trademark", "patent", "ip", "infringement",
    "cease and desist", "licensing", "royalty",

    # ------------------ CYBER LAW ------------------
    "cyber", "privacy", "data", "dpdp", "hacking", "phishing",
    "otp fraud", "cybercrime", "it act", "misuse", "breach",

    # ------------------ CONSUMER LAW ------------------
    "consumer", "refund", "warranty", "guarantee",
    "defective", "deficiency", "ecommerce", "consumer court",

    # ------------------ DOCUMENTS & DRAFTING ------------------
    "legal notice", "affidavit", "power of attorney", "poa",
    "deed", "undertaking", "agreement", "contract", "will",
    "settlement", "loan agreement", "terms of service",
    "privacy policy", "draft", "clause", "notary",

    # ------------------ COURT & PROCEDURE ------------------
    "court", "judge", "summon", "warrant", "notice",
    "high court", "supreme court", "district court",
    "tribunal", "appeal", "revision", "review", "stay order",
    "adjournment", "proceedings", "hearing date",

    # ------------------ RIGHTS & PROTECTION ------------------
    "fundamental rights", "article", "right to information",
    "rti", "human rights", "equality", "freedom", "protection",
    "constitution", "constitutional law",

    # ------------------ SPECIAL ACTS (India) ------------------
    "motor vehicles act", "domestic violence act", "it act",
    "ni act", "138", "rtpcr", "id act", "ipc section",
    "police act", "posco", "sc/st act",

    # ------------------ FINANCIAL & BANKING ------------------
    "loan", "emi", "recover", "recovery agent", "credit",
    "bank fraud", "npas", "cibil", "insurance", "policy",
    "claim", "settlement", "foreclosure", "charge",

    # ------------------ REAL ESTATE ------------------
    "rera", "builder", "possession delay", "flat", "apartment",
    "agreement for sale", "registration", "stamp duty",

    # ------------------ MISCELLANEOUS LEGAL ------------------
    "license", "permit", "fine", "penalty", "rules",
    "guidelines", "authority", "ombudsman"
]


    p = prompt.lower()
    return any(k in p for k in keywords)

def is_scenario_query(prompt: str) -> bool:
    scenario_indicators = [
        # First-person indicators
        "i was", "i am", "i have", "my", "me", "we", "us",

        # Incidents / actions
        "harassed", "threatened", "abused", "cheated", "forced",
        "assaulted", "stalked", "blackmailed", "scammed", "robbed",
        "terminated", "evicted", "denied", "molested",

        # Context
        "workplace", "office", "college", "school",
        "street", "online", "whatsapp", "instagram",

        # Legal intent phrasing
        "what should i do", "what action can i take",
        "can i complain", "legal action", "file a case",
        "fir", "complaint", "procedure", "next steps"
    ]

    p = prompt.lower()
    return any(k in p for k in scenario_indicators)



# ------------------------------------------------
# DOCUMENT UPLOAD ENDPOINT
# ------------------------------------------------

def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_docx_text(file):
    doc = docx.Document(file)
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    global DOCUMENT_MEMORY

    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        text = extract_pdf_text(file.file)
    elif filename.endswith(".docx"):
        text = extract_docx_text(file.file)
    else:
        return {"error": "Unsupported file type"}

    DOCUMENT_MEMORY = text

    return {
        "status": "success",
        "filename": file.filename,
        "characters": len(text),
        "message": "Document uploaded successfully"
    }

# Conversation title Generation
@app.post("/translate")
async def translate_handler(req: TranslateRequest):
    text = req.text.strip()
    from_lang = req.from_lang.strip() or "auto"
    to_lang = req.to_lang.strip() or "English"

    if not text:
        return {"translation": "No text provided for translation."}

    # Very explicit, minimal prompt
    prompt = (
        "You are a professional translator. "
        f"Translate the following text from {from_lang} to {to_lang}.\n\n"
        "IMPORTANT RULES:\n"
        "- Return ONLY the translated text and nothing else (no labels, no explanation, no punctuation outside the translation).\n"
        "- Preserve meaning and punctuation inside the translated sentence only.\n"
        "- If there is ambiguity about dialect, use the most common, neutral form.\n\n"
        "Text to translate:\n"
        f"{text}\n\n"
        "Return only the translation (one response)."
    )

    # TEMP DEBUG: log prompt (remove in production)
    print("----- TRANSLATE PROMPT -----")
    print(prompt)
    print("----------------------------")

    result = generate_with_ollama_http(prompt)

    # TEMP DEBUG: log raw model result
    print("----- MODEL RAW RESULT -----")
    print(repr(result))
    print("----------------------------")

    if not result:
        return {"translation": "[LLM unavailable] Could not contact Ollama."}

    # If the model returns extra text, attempt a safe postclean:
    #  - remove common prefixes like "Translation:" or "(Translated ...)" if present
    cleaned = result.strip()
    # remove accidental labels
    for prefix in ["Translation:", "Translated:", "(Translated", "(Translation"]:
        if cleaned.startswith(prefix):
            # remove up to first colon or closing parenthesis
            # simple heuristic:
            cleaned = cleaned.split(":", 1)[-1].strip()
            cleaned = cleaned.lstrip(")") if cleaned.startswith(")") else cleaned
            cleaned = cleaned.strip()

    return {"translation": cleaned}

# ------------------------------------------------
# DOCUMENT SUMMARIZATION ENDPOINT
# ------------------------------------------------
@app.post("/summarize")
async def summarize_document(req: dict):
    global DOCUMENT_MEMORY

    summary_type = req.get("type", "short")

    if not DOCUMENT_MEMORY:
        return {"summary": "No document uploaded yet."}

    prompt = f"""
You are LawEase, an AI legal assistant.

Summarize the following legal document in a **{summary_type}** manner.

Rules:
- Use headings
- Bullet points
- Clear legal language
- No personal advice
- Only summarize from the document

Document:
{DOCUMENT_MEMORY}

Provide the summary below:
"""

    result = generate_with_ollama_http(prompt)

    if not result:
        return {"summary": "[LLM unavailable] Could not contact Ollama."}

    return {"summary": result.strip()}



# ------------------------------------------------
# CHAT ENDPOINT (legal filtered + document aware)
# ------------------------------------------------
@app.post("/chat")
async def chat_handler(req: ChatRequest):
    user_prompt_raw = req.prompt.strip()
    user_prompt = user_prompt_raw.lower()

    # -----------------------------------------------------------
    # 1️⃣ Strong Greeting Detection
    # -----------------------------------------------------------
    greeting_keywords = [
        "hi","hii", "hello", "hey", "good morning", "good evening",
        "good afternoon", "gm", "ge", "ga", "namaste", "vanakkam"
    ]

    if user_prompt_raw.lower() in greeting_keywords:
        return {
            "response": "Hello! I am LawEase — your AI legal assistant. How can I help you today?"
        }


    # -----------------------------------------------------------
    # 2️⃣ Document Follow-up Question Detection
    # If document exists & user asks questions about summary/content,
    # allow RESPONDING even if it's NOT a legal keyword.
    # -----------------------------------------------------------
    followup_keywords = [
        "point", "clause", "explain", "meaning", "interpret",
        "summary", "more about", "what is", "who is", "why", "how",
        "section", "para", "paragraph", "line", "details", "term"
    ]

    is_doc_followup = any(k in user_prompt for k in followup_keywords)

    # -----------------------------------------------------------
    # 3️⃣ Non-legal message handling — BUT NOT follow-up questions
    # -----------------------------------------------------------
    is_legal = is_legal_query(user_prompt)
    is_scenario = is_scenario_query(user_prompt)

    if not (is_legal or is_scenario ):
        return {
        "response": (
            "I can assist only with legal questions or real-life legal situations. Please ask a law-related query. "
        )
    }



    # -----------------------------------------------------------
    # 4️⃣ Build Context-aware Legal Prompt
    # -----------------------------------------------------------
    persona = (
    "You are LawEase, an AI legal assistant specialized in Indian law.\n\n"
    "You must:\n"
    "- Answer legal questions\n"
    "- Analyze real-life situations described by users (scenario-based queries)\n"
    "- Identify relevant IPC sections ONLY when clearly applicable\n"
    "- Explain why the law applies in simple terms\n"
    "- Suggest practical next steps (police, complaint, legal notice)\n"
    "- Respond empathetically in sensitive cases\n\n"
    "Rules:\n"
    "- Do NOT hallucinate IPC sections\n"
    "- If unsure, clearly say 'This may apply depending on facts'\n"
    "- Do NOT give final legal advice\n"
    "- Use headings and bullet points\n"
    "- End with a short summary\n\n"
)



    doc_context = (
        f"\n\nHere is the user's uploaded document summary/context:\n{DOCUMENT_MEMORY}\n"
        if DOCUMENT_MEMORY else ""
    )

    final_prompt = (
    f"{persona}"
    f"{doc_context}\n"
    f"User question: {user_prompt_raw}\n\n"
    "If this is a real-life situation, respond in this format:\n"
    "1. Issue Summary\n"
    "2. Applicable Laws (if any)\n"
    "3. What You Can Do Next\n"
    "4. Important Notes\n\n"
    "Answer clearly and politely:\n"
)


    # -----------------------------------------------------------
    # 5️⃣ Query LLM (Ollama)
    # -----------------------------------------------------------
    result = generate_with_ollama_http(final_prompt)

    if not result:
        return {"response": "[LLM unavailable] Could not contact Ollama."}

    return {"response": result.strip()}

# ------------------------------------------------
# TRANSLATION ENDPOINT
# ------------------------------------------------




# ------------------------------------------------
# ROOT
# ------------------------------------------------
@app.get("/")
async def root():
    return {"status": "LawEase backend running"}
