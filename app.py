import streamlit as st
import json
import os
import time
from db.setup import init_db

init_db()

st.set_page_config(
    page_title="Armor — Financial Conversation Intelligence",
    page_icon="🛡️",
    layout="wide"
)

# ── Session state ───────────────────────────────────────────────
defaults = {"result": None, "edited_turns": None, "rerun_needed": False}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ─────────────────────────────────────────────────────
st.sidebar.title("🛡️ Armor")
st.sidebar.caption("AI-powered multilingual financial conversation intelligence")
page = st.sidebar.radio("Navigate", ["🎙️ Record & Analyze", "📜 History", "📊 Dashboard"], label_visibility="collapsed")
st.sidebar.markdown("---")

# LLM backend toggle
st.sidebar.subheader("⚙️ LLM Backend")
llm_backend = st.sidebar.radio(
    "Choose backend",
    ["🔒 Local (Ollama)", "⚡ Cloud (Groq API)"],
    help="Local: data stays on your machine. Cloud: faster but data sent to API.",
    label_visibility="collapsed"
)

groq_key = ""
if "Cloud" in llm_backend:
    groq_key = st.sidebar.text_input("Groq API Key", type="password", placeholder="gsk_...")
    st.sidebar.caption("⚡ ~3 seconds | Data sent to Groq servers")
    if not groq_key:
        st.sidebar.warning("Enter key to use cloud mode")
else:
    st.sidebar.caption("🔒 ~2-4 min on CPU | Data never leaves your machine")

st.sidebar.markdown("---")
st.sidebar.markdown("**Team Axon** • DSAI Society IIIT Dharwad")

# ── Demo transcript ─────────────────────────────────────────────
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


