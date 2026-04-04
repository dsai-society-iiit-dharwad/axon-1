# Armor — Financial Conversation Intelligence

## What Armor does in plain English

When Indians make financial decisions — taking a loan, starting
an SIP, planning an investment — they talk about it casually with
family and friends, in Hindi and English mixed together. These
conversations are never recorded, commitments get forgotten, and
disputes happen.

Armor listens to these conversations, figures out who said what,
extracts every financial commitment made, and gives you a
structured report: who committed to what, by when, and how risky
the plan is. It works completely offline on your device, or
10x faster using cloud APIs — your choice.

## Team Axon
- Thejas — ML lead, ASR pipeline
- Ryan — NLP, classifier, entity extraction
- Surya — LLM summarization, backend
- Sanketh — Frontend

## Stack
- faster-whisper (local ASR) / Groq Whisper API (cloud ASR)
- mDeBERTa (financial classifier, with keyword shortcut)
- GLiNER-Multi (NER) + Hinglish regex patterns
- Silence-gap heuristic (N-speaker diarization)
- gemma3:4b via Ollama (local) / llama-3.3-70b via Groq (cloud)
- Streamlit UI with dual-mode toggle
- SQLite for conversation history

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

For cloud mode (10x faster), set your Groq API key in the sidebar.