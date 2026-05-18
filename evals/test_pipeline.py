from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from src.agents.graph import run

load_dotenv()

test_cases = [
    {
        "question": "What is multi-head attention?",
        "ground_truth": "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions using multiple parallel attention heads."
    },
    {
        "question": "How many attention heads does the transformer use?",
        "ground_truth": "The transformer uses 8 parallel attention heads."
    },
    {
        "question": "What is the role of positional encoding?",
        "ground_truth": "Positional encoding injects information about the position of tokens in the sequence using sine and cosine functions of different frequencies."
    },
]

print("Running pipeline on test cases...\n")
results = []
for tc in test_cases:
    result = run(tc["question"])
    results.append({
        "question": tc["question"],
        "answer": result["answer"],
        "contexts": [doc.page_content for doc in result["chunks"]],
        "ground_truth": tc["ground_truth"]
    })
    print(f"✓ Done: {tc['question']}\n")

dataset = Dataset.from_list(results)

groq_llm = LangchainLLMWrapper(ChatGroq(model="llama-3.3-70b-versatile"))
local_embeddings = LangchainEmbeddingsWrapper(
    HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
)

faithfulness.llm = groq_llm
answer_relevancy.llm = groq_llm
answer_relevancy.embeddings = local_embeddings
context_recall.llm = groq_llm

print("\nRunning RAGAS evaluation...\n")
scores = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy, context_recall],
)

print("\n" + "="*50)
print("EVAL RESULTS:")
print("="*50)
df = scores.to_pandas()
print(df[["user_input", "faithfulness", "answer_relevancy", "context_recall"]])
print("\nMean scores:")
print(df[["faithfulness", "answer_relevancy", "context_recall"]].mean())