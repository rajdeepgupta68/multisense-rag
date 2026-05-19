import whisper
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from src.ingestion.pipeline import LocalEmbeddings

def transcribe_audio(audio_path: str) -> str:
    print(f"Transcribing {audio_path}...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    print(f"  → Transcription complete ({len(result['text'])} characters)")
    return result["text"]

def ingest_audio(audio_path: str, collection_name: str = "multisense"):
    transcript = transcribe_audio(audio_path)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    docs = [Document(
        page_content=transcript,
        metadata={"source": audio_path, "type": "audio"}
    )]
    chunks = splitter.split_documents(docs)
    print(f"  → {len(chunks)} chunks created from transcript")

    embeddings = LocalEmbeddings()
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory="./chroma_db"
    )
    print(f"  → Stored in chroma_db/")
    return transcript