# DocuAsk — AI Document Q&A

> Upload PDFs. Ask questions. Get answers with sources.

**Live Demo:** [beautiful-crumble-2731b5.netlify.app](https://beautiful-crumble-2731b5.netlify.app)

---

## What is this?

DocuAsk is a full-stack RAG (Retrieval-Augmented Generation) application that lets you upload PDF documents and ask natural language questions about them. Instead of keyword search, it understands the *meaning* of your question and retrieves the most relevant content from your documents.

---

## How it works

```
PDF Upload
    ↓
Extract text → Split into chunks → Embed with sentence-transformers
    ↓
Store in FAISS vector index
    ↓
User asks a question
    ↓
Embed question → Search FAISS → Retrieve top 3 relevant chunks
    ↓
Prompt = chunks + question → Groq LLM (Llama 3.3 70B)
    ↓
Answer with page-level source attribution 
```

---

## Features

- **Multi-PDF support** — upload and query across multiple documents simultaneously
- **Semantic search** — finds relevant content by meaning, not just keywords
- **Source attribution** — every answer shows exactly which file and page it came from
- **Per-user session isolation** — multiple users can use the app simultaneously without interfering with each other
- **Chat history** — follow-up questions work naturally within a session
- **Clean minimal UI** — no clutter, just upload and ask

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | FastAPI (Python) |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Vector Search | FAISS (Facebook AI Similarity Search) |
| LLM | Llama 3.3 70B via Groq API |
| PDF Parsing | pypdf |
| Deployment — Frontend | Netlify |
| Deployment — Backend | HuggingFace Spaces (Docker) |

---

## Project Structure

```
rag-project/
│
├── frontend/
│   ├── index.html       — UI layout
│   ├── style.css        — styling
│   └── script.js        — fetch logic, session management
│
└── backend/
    ├── main.py          — FastAPI routes (/session, /upload, /ask)
    ├── rag.py           — RAG pipeline (chunking, embedding, FAISS, LLM)
    ├── requirements.txt
    └── Dockerfile
```

---

## Running Locally

### Prerequisites
- Python 3.10+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
pip install -r requirements.txt

# create .env file
echo "GROQ_API_KEY=your_key_here" > .env

uvicorn main:app --reload
# runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
python -m http.server 5500
# open http://localhost:5500
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/session` | Create a new user session |
| `POST` | `/upload?session_id={}` | Upload and index PDF files |
| `POST` | `/ask` | Ask a question, get answer + sources |
| `DELETE` | `/session/{id}` | Clear session and uploaded files |
| `GET` | `/` | Health check |

---


## What I Learned Building This

- Built the full RAG pipeline **from scratch in pure Python** before using any framework — understanding every step (embedding, FAISS indexing, similarity search, prompt construction)
- Understood why chunking strategy and overlap matter for retrieval quality
- Handled the "lost in the middle" problem by retrieving only top-k relevant chunks instead of stuffing the entire PDF into the prompt
- Designed per-user session isolation to handle concurrent users correctly
- Containerized a Python ML app with Docker and deployed on HuggingFace Spaces

---

## Author

**Rithish**

[GitHub](https://github.com/mr-rithish)
