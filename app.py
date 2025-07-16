from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ingestion import blob_upload, parse, chunk
from backend import embed, search
import os

app = FastAPI(title="Azure RAG (Single File FastAPI)")

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import hashlib


indexed_docs = {}  # in-memory tracking

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()

    if file_hash in indexed_docs:
        return {"status": "success", "message": "Already indexed."}

    # Proceed with blob upload, parsing, chunking, embedding, indexing
    # ...
    indexed_docs[file_hash] = True
    return {"status": "success", "message": "Indexed successfully."}

# ------------------------------
# 💬 Ask a Question Route
# ------------------------------
class Query(BaseModel):
    question: str

@app.post("/ask/")
def ask_question(q: Query):
    try:
        answer = search.search_query(q.question)
        return {"status": "success", "answer": answer}
    except Exception as e:
        return {"status": "error", "message": str(e)}
