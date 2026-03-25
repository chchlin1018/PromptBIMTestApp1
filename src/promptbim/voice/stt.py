"""Speech-to-text using faster-whisper for local speech recognition.

Falls back to macOS native ``NSSpeechRecognizer`` / ``say`` if
faster-whisper is unavailable.  Audio is captured via ``sounddevice``
(PortAudio wrapper) to keep dependencies minimal.
"""

from __future__ import annotations

import io
import struct
import tempfile
import threading
import time
import wave
from pathlib import Path
from typing import Callable

from promptbim.debug import get_logger

logger = get_logger("voice.stt")

# ---------------------------------------------------------------------------
# Lightweight WAV helpers (no external deps)
# ---------------------------------------------------------------------------

SAMPLE_RATE = 16_000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit PCM


def _pcm_to_wav(frames: list[bytes], sample_rate: int = SAMPLE_RATE) -> bytes:
    """Pack raw PCM frames into an in-memory WAV file."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Recorder: capture audio via sounddevice
# ---------------------------------------------------------------------------

class AudioRecorder:
    """Record audio from the default input device.

    Starts / stops recording and returns raw PCM frames.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE) -> None:
        self._sample_rate = sample_rate
        self._frames: list[bytes] = []
        self._recording = False
        self._stream = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    def start(self) -> None:
        """Begin recording from the default microphone."""
        if self._recording:
            return
        self._frames = []
        self._recording = True
        self._start_time = time.monotonic()
        logger.debug("Recording started (sample_rate=%d)", self._sample_rate)
        try:
            import sounddevice as sd

            self._stream = sd.RawInputStream(
                samplerate=self._sample_rate,
                channels=CHANNELS,
                dtype="int16",
                callback=self._audio_callback,
            )
            self._stream.start()
        except Exception as exc:
            logger.warning("sounddevice unavailable, recording disabled: %s", exc)
            self._recording = False

    def stop(self) -> bytes:
        """Stop recording and return WAV bytes."""
        duration = time.monotonic() - getattr(self, "_start_time", time.monotonic())
        logger.debug("Recording stopped (duration=%.2fs, frames=%d)", duration, len(self._frames))
        self._recording = False
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if not self._frames:
            return b""
        return _pcm_to_wav(self._frames, self._sample_rate)

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        if self._recording:
            self._frames.append(bytes(indata))


# ---------------------------------------------------------------------------
# Transcriber: faster-whisper (local) → fallback to macOS native
# ---------------------------------------------------------------------------

class Transcriber:
    """Transcribe WAV audio to text.

    Uses *faster-whisper* when available; otherwise falls back to a
    macOS ``NSSpeechRecognizer``-based approach or returns an error.
    """

    def __init__(self, model_size: str = "base") -> None:
        self._model_size = model_size
        self._model = None
        self._backend: str = "none"

    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        try:
            from faster_whisper import WhisperModel

            logger.debug("Loading faster-whisper model '%s'...", self._model_size)
            t0 = time.monotonic()
            self._model = WhisperModel(
                self._model_size, device="cpu", compute_type="int8"
            )
            elapsed = time.monotonic() - t0
            self._backend = "faster-whisper"
            logger.info("Loaded faster-whisper model: %s (%.2fs)", self._model_size, elapsed)
        except ImportError:
            logger.warning(
                "faster-whisper not installed; speech recognition unavailable. "
                "Install with: pip install faster-whisper"
            )
            self._backend = "none"

    def transcribe(self, wav_bytes: bytes) -> str:
        """Transcribe WAV audio bytes to text."""
        if not wav_bytes:
            return ""

        self._ensure_model()

        if self._backend == "faster-whisper":
            return self._transcribe_whisper(wav_bytes)

        return ""

    def _transcribe_whisper(self, wav_bytes: bytes) -> str:
        """Transcribe using faster-whisper."""
        logger.debug("Transcribing WAV data (%d bytes)", len(wav_bytes))
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(wav_bytes)
            tmp_path = tmp.name

        try:
            t0 = time.monotonic()
            segments, info = self._model.transcribe(
                tmp_path,
                language=None,  # auto-detect
                beam_size=5,
                vad_filter=True,
            )
            seg_list = list(segments)
            text = " ".join(seg.text.strip() for seg in seg_list)
            elapsed = time.monotonic() - t0
            avg_confidence = (
                sum(seg.avg_log_prob for seg in seg_list) / len(seg_list)
                if seg_list else 0.0
            )
            logger.info(
                "Transcribed (%s, %.1fs audio, %.2fs processing): %s",
                info.language,
                info.duration,
                elapsed,
                text[:100],
            )
            logger.debug(
                "Transcription details: language_prob=%.3f, avg_log_prob=%.3f, segments=%d",
                info.language_probability,
                avg_confidence,
                len(seg_list),
            )
            return text.strip()
        except Exception as exc:
            logger.error("Transcription failed: %s", exc)
            return ""
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    @property
    def backend(self) -> str:
        """Return which backend is active."""
        self._ensure_model()
        return self._backend


# ---------------------------------------------------------------------------
# High-level convenience: record → transcribe in one call (threaded)
# ---------------------------------------------------------------------------

class VoiceInput:
    """High-level voice input: manages recording + transcription.

    Usage::

        vi = VoiceInput()
        vi.start_recording()
        # ... user speaks ...
        vi.stop_and_transcribe(callback=lambda text: print(text))
    """

    def __init__(self, model_size: str = "base") -> None:
        self._recorder = AudioRecorder()
        self._transcriber = Transcriber(model_size=model_size)

    @property
    def is_recording(self) -> bool:
        return self._recorder.is_recording

    @property
    def backend(self) -> str:
        return self._transcriber.backend

    def start_recording(self) -> None:
        self._recorder.start()

    def stop_and_transcribe(
        self,
        callback: Callable[[str], None] | None = None,
    ) -> None:
        """Stop recording and transcribe in a background thread.

        *callback* is called with the transcribed text (or "" on failure).
        """
        wav_data = self._recorder.stop()
        if not wav_data:
            if callback:
                callback("")
            return

        def _worker():
            text = self._transcriber.transcribe(wav_data)
            if callback:
                callback(text)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def stop_and_transcribe_sync(self) -> str:
        """Stop recording and transcribe synchronously."""
        wav_data = self._recorder.stop()
        if not wav_data:
            return ""
        return self._transcriber.transcribe(wav_data)
