import requests
import json
import re

# ── Local Backend (Ollama) ──────────────────────────────────────
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

# ── Cloud Backend (Groq — free, fast) ───────────────────────────
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are a financial intelligence assistant analyzing a conversation
between Indian speakers. There may be 2 or more speakers.
You will receive a transcript with speaker labels and extracted
financial entities.

CRITICAL RULES:
1. ALL text output MUST be in English. Translate any Hindi/Hinglish to English.
2. ALL financial amounts MUST use Indian Rupees (₹). NEVER use Dollars ($). If no currency is spoken, assume Rupees (₹).

Output ONLY valid JSON. No explanation. No markdown. No preamble.
No trailing text after the closing brace.

Output format:
{
  "commitments": [
    {"speaker": "Speaker 1", "commitment": "description"}
  ],
  "pending_decisions": ["description"],
  "financial_snapshot": {
    "instruments": ["SIP", "car loan"],
    "amounts": ["₹2,000/month", "₹12,500 EMI"],
    "timelines": ["by March", "18 months remaining"]
  },
  "speaker_sentiments": [
    {"speaker": "Speaker 1", "sentiment": "cautious", "reasoning": "one line"}
  ],
  "risk_score": 0-100,
  "risk_label": "Low" or "Medium" or "High",
  "risk_reasoning": "one sentence explaining the score"
}

Risk scoring rules (apply in order, add scores):
  Base score = 0
  Active loan or EMI present → add 25
  New investment planned while loan active → add 20
  Emergency fund below 3 months expenses → add 20
  Emergency fund below 6 months expenses → add 10
  Multiple financial commitments in one conversation → add 10
  Only savings discussion, no debt → subtract 20

  Final: below 40 = Low, 40-70 = Medium, above 70 = High
""".strip()

FALLBACK_SUMMARY = {
    "commitments": [],
    "pending_decisions": [],
    "financial_snapshot": {
        "instruments": [],
        "amounts": [],
        "timelines": []
    },
    "risk_score": 0,
    "risk_label": "Low",
    "risk_reasoning": "Could not generate summary"
}


def build_prompt(transcript, entities):
    """Build the user prompt with transcript + entities."""
    entity_text = ""
    if entities:
        entity_lines = []
        for e in entities:
            label = e.get("short_label", e.get("label", "ENTITY"))
            normalized = e.get("normalized", e["text"])
            entity_lines.append(f"  [{label}] {e['text']} → {normalized}")
        entity_text = "\nExtracted entities:\n" + "\n".join(entity_lines)

    return f"Transcript:\n{transcript}\n{entity_text}"


def generate_summary(transcript, entities, st_placeholder=None,
                     backend="local", groq_api_key=""):
    """Generate summary. backend='local' (Ollama) or 'cloud' (Groq API)."""
    prompt = build_prompt(transcript, entities)

    try:
        if backend == "cloud" and groq_api_key:
            raw_text = _call_groq(prompt, groq_api_key, st_placeholder)
        else:
            raw_text = _call_ollama(prompt, st_placeholder)

        return _parse_json_response(raw_text)

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to LLM backend.")
        return FALLBACK_SUMMARY.copy()
    except requests.exceptions.Timeout:
        print("ERROR: LLM timed out.")
        return FALLBACK_SUMMARY.copy()
    except Exception as e:
        print(f"LLM error: {e}")
        return FALLBACK_SUMMARY.copy()


def _call_ollama(prompt, st_placeholder=None):
    """🔒 Local: Ollama — data never leaves your machine."""
    use_stream = st_placeholder is not None
    print(f"Calling Ollama ({OLLAMA_MODEL}) [LOCAL]{'  [streaming]' if use_stream else ''}...")

    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt,
              "system": SYSTEM_PROMPT, "stream": use_stream},
        timeout=300, stream=use_stream
    )
    response.raise_for_status()

    if use_stream:
        raw_text = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                token = chunk.get("response", "")
                raw_text += token
                st_placeholder.code(raw_text, language="json")
                if chunk.get("done", False):
                    break
    else:
        raw_text = response.json().get("response", "")

    print(f"Ollama responded ({len(raw_text)} chars)")
    return raw_text


def _call_groq(prompt, api_key, st_placeholder=None):
    """⚡ Cloud: Groq API — fast but data goes to cloud."""
    use_stream = st_placeholder is not None
    print(f"Calling Groq ({GROQ_MODEL}) [CLOUD]{'  [streaming]' if use_stream else ''}...")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 1500,
        "stream": use_stream
    }

    response = requests.post(GROQ_URL, headers=headers, json=payload,
                             timeout=30, stream=use_stream)
    response.raise_for_status()

    if use_stream and st_placeholder:
        raw_text = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data: "):
                    data = line_str[6:]
                    if data.strip() == "[DONE]":
                        break
                    chunk = json.loads(data)
                    token = chunk["choices"][0]["delta"].get("content", "")
                    raw_text += token
                    st_placeholder.code(raw_text, language="json")
    else:
        raw_text = response.json()["choices"][0]["message"]["content"]

    print(f"Groq responded ({len(raw_text)} chars)")
    return raw_text


def _parse_json_response(raw_text):
    """Try to parse JSON from Ollama response. Handles markdown wrapping."""
    # try direct parse first
    try:
        return json.loads(raw_text.strip())
    except json.JSONDecodeError:
        pass

    # try markdown code block
    json_match = re.search(r'```(?:json)?\s*(.*?)```', raw_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # try finding first { to last }
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(raw_text[start:end + 1])
        except json.JSONDecodeError:
            pass

    print("WARNING: Could not parse Ollama response as JSON")
    print(f"  Raw response: {raw_text[:200]}...")
    return FALLBACK_SUMMARY.copy()


if __name__ == "__main__":
    test_transcript = """Speaker 1: I want to start a SIP of 5000 monthly.
Speaker 2: But you have a car loan EMI of 12500, 18 months remaining.
Speaker 1: I'll start with 2000 then, by March."""

    test_entities = [
        {"text": "SIP", "short_label": "INSTRUMENT", "normalized": "SIP"},
        {"text": "5000", "short_label": "AMOUNT", "normalized": "₹5,000"},
        {"text": "12500", "short_label": "AMOUNT", "normalized": "₹12,500"},
    ]

    summary = generate_summary(test_transcript, test_entities)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
