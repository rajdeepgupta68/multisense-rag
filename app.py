import gradio as gr
import requests

API_URL = "http://0.0.0.0:8000"

def query(question):
    if not question.strip():
        return "Please enter a question."
    response = requests.post(f"{API_URL}/query", json={"question": question})
    if response.status_code == 200:
        data = response.json()
        return f"""**Answer:**
{data['answer']}

---
**Intent detected:** {data['intent']}
**Chunks retrieved:** {data['num_chunks']}"""
    return f"Error: {response.text}"

def ingest(file):
    if file is None:
        return "Please upload a PDF."
    with open(file.name, "rb") as f:
        response = requests.post(f"{API_URL}/ingest", files={"file": f})
    if response.status_code == 200:
        return "Document ingested successfully!"
    return f"Error: {response.text}"

def ingest_audio_gradio(file):
    if file is None:
        return "Please upload an audio file."
    with open(file.name, "rb") as f:
        response = requests.post(f"{API_URL}/ingest/audio", files={"file": f})
    if response.status_code == 200:
        data = response.json()
        return f" Transcribed and ingested!\n\nPreview: {data['transcript_preview']}"
    return f"Error: {response.text}"

with gr.Blocks(title="MultiSense RAG") as demo:
    gr.Markdown("# 🧠 MultiSense RAG\nMultimodal document intelligence with multi-agent orchestration.")
    
    with gr.Tab("Query"):
        question = gr.Textbox(label="Ask a question", placeholder="How does multi-head attention work?")
        answer = gr.Markdown(label="Answer")
        query_btn = gr.Button("Ask", variant="primary")
        query_btn.click(query, inputs=question, outputs=answer)

    with gr.Tab("Upload Document"):
        pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])
        ingest_status = gr.Textbox(label="Status")
        ingest_btn = gr.Button("Ingest", variant="primary")
        ingest_btn.click(ingest, inputs=pdf_input, outputs=ingest_status)

    with gr.Tab("Upload Audio"):
        audio_input = gr.File(label="Upload audio file", file_types=[".mp3", ".wav", ".m4a", ".mp4"])
        audio_status = gr.Textbox(label="Transcript preview")
        audio_btn = gr.Button("Transcribe & Ingest", variant="primary")
        audio_btn.click(ingest_audio_gradio, inputs=audio_input, outputs=audio_status)


import uvicorn
import threading
from src.api.main import app as fastapi_app

def run_api():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

API_URL = "http://0.0.0.0:8000"
demo.launch(server_name="0.0.0.0", server_port=7860)