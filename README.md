<div align="center">
  <img src="https://img.shields.io/badge/Armor-Intelligence-000000?style=for-the-badge&logoColor=white" alt="Armor Logo" />
  <h1 align="center">Armor Financial Intelligence</h1>
  <p align="center">
    <strong>An end-to-end Machine Learning pipeline for structuring multilingual financial conversations.</strong>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=FastAPI&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black" alt="HuggingFace" />
    <img src="https://img.shields.io/badge/Ollama-000000?style=flat-square&logo=ollama&logoColor=white" alt="Ollama" />
    <img src="https://img.shields.io/badge/Next.js-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js" />
  </p>
</div>

---

## 🛡️ The Problem

In India, critical financial decisions (EMIs, SIPs, loans, informal debt) are frequently discussed in code-mixed languages like Hinglish. Because these conversations are unstructured, tracking subjective financial risk and formal commitments is incredibly difficult. 

**Armor** is an autonomous ML pipeline that passively transcribes, classifies, and extracts structured intelligence from raw conversational audio.

---

## 🧠 The AI / ML Pipeline

Armor is built around a rigorous, multi-stage machine learning orchestrated pipeline designed to run both locally and in the cloud.

1. **Audio Transcription (`faster-whisper`)**: Processes raw 16kHz mono WAV audio to transcribe code-mixed inputs (e.g., Hinglish) into raw text with word-level timestamps.
2. **Language Detection (`langdetect`)**: Identifies the primary language topology.
3. **Speaker Diarization**: Leverages silence-gap heuristics and speaker-segmentation to actively toggle between interlocutors (e.g., `Speaker 1` and `Speaker 2`).
4. **Context Classification (`mDeBERTa`)**: Utilizes `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` (Zero-Shot Classification) to aggressively filter out non-financial dialogue, protecting the LLM from hallucinating on casual conversations.
5. **Named Entity Recognition (`GLiNER`)**: Uses `urchade/gliner_multi-v2.1` to extract unstructured monetary spans, timelines, and financial instruments natively in Hindi/English context.
6. **Entity Normalization**: Maps localized verbal terms (e.g., *"barah hazaar paanch sau"*) to structured integers (*"₹12,500"*).
7. **Generative Intelligence (`Ollama` / `Llama`)**: Parses the normalized entities and diarized transcript through `llama3.2:1b` or `llama-3.3-70b` using strict JSON-schema enforcement to extract final commitments, subjective sentiments, and a calculated Risk Score.

---

## 🚀 Setup & Execution

You will need two open terminal windows to run the localized simulation. Ensure you have Node.js and Python 3.10+ installed.

### 1. Environment Configurations
Create a `.env` file in your root `Axon-1/` project folder and configure your keys:
```env
# Required for Cloud Inference (Groq)
GROQ_API_KEY="your_groq_key"

# Required for Automated Telegram Dispatch
TELEGRAM_BOT_TOKEN="your_botfather_token"
TELEGRAM_CHAT_ID="your_personal_chat_id" 

# Local Hook
OLLAMA_URL="http://localhost:11434"
```

### 2. Boot the ML Backend
From the root project directory:
```bash
# Activate your virtual environment
.venv\Scripts\activate

# Start the FastAPI Orchestrator
python api.py
```
> The FastAPI service will load the Whisper, mDeBERTa, and GLiNER tensors into memory and bind to `http://localhost:8000`.

### 3. Boot the UX Dashboard
Open a new terminal session:
```bash
cd frontend
npm run dev
```
> The React application will spin up at `http://localhost:3000`. Audio captures are dynamically stored to `audio_samples/live_recordings/`.

---

## 👥 Axon Team Leads
**Thejas** 
**Ryan**
**Surya** 
**Sanketh**