def run_pipeline(audio_source, duration_sec=120):
    from modules.transcribe import transcribe_audio, transcribe_audio_groq, text_to_segments
    from modules.detect_lang import detect_language
    from modules.diarize import silence_diarize
    from modules.summarize import generate_summary
    from modules.store import (
        save_conversation, save_speaker_turns,
        save_entities, save_summary
    )

    is_cloud = "Cloud" in llm_backend and groq_key
    total_steps = 5 if is_cloud else 7
    progress = st.progress(0, text="Starting pipeline...")
    t0 = time.time()

    # ── Step 1: Transcription ───────────────────────────────────
    t1 = time.time()
    if audio_source == "demo_text":
        progress.progress(10, text=f"[1/{total_steps}] Loading demo transcript...")
        full_text, segments = text_to_segments(TRANSCRIPT)
    elif audio_source and os.path.exists(audio_source):
        if is_cloud:
            progress.progress(10, text=f"[1/{total_steps}] Groq Whisper ⚡ transcribing...")
            full_text, segments = transcribe_audio_groq(audio_source, groq_key)
        else:
            progress.progress(10, text=f"[1/{total_steps}] Local Whisper transcribing...")
            full_text, segments = transcribe_audio(audio_source)
    else:
        progress.progress(10, text=f"[1/{total_steps}] Loading demo transcript...")
        full_text, segments = text_to_segments(TRANSCRIPT)
    print(f"  ⏱ Transcription: {time.time()-t1:.1f}s")

    # ── Step 2: Language Detection ──────────────────────────────
    t1 = time.time()
    progress.progress(20, text=f"[2/{total_steps}] Detecting language...")
    lang_code, lang_name, _ = detect_language(full_text)
    print(f"  ⏱ Language: {time.time()-t1:.1f}s")

    # ── Step 3: Speaker Diarization ─────────────────────────────
    t1 = time.time()
    progress.progress(30, text=f"[3/{total_steps}] Speaker segmentation...")
    turns = silence_diarize(segments)
    print(f"  ⏱ Diarization: {time.time()-t1:.1f}s")

    labeled = "\n".join(f"{t['speaker']}: {t['text']}" for t in turns)

    if is_cloud:
        # ═══ CLOUD PATH: Groq handles classification + NER + summary ═══
        t1 = time.time()
        progress.progress(50, text=f"[4/{total_steps}] Groq AI analysis ⚡...")
        stream_box = st.empty()
        summary = generate_summary(labeled, entities=[],
                                   st_placeholder=stream_box,
                                   backend="cloud", groq_api_key=groq_key)
        stream_box.empty()
        print(f"  ⏱ Groq analysis: {time.time()-t1:.1f}s")

        # Extract entities from Groq's financial_snapshot for DB storage
        snapshot = summary.get("financial_snapshot", {})
        entities = []
        for amt in (snapshot.get("amounts") or []):
            if amt:
                entities.append({"text": str(amt), "label": "financial amount",
                                 "short_label": "AMOUNT", "normalized": str(amt)})
        for inst in (snapshot.get("instruments") or []):
            if inst:
                entities.append({"text": str(inst), "label": "financial instrument",
                                 "short_label": "INSTRUMENT", "normalized": str(inst)})
        for tl in (snapshot.get("timelines") or []):
            if tl:
                entities.append({"text": str(tl), "label": "timeline",
                                 "short_label": "TIMELINE", "normalized": str(tl)})

        is_financial = summary.get("is_financial", True)
        fin_score = summary.get("financial_score", 0.95)
        fin_label = "financial discussion" if is_financial else "general conversation"

    else:
        # ═══ LOCAL PATH: Full pipeline with local models ═══════════
        from modules.classify import classify_financial
        from modules.ner import extract_entities as extract_ner
        from modules.normalize import normalize_entities

        # Step 4: Classification
        t1 = time.time()
        progress.progress(40, text=f"[4/{total_steps}] Financial classification...")
        is_financial, fin_score, fin_label = classify_financial(full_text)
        print(f"  ⏱ Classification: {time.time()-t1:.1f}s")

        # Step 5: NER
        t1 = time.time()
        progress.progress(55, text=f"[5/{total_steps}] Extracting entities...")
        all_entities = []
        seen_texts = set()
        for t in turns:
            for e in extract_ner(t["text"]):
                if e["text"].lower() not in seen_texts:
                    seen_texts.add(e["text"].lower())
                    all_entities.append(e)
        entities = normalize_entities(all_entities)
        print(f"  ⏱ NER: {time.time()-t1:.1f}s")

        # Step 6: Summary via Ollama
        t1 = time.time()
        progress.progress(70, text=f"[6/{total_steps}] AI summary via Ollama 🔒...")
        stream_box = st.empty()
        summary = generate_summary(labeled, entities,
                                   st_placeholder=stream_box,
                                   backend="local")
        stream_box.empty()
        print(f"  ⏱ LLM Summary: {time.time()-t1:.1f}s")

    # ── Final: Save to DB ───────────────────────────────────────
    t1 = time.time()
    progress.progress(90, text=f"[{total_steps}/{total_steps}] Saving to database...")
    duration = segments[-1]["end"] if segments else 0.0
    speaker_count = len(set(t["speaker"] for t in turns))
    conv_id = save_conversation(full_text, lang_name, duration, speaker_count)
    save_speaker_turns(conv_id, turns)
    save_entities(conv_id, entities, turns)
    save_summary(conv_id, summary)

    total = time.time() - t0
    progress.progress(100, text=f"✅ Done in {total:.0f}s")

    return {
        "conv_id": conv_id, "full_text": full_text, "turns": turns,
        "language": lang_name, "is_financial": is_financial,
        "fin_score": fin_score, "entities": entities, "summary": summary,
        "duration": duration, "speaker_count": speaker_count,
        "pipeline_time": round(total, 1),
        "backend": "Cloud ⚡" if is_cloud else "Local 🔒",
    }


