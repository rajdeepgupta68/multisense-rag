from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.retrieval.retriever import retrieve

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

prompt = ChatPromptTemplate.from_template("""
You are a helpful research assistant. Answer the user's question 
using ONLY the context provided below. If the answer isn't in 
the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:
""")

def answer(question: str):
    chunks = retrieve(question, k=4)
    context = "\n\n".join([doc.page_content for doc in chunks])
    
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "question": question
    })
    
    print("\n" + "="*50)
    print("ANSWER:")
    print("="*50)
    print(response.content)
    return response.content

if __name__ == "__main__":
    answer("What is attention mechanism and how does it work?")