from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document

def extract_text_from_file(filename, content_bytes):
    lower = filename.lower()
    if lower.endswith('.pdf'):
        try:
            reader = PdfReader(BytesIO(content_bytes))
            texts = []
            for p in reader.pages:
                try:
                    texts.append(p.extract_text() or '')
                except Exception:
                    pass
            return '\n'.join(texts)
        except Exception as e:
            return f'[Error extracting PDF] {e}'
    if lower.endswith('.docx'):
        try:
            doc = Document(BytesIO(content_bytes))
            texts = [p.text for p in doc.paragraphs]
            return '\n'.join(texts)
        except Exception as e:
            return f'[Error extracting DOCX] {e}'
    try:
        return content_bytes.decode('utf-8', errors='ignore')[:100000]
    except:
        return '[Unsupported file type]'
