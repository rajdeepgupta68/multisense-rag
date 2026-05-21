from dotenv import load_dotenv
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
from src.ingestion.pipeline import LocalEmbeddings

load_dotenv()

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

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
    
    # fetch more candidates than needed
    candidates = vectorstore.similarity_search(query, k=k*3)
    
    # rerank candidates using cross-encoder
    pairs = [(query, doc.page_content) for doc in candidates]
    scores = reranker.predict(pairs)
    
    # sort by score and keep top k
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)
    results = [doc for _, doc in ranked[:k]]
    
    print(f"\nQuery: {query}")
    print(f"Top {k} chunks after reranking:\n")
    for i, doc in enumerate(results):
        print(f"--- Chunk {i+1} ---")
        print(doc.page_content[:300])
        print()
    
    return results

if __name__ == "__main__":
    retrieve("What is attention mechanism?")