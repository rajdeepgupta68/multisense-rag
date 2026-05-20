import gradio as gr
import requests
import threading
import uvicorn
from src.api.main import app as fastapi_app

API_URL = "http://0.0.0.0:8000"

def run_api():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

def query(question):
    if not question.strip():
        return "[ ERROR ] INPUT REQUIRED"
    response = requests.post(f"{API_URL}/query", json={"question": question})
    if response.status_code == 200:
        data = response.json()
        return f"""[ DECRYPTION COMPLETE ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{data['answer']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ INTENT CLASSIFIED ] : {data['intent'].upper()}
[ SOURCES ACCESSED  ] : {data['num_chunks']} nodes
[ STATUS            ] : TRANSMISSION COMPLETE"""
    elif response.status_code == 429:
        return "[ WARNING ] RATE LIMIT REACHED — RETRY IN 60s"
    return f"[ ERROR ] {response.text}"

def ingest(file):
    if file is None:
        return "[ ERROR ] NO FILE DETECTED"
    with open(file.name, "rb") as f:
        response = requests.post(f"{API_URL}/ingest", files={"file": f})
    if response.status_code == 200:
        return "[ SUCCESS ] DATA INJECTED INTO NEURAL NETWORK"
    return f"[ ERROR ] {response.text}"

def ingest_audio_gradio(file):
    if file is None:
        return "[ ERROR ] NO AUDIO SIGNAL DETECTED"
    with open(file.name, "rb") as f:
        response = requests.post(f"{API_URL}/ingest/audio", files={"file": f})
    if response.status_code == 200:
        data = response.json()
        return f"[ SUCCESS ] AUDIO INTERCEPTED & INDEXED\n\n[ TRANSCRIPT PREVIEW ]\n{data['transcript_preview']}"
    return f"[ ERROR ] {response.text}"

def clear_db():
    response = requests.post(f"{API_URL}/clear")
    if response.status_code == 200:
        return "[ SUCCESS ] NEURAL NETWORK WIPED"
    return f"[ ERROR ] {response.text}"

ctos_css = """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

:root {
    --cyan: #00d4ff;
    --green: #39ff14;
    --orange: #ff6b00;
    --bg: #04080f;
    --bg2: #080d18;
    --bg3: #0d1525;
    --border: #00d4ff33;
    --text: #c8dff0;
    --dim: #4a6a8a;
}

* { font-family: 'Share Tech Mono', monospace !important; }

body, .gradio-container {
    background: var(--bg) !important;
    color: var(--text) !important;
}

.gradio-container {
    background-image: 
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
}

/* Scanline overlay */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.15) 2px,
        rgba(0,0,0,0.15) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* Header */
.prose h1, h1 {
    font-family: 'Orbitron', monospace !important;
    color: var(--cyan) !important;
    text-shadow: 0 0 20px rgba(0,212,255,0.8), 0 0 40px rgba(0,212,255,0.4) !important;
    letter-spacing: 4px !important;
    animation: flicker 4s infinite !important;
}

@keyframes flicker {
    0%, 95%, 100% { opacity: 1; }
    96% { opacity: 0.7; }
    97% { opacity: 1; }
    98% { opacity: 0.5; }
    99% { opacity: 1; }
}

/* Tabs */
.tab-nav button {
    background: var(--bg2) !important;
    color: var(--dim) !important;
    border: 1px solid var(--border) !important;
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 2px !important;
    font-size: 11px !important;
    transition: all 0.2s !important;
}

.tab-nav button.selected {
    background: rgba(0,212,255,0.1) !important;
    color: var(--cyan) !important;
    border-color: var(--cyan) !important;
    box-shadow: 0 0 15px rgba(0,212,255,0.3) !important;
}

.tab-nav button:hover {
    color: var(--cyan) !important;
    border-color: var(--cyan) !important;
}

/* Input boxes */
textarea, input[type="text"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--cyan) !important;
    font-family: 'Share Tech Mono', monospace !important;
    caret-color: var(--cyan) !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}

textarea:focus, input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 15px rgba(0,212,255,0.2), inset 0 0 10px rgba(0,212,255,0.05) !important;
    outline: none !important;
}

/* Buttons */
button.primary {
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 3px !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
    position: relative !important;
    overflow: hidden !important;
}

button.primary:hover {
    background: rgba(0,212,255,0.1) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.4) !important;
    transform: translateY(-1px) !important;
}

button.primary::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: linear-gradient(transparent, rgba(0,212,255,0.1), transparent);
    transform: rotate(45deg) translateX(-100%);
    transition: transform 0.4s;
}

button.primary:hover::after {
    transform: rotate(45deg) translateX(100%);
}

/* Secondary buttons */
button.secondary {
    background: transparent !important;
    border: 1px solid var(--orange) !important;
    color: var(--orange) !important;
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 2px !important;
    font-size: 10px !important;
}

button.secondary:hover {
    background: rgba(255,107,0,0.1) !important;
    box-shadow: 0 0 15px rgba(255,107,0,0.3) !important;
}

/* Output/markdown boxes */
.prose, .output-markdown, .output-class {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--green) !important;
    padding: 16px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}

/* Labels */
label span, .label-wrap span {
    color: var(--dim) !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
}

/* File upload */
.upload-button {
    border: 1px dashed var(--border) !important;
    background: var(--bg2) !important;
    color: var(--dim) !important;
}

.upload-button:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
}

/* Block containers */
.block {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 0 !important;
}

/* Status bar animation */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--green);
    border-radius: 50%;
    animation: pulse 2s infinite;
    box-shadow: 0 0 8px var(--green);
}
"""