# ═══════════════════════════════════════════════════════════════
# PAGE 1 — Record & Analyze
# ═══════════════════════════════════════════════════════════════
if page == "🎙️ Record & Analyze":
    st.title("🎙️ Record & Analyze")

    col_input, col_info = st.columns([2, 1])

    with col_input:
        duration = st.slider("Recording duration (seconds)", 30, 300, 120)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🎤 Record Live", width="stretch"):
                from modules.audio import record_audio
                with st.spinner("Recording..."):
                    wav_path = record_audio(duration)
                if wav_path:
                    st.session_state.result = run_pipeline(wav_path, duration)
                    st.session_state.edited_turns = None
                else:
                    st.error("Mic failed — use Demo Audio instead")
        with c2:
            if st.button("📂 Demo Audio", width="stretch"):
                demo_wav = "audio_samples/demo_arjun_priya.wav"
                source = demo_wav if os.path.exists(demo_wav) else "demo_text"
                st.session_state.result = run_pipeline(source)
                st.session_state.edited_turns = None
        with c3:
            uploaded = st.file_uploader("Upload WAV", type=["wav"], label_visibility="collapsed")
            if uploaded:
                os.makedirs("audio_samples", exist_ok=True)
                path = "audio_samples/uploaded.wav"
                with open(path, "wb") as f:
                    f.write(uploaded.read())
                st.session_state.result = run_pipeline(path)
                st.session_state.edited_turns = None

    with col_info:
        st.caption("**Pipeline:** Whisper → Language Detection → Speaker Diarization → "
                   "mDeBERTa Classification → GLiNER NER → Ollama Summary → SQLite")

    # ── Results ─────────────────────────────────────────────────
    result = st.session_state.result
    if not result:
        st.info("Click a button above to start. 'Demo Audio' works without a mic.")
        st.stop()

    st.markdown("---")
    st.caption(f"⏱ Processed in {result.get('pipeline_time', '?')}s using {result.get('backend', 'Unknown')} mode")

    # non-financial warning
    if not result["is_financial"]:
        st.warning(f"⚠️ This conversation was NOT classified as financial "
                   f"(score: {result['fin_score']:.0%}). Results may be limited.")

    # metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Language", result["language"])
    m2.metric("Financial", f"{result['fin_score']:.0%}")
    m3.metric("Speakers", result["speaker_count"])
    m4.metric("Entities", len(result["entities"]))
    m5.metric("Conv #", result["conv_id"])

    # ── Transcript with editing ──────────────────────────────
    st.subheader("💬 Transcript — Review & Edit")
    st.caption("You can rename speakers and edit each line. Changes are reflected in the analysis below.")

    turns = result["turns"]
    speakers = sorted(set(t["speaker"] for t in turns))

    # speaker renaming
    st.markdown("**Rename speakers:**")
    rename_cols = st.columns(min(len(speakers), 5))
    speaker_map = {}
    for i, spk in enumerate(speakers):
        with rename_cols[i % len(rename_cols)]:
            speaker_map[spk] = st.text_input(f"{spk}:", value=spk, key=f"rn_{spk}")

    # editable transcript
    edited_turns = []
    for i, turn in enumerate(turns):
        display_name = speaker_map.get(turn["speaker"], turn["speaker"])
        col_spk, col_txt = st.columns([1, 5])
        with col_spk:
            st.markdown(f"**{display_name}**")
        with col_txt:
            edited_text = st.text_input(
                f"turn_{i}", value=turn["text"],
                key=f"edit_{i}", label_visibility="collapsed"
            )
            edited_turns.append({
                **turn,
                "speaker": display_name,
                "text": edited_text
            })

    # ── Two-column results ──────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # entities
        st.subheader("🏷️ Extracted Entities")
        entity_icons = {
            "AMOUNT": "💰", "INSTRUMENT": "📈", "TIMELINE": "⏰",
            "PERSON": "👤", "COMMITMENT": "🤝"
        }
        if result["entities"]:
            for e in result["entities"]:
                icon = entity_icons.get(e["short_label"], "🔹")
                norm = e.get("normalized", e["text"])
                if norm != e["text"]:
                    st.markdown(f"{icon} **{e['short_label']}**: {e['text']} → **{norm}**")
                else:
                    st.markdown(f"{icon} **{e['short_label']}**: {e['text']}")
        else:
            st.info("No entities found")

        # sentiment (bonus feature)
        summary = result["summary"]
        sentiments = summary.get("speaker_sentiments", [])
        if sentiments:
            st.subheader("🎭 Speaker Sentiments")
            for s in sentiments:
                spk = speaker_map.get(s.get("speaker", ""), s.get("speaker", ""))
                sentiment = s.get("sentiment", "unknown")
                emoji = {"cautious": "😐", "optimistic": "😊", "anxious": "😟",
                         "confident": "😎", "neutral": "😐"}.get(sentiment.lower(), "🤔")
                st.markdown(f"{emoji} **{spk}**: {sentiment} — {s.get('reasoning', '')}")

    with col_right:
        # risk score
        st.subheader("⚠️ Risk Assessment")
        risk_score = summary.get("risk_score", 0)
        risk_label = summary.get("risk_label", "Unknown")
        color_map = {"Low": "green", "Medium": "orange", "High": "red"}
        risk_color = color_map.get(risk_label, "gray")

        st.markdown(f"### :{risk_color}[{risk_label} Risk] — {risk_score}/100")
        st.progress(min(risk_score, 100) / 100)
        st.caption(summary.get("risk_reasoning", ""))

        # financial snapshot
        snapshot = summary.get("financial_snapshot", {})
        if snapshot.get("instruments"):
            items = [str(x) for x in snapshot["instruments"] if x]
            st.markdown("**📈 Instruments:** " + " • ".join(items))
        if snapshot.get("amounts"):
            items = [str(x) for x in snapshot["amounts"] if x]
            st.markdown("**💰 Amounts:** " + " • ".join(items))
        if snapshot.get("timelines"):
            items = [str(x) for x in snapshot["timelines"] if x]
            st.markdown("**⏰ Timelines:** " + " • ".join(items))

        # commitments
        commitments = summary.get("commitments", [])
        if commitments:
            st.subheader("📋 Commitments")
            for c in commitments:
                spk = speaker_map.get(c.get("speaker", ""), c.get("speaker", ""))
                st.markdown(f"- **{spk}**: {c['commitment']}")

        # pending decisions
        pending = summary.get("pending_decisions", [])
        if pending:
            st.subheader("❓ Pending Decisions")
            for p in pending:
                st.markdown(f"- {p}")

    # raw JSON + export
    with st.expander("🔍 Raw Summary JSON"):
        st.json(summary)

    report_json = json.dumps(summary, indent=2, ensure_ascii=False)
    st.download_button("📥 Download Report", report_json,
                       file_name="armor_report.json", mime="application/json")


