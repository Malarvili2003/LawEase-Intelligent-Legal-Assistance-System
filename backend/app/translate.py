# translate.py
from llm import generate_with_ollama_http  # make sure llm.py is in same folder or on PYTHONPATH

def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """
    Translate single text string from from_lang to to_lang using llm.generate_with_ollama_http.
    Returns translated text (string). Raises ValueError for empty text.
    """
    text = (text or "").strip()
    from_lang = (from_lang or "auto").strip()
    to_lang = (to_lang or "English").strip()

    if not text:
        raise ValueError("No text to translate")

    prompt = (
        f"You are a professional translator. Convert the following text from {from_lang} to {to_lang}.\n\n"
        f"Instructions:\n"
        f"- Return only the translated text.\n"
        f"- No explanations, no labels, no repetition.\n\n"
        f"Text:\n{text}"
    )

    result = generate_with_ollama_http(prompt)
    if result is None:
        # Keep return type consistent (string)
        return "[LLM unavailable] Could not contact Ollama."

    return result.strip()
