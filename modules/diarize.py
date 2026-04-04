SILENCE_GAP_SHORT = 0.6   # gap > this = speaker change
SILENCE_GAP_LONG = 1.5    # gap > this = new speaker entering


def silence_diarize(segments, max_speakers=None):
    """N-speaker diarization using silence gaps between segments.
    gap > 0.6s = existing speaker changes turn
    gap > 1.5s = brand new speaker enters conversation"""
    if not segments:
        return []

    if max_speakers is None:
        max_speakers = 5

    turns = []
    speaker_idx = 0
    active_speakers = 1

    for i, seg in enumerate(segments):
        if i > 0:
            gap = seg["start"] - segments[i - 1]["end"]
            if gap > SILENCE_GAP_LONG and active_speakers < max_speakers:
                # long silence — new voice entering
                speaker_idx = active_speakers
                active_speakers += 1
            elif gap > SILENCE_GAP_SHORT:
                # regular pause — cycle to next known speaker
                speaker_idx = (speaker_idx + 1) % active_speakers

        turns.append({
            "speaker": f"Speaker {speaker_idx + 1}",
            "text": seg["text"],
            "start": seg["start"],
            "end": seg["end"]
        })

    speaker_count = len(set(t["speaker"] for t in turns))
    print(f"Silence diarization: {len(turns)} turns, {speaker_count} speakers")
    return turns


if __name__ == "__main__":
    # test: 3 speakers with escalating gaps
    fake = [
        {"start": 0.0, "end": 3.0, "text": "Speaker A says something"},
        {"start": 3.3, "end": 5.0, "text": "Speaker A continues"},
        {"start": 6.0, "end": 9.0, "text": "Speaker B responds"},
        {"start": 9.4, "end": 11.0, "text": "Speaker B adds more"},
        {"start": 13.0, "end": 16.0, "text": "New voice enters"},
        {"start": 16.5, "end": 18.0, "text": "Speaker A replies"},
    ]
    for t in silence_diarize(fake):
        print(f"  [{t['speaker']}] {t['text']}")
