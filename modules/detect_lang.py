from langdetect import detect, detect_langs, LangDetectException

# mapping langdetect codes to readable names
LANG_NAMES = {
    "hi": "Hindi",
    "en": "English",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ur": "Urdu",
}


def detect_language(text):
    """Detect language of text. Returns (lang_code, lang_name, confidence).
    Includes heuristic for Romanized Hindi/Hinglish that langdetect misses."""
    if not text or len(text.strip()) < 10:
        return "unknown", "Unknown", 0.0

    try:
        lang_code = detect(text)
        probabilities = detect_langs(text)

        # find confidence for the top language
        confidence = 0.0
        for prob in probabilities:
            if str(prob.lang) == lang_code:
                confidence = prob.prob
                break

        lang_name = LANG_NAMES.get(lang_code, lang_code.upper())

        # check for Hinglish — both Hindi and English detected
        lang_codes = [str(p.lang) for p in probabilities]
        if "hi" in lang_codes and "en" in lang_codes:
            lang_name = "Hinglish"

        # heuristic: langdetect misclassifies Romanized Hindi as Indonesian/etc.
        # if we see common Hindi words, override to Hinglish
        if lang_code not in ("hi", "en"):
            hindi_keywords = [
                "yaar", "hai", "karna", "hazaar", "mahine", "paanch",
                "nahi", "raha", "kya", "mein", "abhi", "bhi", "toh",
                "karoonga", "sahi", "aur", "pehle", "sirf", "wahi",
            ]
            text_lower = text.lower()
            hits = sum(1 for kw in hindi_keywords if kw in text_lower)
            if hits >= 3:
                lang_code = "hi"
                lang_name = "Hinglish"
                confidence = 0.85
                print(f"  Heuristic override: {hits} Hindi keywords found")

        print(f"Language: {lang_name} ({lang_code}), confidence: {confidence:.2f}")
        return lang_code, lang_name, confidence

    except LangDetectException as e:
        print(f"Language detection failed: {e}")
        return "unknown", "Unknown", 0.0


if __name__ == "__main__":
    samples = [
        "Yaar mujhe SIP start karna hai paanch hazaar monthly",
        "I want to start a mutual fund investment of five thousand",
        "Main bhi sochh raha hoon investment karne ka next month",
    ]
    for text in samples:
        code, name, conf = detect_language(text)
        print(f"  \"{text[:50]}...\" → {name}\n")
