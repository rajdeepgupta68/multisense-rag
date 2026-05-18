from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing import TypedDict

load_dotenv()

# Test 1: Groq LLM
llm = ChatGroq(model="llama-3.1-70b-versatile")
response = llm.invoke("Say hello in one sentence.")
print("✓ Groq works:", response.content)

# Test 2: LangGraph
class State(TypedDict):
    message: str

def hello_node(state: State):
    return {"message": "LangGraph works!"}

graph = StateGraph(State)
graph.add_node("hello", hello_node)
graph.set_entry_point("hello")
graph.add_edge("hello", END)
app = graph.compile()

result = app.invoke({"message": ""})
print("✓ LangGraph works:", result["message"])