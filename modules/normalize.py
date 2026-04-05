import re

# Hindi numeral words → normalized values
# Only for VALUE CONVERSION after GLiNER detects the span
HINDI_VALUES = {
    "ek hazaar": "₹1,000",
    "do hazaar": "₹2,000",
    "teen hazaar": "₹3,000",
    "chaar hazaar": "₹4,000",
    "paanch hazaar": "₹5,000",
    "das hazaar": "₹10,000",
    "barah hazaar": "₹12,000",
    "barah hazaar paanch sau": "₹12,500",
    "paanch hazaar paanch sau": "₹5,500",
    "chaalees hazaar": "₹40,000",
    "ek mahina": "1 month",
    "teen mahine": "3 months",
    "chhe mahine": "6 months",
    "chhe months": "6 months",
    "aath mahine": "8 months",
    "aath months": "8 months",
    "barah mahine": "12 months",
    "aathaarah mahine": "18 months",
    "aathaarah months": "18 months",
    "saade aath percent": "8.5%",
    "das percent": "10%",
}


def normalize_entity(raw_text):
    """Convert Hindi numeral text to normalized value.
    Returns normalized string or original if no match found."""
    cleaned = raw_text.strip().lower()

    # try exact match first
    if cleaned in HINDI_VALUES:
        return HINDI_VALUES[cleaned]

    # try longest substring match (handles partial matches)
    # sort by length descending so longer matches win
    for hindi, normalized in sorted(
        HINDI_VALUES.items(), key=lambda x: len(x[0]), reverse=True
    ):
        if hindi in cleaned:
            return normalized

    # catch numeric patterns already in text (e.g. "12,500" or "₹5000")
    if re.search(r'[₹$%]|[\d,]+', cleaned):
        # convert dollar hallucination to rupees
        result = raw_text.strip()
        if "$" in result:
            result = result.replace("$", "₹")
        return result

    return raw_text.strip()


def normalize_entities(entities):
    """Add normalized values to a list of entity dicts.
    Modifies entities in-place and returns them."""
    for ent in entities:
        ent["normalized"] = normalize_entity(ent["text"])
        if ent["normalized"] != ent["text"]:
            print(f"  Normalized: \"{ent['text']}\" → {ent['normalized']}")

    normalized_count = sum(
        1 for e in entities if e["normalized"] != e["text"]
    )
    print(f"Normalized {normalized_count}/{len(entities)} entities")
    return entities


if __name__ == "__main__":
    test_entities = [
        {"text": "barah hazaar paanch sau", "short_label": "AMOUNT"},
        {"text": "aathaarah mahine", "short_label": "TIMELINE"},
        {"text": "do hazaar", "short_label": "AMOUNT"},
        {"text": "saade aath percent", "short_label": "AMOUNT"},
        {"text": "SIP", "short_label": "INSTRUMENT"},
        {"text": "chaalees hazaar", "short_label": "AMOUNT"},
        {"text": "chhe mahine", "short_label": "TIMELINE"},
    ]
    results = normalize_entities(test_entities)
    print()
    for r in results:
        print(f"  [{r['short_label']}] {r['text']} → {r['normalized']}")