# ═══════════════════════════════════════════════════════════════
# PAGE 2 — History
# ═══════════════════════════════════════════════════════════════
elif page == "📜 History":
    st.title("📜 Conversation History")
    from modules.store import get_all_conversations, get_conversation_detail

    conversations = get_all_conversations()
    if not conversations:
        st.info("No conversations yet. Go to Record & Analyze to create one.")
        st.stop()

    st.markdown(f"**{len(conversations)}** conversations recorded")

    for conv in conversations:
        detail = get_conversation_detail(conv["id"])
        risk = detail["summary"].get("risk_label", "—") if detail["summary"] else "—"

        with st.expander(
            f"#{conv['id']} • {conv['timestamp'][:16]} • {conv['language']} • "
            f"{conv.get('speaker_count', '?')} speakers • Risk: {risk} • "
            f"{conv.get('duration_sec', 0):.0f}s"
        ):
            tab1, tab2, tab3 = st.tabs(["Transcript", "Entities", "Summary"])

            with tab1:
                for t in detail["turns"]:
                    st.markdown(f"**{t['speaker']}:** {t['text']}")

            with tab2:
                if detail["entities"]:
                    for e in detail["entities"]:
                        st.markdown(f"- **{e['entity_type']}**: {e['raw_value']} → {e['normalized']}")
                else:
                    st.caption("No entities")

            with tab3:
                if detail["summary"]:
                    try:
                        sj = detail["summary"]["summary_text"]
                        st.json(json.loads(sj.replace("'", '"')))
                    except Exception:
                        st.text(str(detail["summary"].get("summary_text", "")))
                    st.metric("Risk", f"{detail['summary'].get('risk_label', '?')} ({detail['summary'].get('risk_score', '?')}/100)")


# ═══════════════════════════════════════════════════════════════
# PAGE 3 — Dashboard (Bonus: visualization)
# ═══════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.title("📊 Financial Insights Dashboard")
    from modules.store import get_all_conversations, get_conversation_detail

    conversations = get_all_conversations()
    if not conversations:
        st.info("No data yet. Analyze some conversations first.")
        st.stop()

    # risk score timeline
    risk_scores = []
    timestamps = []
    languages = []
    for conv in conversations:
        detail = get_conversation_detail(conv["id"])
        if detail["summary"]:
            risk_scores.append(detail["summary"].get("risk_score", 0))
            timestamps.append(conv["timestamp"][:16])
            languages.append(conv["language"])

    if risk_scores:
        st.subheader("Risk Score Trend")
        import pandas as pd
        df = pd.DataFrame({"Conversation": timestamps, "Risk Score": risk_scores})
        st.bar_chart(df.set_index("Conversation"))

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Conversations", len(conversations))
        col2.metric("Avg Risk Score", f"{sum(risk_scores)/len(risk_scores):.0f}/100")
        col3.metric("Languages", ", ".join(set(languages)))

    # all entities across conversations
    st.subheader("All Financial Entities")
    all_ents = []
    for conv in conversations:
        detail = get_conversation_detail(conv["id"])
        for e in detail["entities"]:
            all_ents.append({
                "Conv #": conv["id"],
                "Type": e["entity_type"],
                "Value": e["raw_value"],
                "Normalized": e["normalized"],
                "Speaker": e["speaker"]
            })

    if all_ents:
        import pandas as pd
        st.dataframe(pd.DataFrame(all_ents), width="stretch")
    else:
        st.caption("No entities found across conversations")
