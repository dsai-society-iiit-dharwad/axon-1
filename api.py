from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import tempfile
import os
import json
import time

from db.setup import init_db
from modules.store import get_all_conversations, get_conversation_detail
from dotenv import load_dotenv

load_dotenv()

init_db()

app = FastAPI(title="Armor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_pipeline_headless(audio_source, backend="local", groq_key=""):
    from modules.transcribe import transcribe_audio, transcribe_audio_groq, text_to_segments
    from modules.detect_lang import detect_language
    from modules.diarize import silence_diarize
    from modules.summarize import generate_summary
    from modules.store import (save_conversation, save_speaker_turns, save_entities, save_summary)

    is_cloud = (backend == "cloud")
    # If groq_key is not sent from frontend, fallback to environment variable
    final_groq_key = groq_key if groq_key else os.getenv("GROQ_API_KEY", "")
    
    t0 = time.time()

    # 1. Transcribe
    if audio_source == "demo_text":
        demo_transcript = "Arjun: Yaar, mujhe ek baat puchni thi — tu SIP kar raha hai na?\nMain bhi sochh raha hoon paanch hazaar monthly start karne ka.\nPriya: Haan yaar, main toh aath months se kar rahi hoon. Teen hazaar\nka Mirae Asset mein. Tu bhi kar, but pehle apna EMI ka kya plan hai?\nArjun: Wahi toh problem hai. Car loan ki EMI barah hazaar paanch sau\nhai, aathaarah more months remaining.\nPriya: Aisa mat kar yaar. Even do hazaar se SIP shuru kar abhi.\nCompounding ka fayda milega. Aathaarah mahine wait kiya toh time waste.\nArjun: Hmm, sahi bol rahi hai. Main decide karta hoon — March tak\nek SIP shuru karoonga. Do hazaar se hi sahi.\nPriya: Bilkul. Aur home loan ke baare mein bhi soch — interest rates\nabhi down hain, saade aath percent. Pehle emergency fund banaa,\nchhe months ka.\nArjun: Emergency fund mein abhi sirf chaalees hazaar hai."
        full_text, segments = text_to_segments(demo_transcript)
    elif is_cloud and final_groq_key:
        full_text, segments = transcribe_audio_groq(audio_source, final_groq_key)
    else:
        full_text, segments = transcribe_audio(audio_source)

    # 2. Language Detection
    lang_code, lang_name, _ = detect_language(full_text)

    # 3. Diarization
    turns = silence_diarize(segments)
    labeled = "\n".join(f"{t['speaker']}: {t['text']}" for t in turns)

    if is_cloud:
        # Cloud Path (Groq single pass)
        summary = generate_summary(labeled, entities=[], backend="cloud", groq_api_key=final_groq_key)
        snapshot = summary.get("financial_snapshot", {})
        entities = []
        for amt in (snapshot.get("amounts") or []):
            if amt: entities.append({"text": str(amt), "label": "financial amount", "short_label": "AMOUNT", "normalized": str(amt)})
        for inst in (snapshot.get("instruments") or []):
            if inst: entities.append({"text": str(inst), "label": "financial instrument", "short_label": "INSTRUMENT", "normalized": str(inst)})
        for tl in (snapshot.get("timelines") or []):
            if tl: entities.append({"text": str(tl), "label": "timeline", "short_label": "TIMELINE", "normalized": str(tl)})
            
        is_financial = summary.get("is_financial", True)
        fin_score = summary.get("financial_score", 0.95)
        
    else:
        # Local Path
        from modules.classify import classify_financial
        from modules.ner import extract_entities as extract_ner
        from modules.normalize import normalize_entities

        is_financial, fin_score, _ = classify_financial(full_text)
        
        all_entities = []
        seen_texts = set()
        for t in turns:
            for e in extract_ner(t["text"]):
                if e["text"].lower() not in seen_texts:
                    seen_texts.add(e["text"].lower())
                    all_entities.append(e)
        entities = normalize_entities(all_entities)
        
        if not is_financial:
            summary = {
                "is_financial": False,
                "financial_score": fin_score,
                "commitments": [],
                "pending_decisions": [],
                "financial_snapshot": {
                    "instruments": [],
                    "amounts": [],
                    "timelines": []
                },
                "speaker_sentiments": [],
                "risk_score": 0,
                "risk_label": "Low",
                "risk_reasoning": "Non-financial conversation detected. Generation bypassed."
            }
        else:
            summary = generate_summary(labeled, entities, backend="local")

    # Store in DB
    duration = segments[-1]["end"] if segments else 0.0
    speaker_count = len(set(t["speaker"] for t in turns))
    
    conv_id = save_conversation(full_text, lang_name, duration, speaker_count)
    save_speaker_turns(conv_id, turns)
    save_entities(conv_id, entities, turns)
    save_summary(conv_id, summary)

    # Automatically dispatch to Telegram if it's a financial conversation
    if is_financial:
        try:
            from modules.telegram_bot import send_telegram_summary
            send_telegram_summary(chat_id="", summary_data=summary, app_url="http://localhost:3000")
            print(f"Auto-dispatched Conv #{conv_id} to Telegram!")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Failed to auto-dispatch to Telegram: {e}")

    total_time = time.time() - t0

    return {
        "conv_id": conv_id, "full_text": full_text, "turns": turns,
        "language": lang_name, "is_financial": is_financial,
        "fin_score": fin_score, "entities": entities, "summary": summary,
        "duration": duration, "speaker_count": speaker_count,
        "pipeline_time": round(total_time, 1),
        "backend": "cloud" if is_cloud else "local"
    }

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(None),
    demo: str = Form("false"),
    backend: str = Form("local"),
    groq_key: str = Form("")
):
    try:
        audio_source = "demo_text"
        temp_path = None
        final_groq_key = groq_key if groq_key else os.getenv("GROQ_API_KEY", "")

        if file and file.filename:
            # Create a permanent recordings directory
            recordings_dir = os.path.join("audio_samples", "live_recordings")
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Preserve original extension (webm, mp3, wav, m4a, etc.)
            ext = os.path.splitext(file.filename)[1] or ".wav"
            timestamp = time.strftime("%Y%md_%H%M%S")
            permanent_filename = f"capture_{timestamp}{ext}"
            saved_path = os.path.join(recordings_dir, permanent_filename)
            
            content = await file.read()
            with open(saved_path, "wb") as f:
                f.write(content)
                
            audio_source = saved_path
            temp_path = None # We are no longer using temp files
            
        elif demo == "true":
            audio_source = "demo_text"
            demo_wav = "audio_samples/demo_arjun_priya.wav"
            if os.path.exists(demo_wav):
                audio_source = demo_wav
                
        result = run_pipeline_headless(audio_source, backend, final_groq_key)
        
        # We removed os.remove(temp_path) since files are saved permanently
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_history():
    conversations = get_all_conversations()
    return conversations

