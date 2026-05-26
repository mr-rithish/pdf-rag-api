from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import shutil, os, uuid
from rag import load_pdfs, build_index, ask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# each user gets their own session
sessions = {}  # { session_id: { index, chunks, chunk_sources, chat_history } }

# ---- Create Session ----
@app.get("/session")
def create_session():
    session_id = str(uuid.uuid4())  # random unique ID like "a1b2-c3d4-..."
    sessions[session_id] = {
        "chunks": None,
        "chunk_sources": None,
        "index": None,
        "chat_history": []
    }
    return {"session_id": session_id}

# ---- Upload PDFs ----
@app.post("/upload")
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    session_id: str = Query(...)
):
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="Invalid session. Refresh the page.")

    os.makedirs(f"uploads/{session_id}", exist_ok=True)
    pdf_paths = []

    for file in files:
        path = f"uploads/{session_id}/{file.filename}"
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        pdf_paths.append(path)

    chunks, chunk_sources = load_pdfs(pdf_paths)
    index = build_index(chunks)

    # store under this user's session
    sessions[session_id]["chunks"] = chunks
    sessions[session_id]["chunk_sources"] = chunk_sources
    sessions[session_id]["index"] = index
    sessions[session_id]["chat_history"] = []  # reset chat on new upload

    return {"message": f"Indexed {len(chunks)} chunks from {len(files)} file(s)"}

# ---- Ask Question ----
class QuestionRequest(BaseModel):
    question: str
    session_id: str

@app.post("/ask")
async def ask_question(req: QuestionRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=400, detail="Invalid session. Refresh the page.")

    session = sessions[req.session_id]

    if session["index"] is None:
        raise HTTPException(status_code=400, detail="No PDFs uploaded yet.")

    answer, sources = ask(
        req.question,
        session["index"],
        session["chunks"],
        session["chunk_sources"],
        session["chat_history"]
    )

    session["chat_history"].append({"role": "user", "content": req.question})
    session["chat_history"].append({"role": "assistant", "content": answer})

    return {"answer": answer, "sources": sources}

# ---- Clear Session ----
@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        # cleanup uploaded files
        upload_dir = f"uploads/{session_id}"
        if os.path.exists(upload_dir):
            shutil.rmtree(upload_dir)
    return {"message": "Session cleared"}

@app.get("/")
def root():
    return {"status": "RAG backend running"}