# LawEase – Intelligent Legal Assistant System

LawEase is an AI-powered legal assistant designed to simplify legal research, document understanding, and query handling. It enables users to upload various legal documents, extract insights, summarize content, translate text, and get AI‑generated responses—all through a clean, user-friendly interface.

---

## 🚀 Features

* **AI Chat Assistant:** Ask legal queries using natural language and receive accurate, context-aware responses.
* **Document Upload & Parsing:** Supports PDF, DOCX, handwritten (future scope), and scanned documents.
* **Advanced Summarization:** Generates concise summaries for long legal documents.
* **Translation:** Multi-language translation support.
* **Keyword Extraction:** Identifies important legal terms automatically.
* **RAG (Retrieval Augmented Generation):** Ensures responses are grounded in uploaded documents for accuracy.
* **History Panel:** Saves chat history and document interactions for quick access.
* **Dynamic Theming:** Light/Dark theme toggle.
* **Export to PDF:** Download output summaries, responses, or analysis.
* **Mobile-ready UI (in roadmap).**

---

## 🛠️ Tech Stack

### **Frontend:**

* React.js
* TailwindCSS

### **Backend:**

* FastAPI
* Python
* pdfplumber, docx
* CORS Middleware

### **AI Model:**

* Ollama (Qwen2.5 1.5B model used locally)
* Custom RAG pipeline

---

## 🏗️ System Architecture

```
User → React Frontend → FastAPI Backend → RAG Pipeline → Ollama Model → Response
```

**Modules involved:**

1. **Frontend UI** – Upload documents, chat interface, history tracking
2. **Backend API** – File handling, text extraction, feature services
3. **RAG Layer** – Embeddings + similarity search
4. **LLM Inference** – Generates output based on context

---

## 📂 Folder Structure

```
lawease/
│
├── backend/
│   ├── main.py
│   ├── rag/
│   ├── utils/
│   ├── models/
│
├── frontend/
│   ├── src/
│   ├── components/
│   ├── pages/
│   ├── assets/
│
└── README.md
```

---

## ⚙️ Installation

### **Backend Setup**

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
url : npm run dev -- --host

```

---

## ▶️ How to Use

1. Launch both **frontend** and **backend** servers.
2. Open the browser → User Interface loads.
3. Upload a legal document or start chatting.
4. Choose from:

   * Summarize
   * Translate
   * Extract keywords
   * Ask legal questions
5. Export results as PDF if needed.


---

## 💡 Use Cases

* Students researching case laws
* Lawyers verifying legal points quickly
* Common users understanding legal notices
* Multilingual document analysis



---

## 👩‍💻 Author

**Malar**

For feedback or contributions, feel free to open an issue or PR.
