"""
Armor — Full Pipeline Test (offline, no UI, no mic)
Run: python test_pipeline.py > batch_output.txt 2>&1
"""
import json
import os
import time

# ── Config ──────────────────────────────────────────────────────
USE_LIVE_MIC = False
RECORDING_SECONDS = 120
DEMO_WAV = "audio_samples/demo_arjun_priya.wav"

TRANSCRIPT = """
Arjun: Yaar, mujhe ek baat puchni thi — tu SIP kar raha hai na?
Main bhi sochh raha hoon paanch hazaar monthly start karne ka.
Priya: Haan yaar, main toh aath months se kar rahi hoon. Teen hazaar
ka Mirae Asset mein. Tu bhi kar, but pehle apna EMI ka kya plan hai?
Arjun: Wahi toh problem hai. Car loan ki EMI barah hazaar paanch sau
hai, aathaarah more months remaining.
Priya: Aisa mat kar yaar. Even do hazaar se SIP shuru kar abhi.
Compounding ka fayda milega. Aathaarah mahine wait kiya toh time waste.
Arjun: Hmm, sahi bol rahi hai. Main decide karta hoon — March tak
ek SIP shuru karoonga. Do hazaar se hi sahi.
Priya: Bilkul. Aur home loan ke baare mein bhi soch — interest rates
abhi down hain, saade aath percent. Pehle emergency fund banaa,
chhe months ka.
Arjun: Emergency fund mein abhi sirf chaalees hazaar hai.
""".strip()


def run_pipeline():
    # load all models upfront so per-stage timing is clean
    import modules.models  # noqa — triggers one-time 45s startup
    t_total = time.time()

    # ── [1/6] Transcription ─────────────────────────────────────
    t = time.time()
    from modules.transcribe import transcribe_audio, text_to_segments

    wav_path = None
    if USE_LIVE_MIC:
        from modules.audio import get_audio
        wav_path = get_audio(use_live_mic=True, duration_sec=RECORDING_SECONDS)

    if not USE_LIVE_MIC and os.path.exists(DEMO_WAV):
        wav_path = DEMO_WAV

    if wav_path and os.path.exists(wav_path):
        full_text, segments = transcribe_audio(wav_path)
    else:
        full_text, segments = text_to_segments(TRANSCRIPT)
    print(f"[1/6] Transcribe:  {time.time()-t:.2f}s  ({len(segments)} segments, {len(full_text)} chars)")

    # ── [2/6] Language + Diarization ────────────────────────────
    t = time.time()
    from modules.detect_lang import detect_language
    from modules.diarize import silence_diarize

    lang_code, lang_name, lang_conf = detect_language(full_text)
    turns = silence_diarize(segments)
    speaker_count = len(set(t_["speaker"] for t_ in turns))
    print(f"[2/6] Lang+Diarize:{time.time()-t:.2f}s  ({lang_name}, {speaker_count} speakers, {len(turns)} turns)")

    # ── [3/6] Financial Classification ──────────────────────────
    t = time.time()
    from modules.classify import classify_financial
    is_financial, fin_score, fin_label = classify_financial(full_text)
    print(f"[3/6] Classify:    {time.time()-t:.2f}s  ({fin_label}, score={fin_score:.2f})")

    # ── [4/6] Entity Extraction ─────────────────────────────────
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

    # ── [5/6] LLM Summary ──────────────────────────────────────
    t = time.time()
    from modules.summarize import generate_summary
    labeled = "\n".join(f"{t_['speaker']}: {t_['text']}" for t_ in turns)
    summary = generate_summary(labeled, entities)
    print(f"[5/6] Summarize:   {time.time()-t:.2f}s")

    # ── [6/6] Save to Database ──────────────────────────────────
    t = time.time()
    from modules.store import (
        save_conversation, save_speaker_turns,
        save_entities, save_summary
    )
    duration = segments[-1]["end"] if segments else 0.0
    conv_id = save_conversation(full_text, lang_name, duration, speaker_count)
    save_speaker_turns(conv_id, turns)
    save_entities(conv_id, entities, turns)
    save_summary(conv_id, summary)
    print(f"[6/6] Store:       {time.time()-t:.2f}s  (conv #{conv_id})")

    total = time.time() - t_total
    print(f"\nTotal pipeline:    {total:.2f}s")

    # ── Final Output ────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("ARMOR PIPELINE — COMPLETE")
    print("=" * 60)
    print(f"Language:  {lang_name} ({lang_code})")
    print(f"Financial: {fin_label} (score: {fin_score:.2f})")
    print(f"Speakers:  {speaker_count}")
    print(f"Entities:  {len(entities)}")
    print(f"Conv ID:   {conv_id}")
    for e in entities:
        print(f"  [{e['short_label']}] {e['text']} → {e['normalized']}")
    print()
    print("Summary JSON:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_pipeline()
