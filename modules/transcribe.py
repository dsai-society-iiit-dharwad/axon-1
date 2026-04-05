import re
import requests
import json

GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


def transcribe_audio(wav_path):
    """Local Whisper transcription. Returns (full_text, segments_list)."""
    from modules.models import whisper_model

    segments_iter, info = whisper_model.transcribe(
        wav_path,
        beam_size=5,
        word_timestamps=True,
        language=None,
        vad_filter=True
    )

    segments_list = []
    full_text_parts = []
    for seg in segments_iter:
        segments_list.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip()
        })
        full_text_parts.append(seg.text.strip())

    full_text = " ".join(full_text_parts)

    if re.search(r'[\u0900-\u097F\u0980-\u09FF]', full_text):
        print("WARNING: Devanagari/Bengali script detected.")

    print(f"Transcribed {len(segments_list)} segments, {len(full_text)} chars")
    return full_text, segments_list


def transcribe_audio_groq(wav_path, api_key):
    """Groq Whisper API transcription (~2-3 seconds)."""
    print("Transcribing via Groq Whisper API...")

    with open(wav_path, "rb") as f:
        response = requests.post(
            GROQ_WHISPER_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            files={"file": (wav_path, f, "audio/wav")},
            data={
                "model": "whisper-large-v3",
                "response_format": "verbose_json",
                "language": "hi",
                "temperature": 0.0,
                "prompt": "Indian context. Currency is Rupees (₹), not Dollars. Terms: SIP, EMI, mutual fund."
            },
            timeout=60
        )

    response.raise_for_status()
    result = response.json()

    full_text = result.get("text", "").strip()
    segments_list = []
    for seg in result.get("segments", []):
        segments_list.append({
            "start": seg.get("start", 0.0),
            "end": seg.get("end", 0.0),
            "text": seg.get("text", "").strip()
        })

    if not segments_list and full_text:
        segments_list = [{"start": 0.0, "end": 10.0, "text": full_text}]

    print(f"Groq Whisper: {len(segments_list)} segments, {len(full_text)} chars")
    return full_text, segments_list


def text_to_segments(raw_text):
    """Convert raw text to fake timestamped segments for testing.
    Uses ~0.4s per word to generate realistic gaps for diarization."""
    lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]

    segments = []
    current_time = 0.0
    prev_speaker = None
    seen_speakers = set()

    for line in lines:
        text = line
        current_speaker = None
        if ":" in line and line.index(":") < 20:
            current_speaker = line.split(":", 1)[0].strip()
            text = line.split(":", 1)[1].strip()

        # generate realistic gaps for diarizer
        if prev_speaker is not None:
            if current_speaker and current_speaker not in seen_speakers:
                current_time += 2.0  # > 1.5s → diarizer creates new speaker
            elif current_speaker and current_speaker != prev_speaker:
                current_time += 1.0  # > 0.6s → diarizer cycles to next speaker
            else:
                current_time += 0.3  # < 0.6s → same speaker continues

        if current_speaker:
            seen_speakers.add(current_speaker)
            prev_speaker = current_speaker

        # ~0.4s per word for realistic duration
        word_count = len(text.split())
        duration = max(1.0, word_count * 0.4)
        segments.append({
            "start": current_time,
            "end": current_time + duration,
            "text": text
        })
        current_time += duration

    full_text = " ".join(s["text"] for s in segments)
    print(f"Created {len(segments)} segments from raw text ({len(full_text)} chars)")
    return full_text, segments


if __name__ == "__main__":
    test_text = """Arjun: Yaar, mujhe ek baat puchni thi
Priya: Haan bolo kya hua
Arjun: SIP start karna hai paanch hazaar monthly"""

    full_text, segs = text_to_segments(test_text)
    for s in segs:
        print(f"  [{s['start']:.1f}s - {s['end']:.1f}s] {s['text'][:60]}")
