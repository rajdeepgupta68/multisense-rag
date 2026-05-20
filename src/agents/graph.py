from dotenv import load_dotenv
from typing import TypedDict, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from src.retrieval.retriever import retrieve

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

# --- Shared state passed between all agents ---
class RAGState(TypedDict):
    question: str
    intent: str
    chunks: List[Document]
    answer: str
    critique: str
    retry_count: int

# --- Agent 1: Router - classifies intent ---
def router_agent(state: RAGState) -> RAGState:
    prompt = ChatPromptTemplate.from_template("""
Classify this question into one of these intents:
- factual: asking for a specific fact
- summary: asking for an overview or summary  
- comparison: asking to compare two things

Question: {question}
Reply with just one word: factual, summary, or comparison.
""")
    chain = prompt | llm
    intent = chain.invoke({"question": state["question"]}).content.strip().lower()
    print(f"[Router] Intent: {intent}")
    return {**state, "intent": intent}

# --- Agent 2: Retrieval - fetches relevant chunks ---
def retrieval_agent(state: RAGState) -> RAGState:
    k = 6 if state["intent"] == "summary" else 4
    chunks = retrieve(state["question"], k=k)
    print(f"[Retrieval] Fetched {len(chunks)} chunks")
    return {**state, "chunks": chunks}

# --- Agent 3: Synthesis - generates answer from chunks ---
def synthesis_agent(state: RAGState) -> RAGState:
    context = "\n\n".join([doc.page_content for doc in state["chunks"]])
    prompt = ChatPromptTemplate.from_template("""
You are a research assistant. Answer using ONLY the context below.
If the answer isn't in the context, say "I don't have enough information."

Context:
{context}

Question: {question}
Answer:
""")
    chain = prompt | llm
    answer = chain.invoke({
        "context": context,
        "question": state["question"]
    }).content
    print(f"[Synthesis] Answer generated")
    return {**state, "answer": answer}

# --- Agent 4: Critique - checks answer quality ---
def critique_agent(state: RAGState) -> RAGState:
    prompt = ChatPromptTemplate.from_template("""
Evaluate this answer. Reply with just one word:
- GOOD: answer has any relevant content about the question
- RETRY: answer explicitly says "I don't have enough information"

Question: {question}
Answer: {answer}
Verdict:
""")
    chain = prompt | llm
    critique = chain.invoke({
        "question": state["question"],
        "answer": state["answer"]
    }).content.strip().upper()
    print(f"[Critique] Verdict: {critique}")
    return {**state, "critique": critique}

# --- Routing logic after critique ---
def should_retry(state: RAGState) -> str:
    if state["critique"] == "RETRY" and state["retry_count"] < 2:
        return "retry"
    return "done"

def increment_retry(state: RAGState) -> RAGState:
    print(f"[Retry] Attempt {state['retry_count'] + 1}")
    return {**state, "retry_count": state["retry_count"] + 1}

# --- Build the graph ---
graph = StateGraph(RAGState)

graph.add_node("router", router_agent)
graph.add_node("retrieval", retrieval_agent)
graph.add_node("synthesis", synthesis_agent)
graph.add_node("critique", critique_agent)
graph.add_node("retry", increment_retry)

graph.set_entry_point("router")
graph.add_edge("router", "retrieval")
graph.add_edge("retrieval", "synthesis")
graph.add_edge("synthesis", "critique")
graph.add_conditional_edges("critique", should_retry, {
    "retry": "retrieval",
    "done": END
})
graph.add_edge("retry", "retrieval")

app = graph.compile()

def run(question: str):
    print(f"\n{'='*50}")
    print(f"QUESTION: {question}")
    print(f"{'='*50}")
    result = app.invoke({
        "question": question,
        "intent": "",
        "chunks": [],
        "answer": "",
        "critique": "",
        "retry_count": 0
    })
    print(f"\nFINAL ANSWER:\n{result['answer']}")
    return result

if __name__ == "__main__":
    run("What does the podcast say about synchronicities?")