@app.get("/api/history/{conv_id}")
async def get_conversation(conv_id: int):
    detail = get_conversation_detail(conv_id)
    if not detail["conversation"]:
        raise HTTPException(status_code=404, detail="Conversation not found")
    # merge it back to shape expected
    result = {
        "conv_id": conv_id,
        "full_text": detail["conversation"]["raw_transcript"],
        "turns": detail["turns"],
        "language": detail["conversation"]["language"],
        "is_financial": True, # approximate, usually in summary
        "fin_score": 0.0,
        "entities": detail["entities"],
        "duration": detail["conversation"]["duration_sec"],
        "speaker_count": detail["conversation"]["speaker_count"],
    }
    
    if detail["summary"]:
         # summary text is stringified JSON
         try:
             result["summary"] = json.loads(detail["summary"]["summary_text"].replace("'", '"'))
         except:
             result["summary"] = {}
             result["is_financial"] = False
             
         result["fin_score"] = detail["summary"]["risk_score"] # Using risk score roughly here
    else:
         result["summary"] = {}

    return result

class TelegramPayload(BaseModel):
    chat_id: str
    summary: dict
    app_url: str = ""

@app.post("/api/telegram/send")
async def send_to_telegram(payload: TelegramPayload):
    try:
        from modules.telegram_bot import send_telegram_summary
        success = send_telegram_summary(payload.chat_id, payload.summary, payload.app_url)
        return {"status": "success", "sent": success}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
