import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()

model = SentenceTransformer('all-MiniLM-L6-v2')
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def load_pdfs(pdf_paths):
    all_chunks = []
    chunk_sources = []
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if not text:
                continue
            chunks = chunk_text(text)
            all_chunks.extend(chunks)
            for _ in chunks:
                chunk_sources.append({
                    "file": os.path.basename(pdf_path),
                    "page": page_num + 1
                })
    return all_chunks, chunk_sources

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_size])
        start += chunk_size - overlap
    return chunks

def build_index(chunks):
    embeddings = model.encode(chunks)
    embeddings = np.array(embeddings).astype('float32')
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index

def search(question, index, chunks, chunk_sources, top_k=3):
    question_vector = model.encode([question]).astype('float32')
    distances, indices = index.search(question_vector, top_k)
    return [{"text": chunks[i], "source": chunk_sources[i]} for i in indices[0]]

def ask(question, index, chunks, chunk_sources, chat_history):
    relevant = search(question, index, chunks, chunk_sources)
    context = "\n\n".join([r["text"] for r in relevant])

    messages = [{"role": "system", "content": "Answer only from the provided context. If answer isn't in context, say I don't know."}]
    for msg in chat_history:
        messages.append(msg)
    messages.append({"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )
    answer = response.choices[0].message.content
    sources = [f"{r['source']['file']} — Page {r['source']['page']}" for r in relevant]
    return answer, sources