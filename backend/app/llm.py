import requests, subprocess, json
OLLAMA_HTTP = "http://127.0.0.1:11434/api"
OLLAMA_MODEL = 'qwen2.5:1.5b'

def generate_with_ollama_http(prompt: str):
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(
            f"{OLLAMA_HTTP}/generate",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        return None

    except Exception as e:
        print("Ollama error:", e)
        return None


def generate_with_ollama_cli(prompt: str):
    try:
        proc = subprocess.run(['ollama','generate', OLLAMA_MODEL], input=prompt, capture_output=True, text=True, timeout=90)
        if proc.returncode==0: return proc.stdout.strip()
        return None
    except Exception as e:
        print('Ollama CLI error', e); return None

def is_legal_query(text: str) -> bool:
    keywords = ['law','legal','contract','court','FIR','bail','divorce','custody','property','GST','tax','police','investigation','patent','trademark','copyright']
    t = text.lower()
    return any(k in t for k in keywords)

def generate(prompt: str) -> str:
    greetings = ['hi','hii','hello','hey','good morning','good evening']
    if prompt.lower().strip() in greetings:
        return "Hello! I'm LawEase — your legal assistant. How can I help you today?"
    if not is_legal_query(prompt):
        return "I can answer legal queries. Please ask me something related to law."
    persona = ("You are LawEase, an AI trained ONLY for legal information. Answer ONLY legal questions. If unclear ask for clarificaton. Do NOT give binding legal advice. Include a short summary at the end.")
    full = persona + "\n\nUser: " + prompt + "\n\nAssistant:"
    t = generate_with_ollama_http(full)
    if t: return t
    t = generate_with_ollama_cli(full)
    if t: return t
    return "[LLM unavailable] Could not contact Ollama."
