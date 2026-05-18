from dotenv import load_dotenv
from langchain_chroma import Chroma
from src.ingestion.pipeline import LocalEmbeddings

load_dotenv()

def load_vectorstore(collection_name: str = "multisense"):
    embeddings = LocalEmbeddings()
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )
    return vectorstore

def retrieve(query: str, k: int = 4):
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    print(f"\nQuery: {query}")
    print(f"Top {k} chunks retrieved:\n")
    for i, doc in enumerate(results):
        print(f"--- Chunk {i+1} ---")
        print(doc.page_content[:300])
        print()
    return results

if __name__ == "__main__":
    retrieve("What is attention mechanism?")