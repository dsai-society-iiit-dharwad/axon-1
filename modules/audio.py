import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import os

SAMPLE_RATE = 16000  # 16kHz mono — required by Whisper
CHANNELS = 1


def record_audio(duration_sec, save_path="audio_samples/recording.wav"):
    """Record from mic. Returns path to saved WAV or None on failure."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    try:
        print(f"Recording {duration_sec}s of audio...")
        audio = sd.rec(
            int(duration_sec * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16"
        )
        sd.wait()  # block until recording finishes
        print("Recording complete.")

        wav.write(save_path, SAMPLE_RATE, audio)
        print(f"Saved to {save_path}")
        return save_path

    except Exception as e:
        print(f"Mic recording failed: {e}")
        return None


def load_wav(wav_path):
    """Load a WAV file, resample to 16kHz mono if needed. Returns (samples, sample_rate)."""
    if not os.path.exists(wav_path):
        print(f"WAV file not found: {wav_path}")
        return None, None

    rate, samples = wav.read(wav_path)

    # convert stereo to mono
    if len(samples.shape) > 1:
        samples = samples.mean(axis=1).astype(samples.dtype)
        print(f"Converted stereo to mono")

    # resample if not 16kHz (simple linear interpolation — good enough for demo)
    if rate != SAMPLE_RATE:
        duration = len(samples) / rate
        new_length = int(duration * SAMPLE_RATE)
        samples = np.interp(
            np.linspace(0, len(samples) - 1, new_length),
            np.arange(len(samples)),
            samples.astype(np.float32)
        ).astype(np.int16)
        print(f"Resampled from {rate}Hz to {SAMPLE_RATE}Hz")

    duration_sec = len(samples) / SAMPLE_RATE
    print(f"Loaded {wav_path} — {duration_sec:.1f}s, {SAMPLE_RATE}Hz mono")
    return samples, SAMPLE_RATE


def get_audio(use_live_mic=False, duration_sec=120, demo_wav=None):
    """Main entry point. Tries mic first, falls back to demo WAV."""
    if use_live_mic:
        save_path = "audio_samples/recording.wav"
        result = record_audio(duration_sec, save_path)
        if result:
            return result

        # mic failed — try fallback
        print("Falling back to demo WAV...")

    if demo_wav and os.path.exists(demo_wav):
        print(f"Using demo audio: {demo_wav}")
        return demo_wav

    print("No audio source available")
    return None


if __name__ == "__main__":
    # quick test — list available audio devices
    print("Available audio devices:")
    print(sd.query_devices())
    print(f"\nDefault input: {sd.default.device[0]}")

    # test loading a wav if one exists
    test_path = "audio_samples/demo_arjun_priya.wav"
    if os.path.exists(test_path):
        samples, rate = load_wav(test_path)
    else:
        print(f"\nNo test WAV at {test_path} — that's fine for now")
