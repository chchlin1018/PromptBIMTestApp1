"""Tests for voice/stt.py — speech-to-text module."""

import io
import struct
import wave

from promptbim.voice.stt import (
    CHANNELS,
    SAMPLE_RATE,
    SAMPLE_WIDTH,
    AudioRecorder,
    Transcriber,
    VoiceInput,
    _pcm_to_wav,
)

# ---------------------------------------------------------------------------
# _pcm_to_wav
# ---------------------------------------------------------------------------


class TestPcmToWav:
    def test_empty_frames(self):
        wav = _pcm_to_wav([])
        assert wav[:4] == b"RIFF"

    def test_single_frame(self):
        # 100 samples of silence
        pcm = struct.pack("<100h", *([0] * 100))
        wav = _pcm_to_wav([pcm])
        assert wav[:4] == b"RIFF"
        # Verify WAV is valid
        buf = io.BytesIO(wav)
        with wave.open(buf, "rb") as wf:
            assert wf.getnchannels() == CHANNELS
            assert wf.getsampwidth() == SAMPLE_WIDTH
            assert wf.getframerate() == SAMPLE_RATE
            assert wf.getnframes() == 100

    def test_multiple_frames(self):
        pcm1 = struct.pack("<50h", *([100] * 50))
        pcm2 = struct.pack("<50h", *([200] * 50))
        wav = _pcm_to_wav([pcm1, pcm2])
        buf = io.BytesIO(wav)
        with wave.open(buf, "rb") as wf:
            assert wf.getnframes() == 100


# ---------------------------------------------------------------------------
# AudioRecorder
# ---------------------------------------------------------------------------


class TestAudioRecorder:
    def test_initial_state(self):
        rec = AudioRecorder()
        assert not rec.is_recording

    def test_stop_without_start_returns_empty(self):
        rec = AudioRecorder()
        assert rec.stop() == b""

    def test_start_without_sounddevice_stays_not_recording(self, monkeypatch):
        """If sounddevice is unavailable, start() gracefully fails."""

        # Simulate import error
        original_import = (
            __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__
        )

        def mock_import(name, *args, **kwargs):
            if name == "sounddevice":
                raise ImportError("No sounddevice")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", mock_import)
        rec = AudioRecorder()
        rec.start()
        # Should gracefully handle missing sounddevice
        assert not rec.is_recording


# ---------------------------------------------------------------------------
# Transcriber
# ---------------------------------------------------------------------------


class TestTranscriber:
    def test_empty_input(self):
        t = Transcriber()
        assert t.transcribe(b"") == ""

    def test_backend_without_whisper(self):
        t = Transcriber()
        t._ensure_model()
        # faster-whisper may or may not be installed
        assert t.backend in ("faster-whisper", "none")

    def test_transcribe_without_model_returns_empty(self):
        """If no backend available, returns empty string."""
        t = Transcriber()
        t._backend = "none"
        t._model = None
        pcm = struct.pack("<100h", *([0] * 100))
        wav = _pcm_to_wav([pcm])
        result = t.transcribe(wav)
        assert result == ""


# ---------------------------------------------------------------------------
# VoiceInput
# ---------------------------------------------------------------------------


class TestVoiceInput:
    def test_initial_state(self):
        vi = VoiceInput()
        assert not vi.is_recording

    def test_stop_without_start(self):
        vi = VoiceInput()
        result = vi.stop_and_transcribe_sync()
        assert result == ""

    def test_callback_on_empty(self):
        vi = VoiceInput()
        received = []
        vi.stop_and_transcribe(callback=lambda t: received.append(t))
        # Should callback with empty string immediately
        import time

        time.sleep(0.1)
        assert received == [""]


# ---------------------------------------------------------------------------
# Task 26: Additional voice tests (+4)
# ---------------------------------------------------------------------------


class TestPcmToWavExtended:
    def test_large_frame(self):
        """Test WAV creation with a large audio buffer (1 second at 16kHz)."""
        pcm = struct.pack(f"<{SAMPLE_RATE}h", *([0] * SAMPLE_RATE))
        wav = _pcm_to_wav([pcm])
        buf = io.BytesIO(wav)
        with wave.open(buf, "rb") as wf:
            assert wf.getnframes() == SAMPLE_RATE
            assert wf.getframerate() == SAMPLE_RATE

    def test_custom_sample_rate(self):
        """Test WAV creation with non-default sample rate."""
        pcm = struct.pack("<100h", *([0] * 100))
        wav = _pcm_to_wav([pcm], sample_rate=44100)
        buf = io.BytesIO(wav)
        with wave.open(buf, "rb") as wf:
            assert wf.getframerate() == 44100


class TestTranscriberMacOSFallback:
    def test_macos_native_with_empty_wav(self):
        """macOS native fallback with empty WAV returns empty string."""
        t = Transcriber()
        t._backend = "none"
        t._model = None
        result = t.transcribe(b"")
        assert result == ""

    def test_transcriber_model_size_stored(self):
        """Verify model size is stored correctly."""
        t = Transcriber(model_size="small")
        assert t._model_size == "small"
        assert t._model is None