with gr.Blocks(css=ctos_css, title="ctOS // MultiSense RAG") as demo:
    
    gr.HTML("""
    <div style="
        border-bottom: 1px solid rgba(0,212,255,0.3);
        padding: 20px 0 16px;
        margin-bottom: 8px;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-family:'Orbitron',monospace; font-size:22px; color:#00d4ff; 
                            text-shadow: 0 0 20px rgba(0,212,255,0.8); letter-spacing:6px; font-weight:900;">
                    ctOS // MULTISENSE RAG
                </div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:11px; 
                            color:#4a6a8a; letter-spacing:3px; margin-top:4px;">
                    NEURAL DOCUMENT INTELLIGENCE SYSTEM v2.0
                </div>
            </div>
            <div style="text-align:right; font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a6a8a;">
                <div style="color:#39ff14;">
                    <span style="display:inline-block; width:8px; height:8px; background:#39ff14; 
                                 border-radius:50%; margin-right:6px; 
                                 box-shadow: 0 0 8px #39ff14;"></span>
                    CONNECTION : SECURE
                </div>
                <div style="margin-top:4px;">ENCRYPTION : AES-256</div>
                <div style="margin-top:4px;">AGENTS : ACTIVE</div>
            </div>
        </div>
    </div>
    """)

    with gr.Tabs():
        with gr.Tab("[ INTERROGATE ]"):
            gr.HTML('<div style="font-family:\'Share Tech Mono\',monospace; font-size:11px; color:#4a6a8a; letter-spacing:2px; margin-bottom:12px;">// QUERY THE NEURAL NETWORK</div>')
            question = gr.Textbox(
                label="INPUT QUERY",
                placeholder="> ENTER SEARCH PARAMETERS...",
                lines=3
            )
            query_btn = gr.Button("[ EXECUTE QUERY ]", variant="primary")
            answer = gr.Markdown(label="DECRYPTED OUTPUT")
            query_btn.click(query, inputs=question, outputs=answer)

        with gr.Tab("[ INJECT DATA ]"):
            gr.HTML('<div style="font-family:\'Share Tech Mono\',monospace; font-size:11px; color:#4a6a8a; letter-spacing:2px; margin-bottom:12px;">// UPLOAD PDF TO NEURAL NETWORK</div>')
            pdf_input = gr.File(label="SELECT TARGET FILE", file_types=[".pdf"])
            ingest_btn = gr.Button("[ INJECT INTO NETWORK ]", variant="primary")
            ingest_status = gr.Textbox(label="SYSTEM RESPONSE")
            ingest_btn.click(ingest, inputs=pdf_input, outputs=ingest_status)

        with gr.Tab("[ INTERCEPT AUDIO ]"):
            gr.HTML('<div style="font-family:\'Share Tech Mono\',monospace; font-size:11px; color:#4a6a8a; letter-spacing:2px; margin-bottom:12px;">// INTERCEPT & TRANSCRIBE AUDIO SIGNAL</div>')
            audio_input = gr.File(label="SELECT AUDIO SIGNAL", file_types=[".mp3", ".wav", ".m4a", ".mp4"])
            audio_btn = gr.Button("[ INTERCEPT SIGNAL ]", variant="primary")
            audio_status = gr.Textbox(label="SYSTEM RESPONSE", lines=4)
            audio_btn.click(ingest_audio_gradio, inputs=audio_input, outputs=audio_status)

        with gr.Tab("[ SYSTEM ]"):
            gr.HTML('<div style="font-family:\'Share Tech Mono\',monospace; font-size:11px; color:#4a6a8a; letter-spacing:2px; margin-bottom:12px;">// SYSTEM MAINTENANCE</div>')
            clear_btn = gr.Button("[ WIPE NEURAL NETWORK ]", variant="secondary")
            clear_status = gr.Textbox(label="SYSTEM RESPONSE")
            clear_btn.click(clear_db, outputs=clear_status)

    gr.HTML("""
    <div style="
        border-top: 1px solid rgba(0,212,255,0.15);
        margin-top: 16px;
        padding-top: 12px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 10px;
        color: #2a4a6a;
        display: flex;
        justify-content: space-between;
        letter-spacing: 2px;
    ">
        <span>ctOS MULTISENSE RAG // MULTIMODAL DOCUMENT INTELLIGENCE</span>
        <span>BUILT WITH LANGGRAPH + GROQ + WHISPER</span>
    </div>
    """)

demo.launch(server_name="0.0.0.0", server_port=7860)