"""
Armor — Full Pipeline Test 
"""
import json
import os
import time

USE_LIVE_MIC = False
RECORDING_SECONDS = 120
DEMO_WAV = "audio_samples/demo_arjun_priya.wav"

TRANSCRIPT = """
Speaker 1: मेरा SIP है 5,000 $ का और मेरा income है 10,000 $ और मैंने invest amount जैसा add किया है
Speaker 2: मान लो 20,000 $ का और मैंने loan भी लिया है करीब 1,500,000 $ का तो I want to save money.
""".strip()

def run_pipeline():
    import modules.models
    t_total = time.time()

    t = time.time()
    from modules.transcribe import text_to_segments
    full_text, segments = text_to_segments(TRANSCRIPT)
    print(f"[1/6] Transcribe:  {time.time()-t:.2f}s  ({len(segments)} segments)")

    t = time.time()
    from modules.detect_lang import detect_language
    from modules.diarize import silence_diarize
    lang_code, lang_name, lang_conf = detect_language(full_text)
    turns = silence_diarize(segments)
    speaker_count = len(set(t_["speaker"] for t_ in turns))
    print(f"[2/6] Lang+Diarize:{time.time()-t:.2f}s  ({lang_name}, {speaker_count} speakers)")

    t = time.time()
    from modules.classify import classify_financial
    is_financial, fin_score, fin_label = classify_financial(full_text)
    print(f"[3/6] Classify:    {time.time()-t:.2f}s  ({fin_label}, score={fin_score:.2f})")

    t = time.time()
    from modules.ner import extract_entities
    from modules.normalize import normalize_entities
    all_entities = []
    seen_texts = set()
    for turn in turns:
        for e in extract_entities(turn["text"]):
            if e["text"].lower() not in seen_texts:
                seen_texts.add(e["text"].lower())
                all_entities.append(e)
    entities = normalize_entities(all_entities)
    print(f"[4/6] NER:         {time.time()-t:.2f}s  ({len(entities)} entities)")

    t = time.time()
    from modules.summarize import generate_summary
    labeled = "\n".join(f"{t_['speaker']}: {t_['text']}" for t_ in turns)
    summary = generate_summary(labeled, entities)
    print(f"[5/6] Summarize:   {time.time()-t:.2f}s")

    print("\nSummary JSON:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run_pipeline()
