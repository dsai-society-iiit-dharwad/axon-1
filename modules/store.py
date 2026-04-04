from db.setup import get_connection, init_db
from datetime import datetime


def save_conversation(transcript, language, duration_sec, speaker_count=2):
    """Save a conversation record. Returns the conversation ID."""
    init_db()  # ensure tables exist
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO conversations (timestamp, raw_transcript, language, duration_sec, speaker_count)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        transcript,
        language,
        duration_sec,
        speaker_count
    ))

    conv_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f"Saved conversation #{conv_id}")
    return conv_id


def save_speaker_turns(conv_id, turns):
    """Save speaker turn records for a conversation."""
    conn = get_connection()
    cursor = conn.cursor()

    for turn in turns:
        cursor.execute("""
            INSERT INTO speaker_turns (conv_id, speaker, text, start_sec, end_sec)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conv_id,
            turn["speaker"],
            turn["text"],
            turn["start"],
            turn["end"]
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(turns)} speaker turns for conv #{conv_id}")


def save_entities(conv_id, entities, turns):
    """Save extracted entities. Tries to match entity to nearest speaker."""
    conn = get_connection()
    cursor = conn.cursor()

    for ent in entities:
        speaker = _match_entity_to_speaker(ent, turns)
        cursor.execute("""
            INSERT INTO entities (conv_id, speaker, entity_type, raw_value, normalized)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conv_id,
            speaker,
            ent.get("short_label", ent.get("label", "unknown")),
            ent["text"],
            ent.get("normalized", ent["text"])
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(entities)} entities for conv #{conv_id}")


def save_summary(conv_id, summary):
    """Save LLM summary with risk score."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO summaries (conv_id, summary_text, risk_score, risk_label, risk_reasoning)
        VALUES (?, ?, ?, ?, ?)
    """, (
        conv_id,
        str(summary),
        summary.get("risk_score", 0),
        summary.get("risk_label", "Unknown"),
        summary.get("risk_reasoning", "")
    ))

    conn.commit()
    conn.close()
    print(f"Saved summary for conv #{conv_id}")


def _match_entity_to_speaker(entity, turns):
    """Find which speaker said this entity by checking text containment."""
    entity_text = entity["text"].lower()
    for turn in turns:
        if entity_text in turn["text"].lower():
            return turn["speaker"]
    return "Unknown"


def get_all_conversations():
    """Fetch all conversations for the history page."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM conversations ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_conversation_detail(conv_id):
    """Fetch full details for one conversation."""
    conn = get_connection()
    conv = conn.execute(
        "SELECT * FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    turns = conn.execute(
        "SELECT * FROM speaker_turns WHERE conv_id = ? ORDER BY start_sec",
        (conv_id,)
    ).fetchall()
    entities = conn.execute(
        "SELECT * FROM entities WHERE conv_id = ?", (conv_id,)
    ).fetchall()
    summary = conn.execute(
        "SELECT * FROM summaries WHERE conv_id = ?", (conv_id,)
    ).fetchone()
    conn.close()

    return {
        "conversation": dict(conv) if conv else None,
        "turns": [dict(t) for t in turns],
        "entities": [dict(e) for e in entities],
        "summary": dict(summary) if summary else None,
    }


if __name__ == "__main__":
    # quick round-trip test
    conv_id = save_conversation("Test transcript", "Hinglish", 45.0)
    save_speaker_turns(conv_id, [
        {"speaker": "Speaker 1", "text": "Test turn", "start": 0.0, "end": 2.0}
    ])
    save_entities(conv_id, [
        {"text": "SIP", "short_label": "INSTRUMENT", "normalized": "SIP"}
    ], [{"speaker": "Speaker 1", "text": "Test turn SIP", "start": 0.0, "end": 2.0}])
    save_summary(conv_id, {"risk_score": 45, "risk_label": "Medium", "risk_reasoning": "Test"})

    detail = get_conversation_detail(conv_id)
    print(f"\nRound-trip OK — conv #{conv_id}:")
    print(f"  Turns: {len(detail['turns'])}")
    print(f"  Entities: {len(detail['entities'])}")
    print(f"  Risk: {detail['summary']['risk_label']}")
