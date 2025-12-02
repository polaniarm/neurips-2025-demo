# Whisper ASR on ARM Demo

Web-based automatic speech recognition using OpenAI's Whisper model on ARM infrastructure.

## Overview

This demo shows Whisper Large v3 Turbo running on ARM CPUs using Hugging Face Transformers. It provides a browser interface for audio recording and transcription.

## Components

- **Backend**: FastAPI server with Whisper model
- **Frontend**: HTML/JavaScript interface with audio recording
- **Model**: openai/whisper-large-v3-turbo

## Requirements

- Python 3.8+
- 8GB RAM minimum
- Ubuntu 20.04 or later (for deployment)

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn transformers torch python-multipart
   ```

## Running Locally

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Access the interface at `http://localhost:8000`

## Deployment

For AWS EC2 deployment, see `DEPLOYMENT.md` for nginx and SSL configuration.

## Usage

1. Open the web interface
2. Click "Start Recording"
3. Speak into your microphone
4. Click "Stop & Transcribe"
5. View the transcription results

## Files

- `server.py` - FastAPI backend server
- `index.html` - Web interface
- `whisper-application.py` - Standalone CLI version
- `DEPLOYMENT.md` - Production deployment guide

## License

See LICENSE file for details.