from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings
import os

load_dotenv()

# Wrapper so LangChain can use sentence-transformers
class LocalEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True).tolist()
    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()

def ingest_pdf(pdf_path: str, collection_name: str = "multisense"):
    print(f"Loading {pdf_path}...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    print(f"  → {len(docs)} pages loaded")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"  → {len(chunks)} chunks created")

    embeddings = LocalEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory="./chroma_db"
    )
    print(f"  → Stored in chroma_db/")
    return vectorstore

if __name__ == "__main__":
    ingest_pdf("test.pdf")