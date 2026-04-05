"""
Singleton model loader — all heavy models load once at import time.
Other modules import from here instead of loading their own copies.
"""
import time

_start = time.time()
print("Loading models (one-time startup)...")

# ── Whisper (speech-to-text) ────────────────────────────────────
from faster_whisper import WhisperModel
whisper_model = WhisperModel("medium", device="cpu", compute_type="int8")
print("  Whisper ready")

# ── mDeBERTa (zero-shot classification) ─────────────────────────
from transformers import pipeline as hf_pipeline
classifier = hf_pipeline(
    "zero-shot-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
)
print("  mDeBERTa ready")

# ── GLiNER (named entity recognition) ──────────────────────────
from gliner import GLiNER
gliner_model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")
print("  GLiNER ready")

print(f"Startup complete in {time.time()-_start:.1f}s\n")
