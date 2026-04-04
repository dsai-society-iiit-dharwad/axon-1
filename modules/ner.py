import re

LABELS = [
    "money amount or financial figure in rupees or percentage",
    "financial instrument such as SIP EMI loan or mutual fund",
    "time duration or deadline or remaining period",
    "person name",
    "financial commitment or decision or plan",
]

LABEL_SHORT = {
    "money amount or financial figure in rupees or percentage": "AMOUNT",
    "financial instrument such as SIP EMI loan or mutual fund": "INSTRUMENT",
    "time duration or deadline or remaining period": "TIMELINE",
    "person name": "PERSON",
    "financial commitment or decision or plan": "COMMITMENT",
}

THRESHOLD = 0.60

# keyword patterns for Romanized Hindi that GLiNER misses
KEYWORD_PATTERNS = {
    "AMOUNT": [
        r"(?:ek|do|teen|chaar|paanch|chhe|saat|aath|nau|das|barah|"
        r"pandrah|bees|chaalees|pachaas|sau)\s*(?:hazaar(?:\s+paanch\s+sau)?)",
        r"saade\s+aath\s+percent",
        r"das\s+percent",
        r"₹[\d,]+",
        r"\d+[\d,]*\s*(?:rupees|rs|percent|%)",
    ],
    "INSTRUMENT": [
        r"\bSIP\b", r"\bEMI\b", r"\bmutual\s+fund\b",
        r"\bcar\s+loan\b", r"\bhome\s+loan\b", r"\bloan\b",
        r"\bMirae\s+Asset\b", r"\bemergency\s+fund\b",
    ],
    "TIMELINE": [
        r"(?:ek|do|teen|chaar|paanch|chhe|saat|aath|nau|das|barah|"
        r"aathaarah)\s*(?:mahine?|months?)",
        r"(?:by|tak)\s+(?:March|April|May|June|July|August|"
        r"September|October|November|December|January|February)",
        r"\d+\s*(?:months?|years?|mahine?)\s*(?:remaining)?",
    ],
}





def keyword_extract(text):
    """Catch common Romanized Hindi financial terms via regex."""
    found = []
    for label, patterns in KEYWORD_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                found.append({
                    "text": match.group().strip(),
                    "label": label,
                    "short_label": label,
                    "score": 0.80,
                    "start": match.start(),
                    "end": match.end(),
                })
    return found


def extract_entities(text):
    """Extract entities using GLiNER + keyword fallback. Deduplicates."""
    if not text or len(text.strip()) < 10:
        return []

    from modules.models import gliner_model
    gliner_ents = gliner_model.predict_entities(text, LABELS, threshold=THRESHOLD)
    keyword_ents = keyword_extract(text)

    # merge: GLiNER results first (higher quality), then keyword supplements
    all_raw = []
    for ent in gliner_ents:
        ent["short_label"] = LABEL_SHORT.get(ent.get("label", ""), ent.get("label", ""))
        all_raw.append(ent)
    all_raw.extend(keyword_ents)

    entities = _deduplicate(all_raw)
    gliner_count = len([e for e in gliner_ents])
    keyword_count = len(entities) - min(len(gliner_ents), len(entities))
    print(f"Extracted {len(entities)} entities (GLiNER: {len(gliner_ents)}, keyword: {len(keyword_ents)})")
    return entities


def _deduplicate(raw_entities):
    """Keep only the highest-scoring entity for each character span."""
    if not raw_entities:
        return []

    sorted_ents = sorted(raw_entities, key=lambda e: e.get("score", 0), reverse=True)
    kept = []
    used_ranges = []

    for ent in sorted_ents:
        ent_start = ent.get("start", 0)
        ent_end = ent.get("end", 0)

        overlaps = False
        for used_start, used_end in used_ranges:
            if ent_start < used_end and ent_end > used_start:
                overlaps = True
                break

        if not overlaps:
            short_label = ent.get("short_label", LABEL_SHORT.get(ent.get("label", ""), "ENTITY"))
            kept.append({
                "text": ent["text"],
                "label": ent.get("label", short_label),
                "short_label": short_label,
                "score": round(ent.get("score", 0.8), 3),
                "start": ent_start,
                "end": ent_end,
            })
            used_ranges.append((ent_start, ent_end))

    return sorted(kept, key=lambda e: e["start"])


if __name__ == "__main__":
    test = (
        "Car loan ki EMI barah hazaar paanch sau hai, "
        "aathaarah more months remaining. "
        "Main SIP start karoonga do hazaar se March tak."
    )
    entities = extract_entities(test)
    for e in entities:
        print(f"  [{e['short_label']}] \"{e['text']}\" (score: {e['score']})")

