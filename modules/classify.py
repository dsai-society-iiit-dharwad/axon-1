
_classifier = None

MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
LABELS = ["financial discussion", "general conversation"]
THRESHOLD = 0.60

# keyword hit = skip mDeBERTa entirely
FINANCIAL_KEYWORDS = {
    "sip", "emi", "loan", "interest", "mutual fund", "fd", "rd",
    "insurance", "equity", "stocks", "investment", "savings",
    "salary", "income", "expense", "debt", "credit", "mortgage",
    "hazaar", "paisa", "rupee", "udhaar", "mahina", "kisht",
    "nivesh", "bachat", "byaj", "karz", "bima", "zerodha",
    "hdfc", "sbi", "mirae", "paytm", "gpay", "lic"
}




def classify_financial(text):
    if not text or len(text.strip()) < 20:
        return False, 0.0, "too short"

    # fast keyword check — skip mDeBERTa if any match
    words = set(text.lower().split())
    matched = words & FINANCIAL_KEYWORDS
    if matched:
        print(f"Keyword shortcut: matched {matched}")
        return True, 0.95, "financial discussion"

    # no keywords — run mDeBERTa for ambiguous cases
    from modules.models import classifier
    result = classifier(text, LABELS)
    top_label = result["labels"][0]
    top_score = result["scores"][0]
    is_financial = (top_label == "financial discussion" and top_score >= THRESHOLD)

    print(f"mDeBERTa: {top_label} (score: {top_score:.3f})")
    return is_financial, top_score, top_label


if __name__ == "__main__":
    test_financial = (
        "Mujhe SIP start karna hai paanch hazaar monthly. "
        "Car loan ki EMI barah hazaar paanch sau hai."
    )
    test_general = "Aaj dinner mein kya banaye? Pizza ya pasta?"

    print("--- Financial test ---")
    print(classify_financial(test_financial))
    print("\n--- General test ---")
    print(classify_financial(test_general))
