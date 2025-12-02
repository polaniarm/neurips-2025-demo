#!/usr/bin/env python3
"""
Whisper Web Transcription Service - Demo Version
Model: openai/whisper-large-v3-turbo

To install dependencies:
    pip install fastapi uvicorn transformers torch python-multipart

To run (direct access):
    uvicorn server:app --host 0.0.0.0 --port 8080

To run (behind nginx):
    uvicorn server:app --host 127.0.0.1 --port 8000

The server will download the Whisper model on first run (~1.5GB).
Access at http://localhost:8080 (direct) or via nginx proxy
"""

import os
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import torch
from transformers import pipeline


# Initialize FastAPI
app = FastAPI(title="Whisper Transcription Demo")

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model variable
asr_pipeline = None
MODEL_ID = "openai/whisper-large-v3-turbo"


@app.on_event("startup")
async def load_model():
    """Load Whisper model at startup"""
    global asr_pipeline
    print(f"🚀 Loading Whisper model: {MODEL_ID}")
    print("This will take a minute on first run...")

    try:
        # Simple pipeline initialization
        asr_pipeline = pipeline(
            "automatic-speech-recognition",
            model=MODEL_ID,
            device="cpu",
            torch_dtype=torch.float32,
        )
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML frontend directly from the root endpoint"""
    html_path = Path("index.html")
    if html_path.exists():
        return html_path.read_text()
    return """
    <html>
        <body>
            <h1>Whisper Transcription API</h1>
            <p>Model: openai/whisper-large-v3-turbo</p>
            <p>Endpoints:</p>
            <ul>
                <li>POST /transcribe - Upload audio for transcription</li>
                <li>GET /health - Check server status</li>
            </ul>
            <p>Place index.html in the same directory to use the web interface.</p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Quick health check"""
    return {
        "status": "ready" if asr_pipeline else "loading",
        "model": MODEL_ID,
        "device": "cpu"
    }


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe uploaded audio file.
    Accepts WebM/Opus from browser or any audio format.
    """
    if not asr_pipeline:
        raise HTTPException(status_code=503, detail="Model still loading...")

    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temp file with original extension
        suffix = Path(file.filename).suffix if file.filename else ".webm"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        content = await file.read()
        temp_file.write(content)
        temp_file.close()

        print(f"📎 Processing: {file.filename} ({len(content):,} bytes)")

        # Transcribe
        start_time = time.time()
        result = asr_pipeline(
            temp_file.name,
            return_timestamps=True,
            generate_kwargs={"language": "en"}
        )
        elapsed = time.time() - start_time

        # Format response
        text = result.get("text", "").strip()

        # Extract word-level timestamps if available
        timestamps = []
        if "chunks" in result:
            for chunk in result["chunks"]:
                timestamps.append({
                    "start": round(chunk["timestamp"][0], 2) if chunk.get("timestamp") else 0,
                    "end": round(chunk["timestamp"][1], 2) if chunk.get("timestamp") else 0,
                    "text": chunk.get("text", "").strip()
                })

        print(f"✅ Transcribed in {elapsed:.2f}s: {text[:100]}...")

        return {
            "text": text,
            "timestamps": timestamps,
            "elapsed_seconds": round(elapsed, 3)
        }

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


if __name__ == "__main__":
    import uvicorn
    import os
    # Use PORT environment variable if set, otherwise default to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)