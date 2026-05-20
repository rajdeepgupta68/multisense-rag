from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
import os

from src.ingestion.pipeline import ingest_pdf
from src.agents.graph import run

load_dotenv()

app = FastAPI(
    title="MultiSense RAG API",
    description="Multimodal document intelligence — ingest PDFs, query with LLMs",
    version="1.0.0"
)

# --- Request/response models ---
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    intent: str
    num_chunks: int

# --- Health check ---
@app.get("/health")
def health():
    return {"status": "ok", "service": "multisense-rag"}

# --- Ingest a PDF ---
@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    tmp_path = f"tmp_{file.filename}"
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        ingest_pdf(tmp_path)
        return {"status": "success", "filename": file.filename}
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

from src.ingestion.audio import ingest_audio

@app.post("/ingest/audio")
async def ingest_audio_file(file: UploadFile = File(...)):
    allowed = [".mp3", ".wav", ".m4a", ".mp4"]
    if not any(file.filename.endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="Supported formats: mp3, wav, m4a, mp4")
    
    tmp_path = f"tmp_{file.filename}"
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        transcript = ingest_audio(tmp_path)
        return {
            "status": "success",
            "filename": file.filename,
            "transcript_preview": transcript[:200] + "..."
        }
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/clear")
def clear_vectorstore():
    import shutil
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")
        os.makedirs("./chroma_db")
    return {"status": "cleared"}
            
# --- Query the pipeline ---
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    try:
        result = run(request.question)
        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            intent=result["intent"],
            num_chunks=len(result["chunks"])
        )
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            raise HTTPException(
                status_code=429,
                detail="LLM rate limit reached. Please try again in a few minutes."
            )
        raise HTTPException(status_code=500, detail=str(e))
    
