# Armor: Financial Conversation Intelligence System

Armor is an AI-powered system designed to capture, transcribe, and structure informal, multilingual financial conversations. Often, critical financial decisions (such as loans, SIPs, or investments) discussed in Hinglish or regional languages go undocumented. Armor records these discussions, extracts financial entities, and generates a structured JSON intelligence report tracking commitments and pending decisions.

## Features

- **Multilingual Speech-to-Text**: Transcribes code-mixed inputs (e.g., Hinglish) using Whisper models.
- **Financial Topic Detection**: Filters out non-financial conversations to protect resources and privacy.
- **Entity Extraction**: Identifies and normalizes financial instruments, amounts, and timelines.
- **Structured Intelligence**: Uses LLMs to generate a concise summary of commitments, pending decisions, and a calculated risk score.
- **Dual-Execution Mode**: 
  - **Cloud Mode**: Fast processing using Groq API.
  - **Local Mode**: Secure, on-device processing using local models (Ollama).
- **Live Recording**: Capable of recording and analyzing live audio directly from the browser.

## Architecture & Technology Stack

The project operates on a decoupled architecture, separating the heavy machine-learning backend from the user interface.

**Backend (Python / FastAPI)**
- `FastAPI` / `Uvicorn`: Core REST API service.
- `faster-whisper` & `Groq Whisper API`: Speech recognition.
- `mDeBERTa`: Zero-shot classification for financial context detection.
- `GLiNER-Multi`: Named Entity Recognition (NER).
- `Ollama` (llama3.2:1b) & `Groq` (llama-3.3-70b): Summary and risk-score generation.
- `SQLite`: Persistent localized database.

**Frontend (React / Next.js)**
- `Next.js 15` (App Router): Web framework.
- `Tailwind CSS 4`: Styling and layout.
- `Framer Motion`: Layout animations.

## Team Axon
- Thejas 
- Ryan 
- Surya 
- Sanketh 

## Setup & Execution

You will need to run the backend and frontend simultaneously in two separate terminals.

### 1. Configuration
Create a `.env` file in the root directory and add your API Key for Cloud Mode:
```env
GROQ_API_KEY="your_api_key_here"
```

### 2. Start the Backend
From the root project directory `Axon-1`:
```bash
python api.py
```
*(The FastAPI service will start on `http://localhost:8000`)*

### 3. Start the Frontend
Open a new terminal and navigate to the `frontend` directory:
```bash
cd frontend
npm run dev
```
*(The React application will start on `http://localhost:3000`)*

Open `http://localhost:3000` in your browser to access the dashboard. All recordings and uploaded audio are saved to `audio_samples/live_recordings/`.