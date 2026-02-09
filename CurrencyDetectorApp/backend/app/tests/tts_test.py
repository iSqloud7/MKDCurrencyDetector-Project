"""
TTS (Text-to-Speech) Testing Suite
Tests ElevenLabs Macedonian speech output
"""

import sys
import time
from pathlib import Path
import os

# Add backend/app to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from services.tts import text_to_speech


def print_test_header(test_name):
    print(f"\n{'=' * 70}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 70}")


# ===========================
# CORE TESTS
# ===========================

def test_api_key_present():
    print_test_header("API Key Presence")
    key = os.getenv("ELEVENLABS_API_KEY")
    assert key, "❌ ELEVENLABS_API_KEY not set"
    print("✅ API key found")


def test_simple_macedonian_tts():
    print_test_header("Simple Macedonian TTS")

    text = "Детектирана банкнота од сто денари"
    audio = text_to_speech(text)

    assert isinstance(audio, bytes)
    assert len(audio) > 1000  # MP3 should not be tiny

    print(f"✅ Audio generated ({len(audio)} bytes)")


def test_multiple_messages():
    print_test_header("Multiple Macedonian Messages")

    samples = [
        "Детектирана банкнота од илјада денари",
        "Детектирана монета од пет денари",
        "Детектирани три банкноти",
        "Не е детектирана валута",
    ]

    for msg in samples:
        print(f"Speaking: {msg}")
        audio = text_to_speech(msg)
        assert isinstance(audio, bytes)
        assert len(audio) > 1000
        time.sleep(0.3)

    print("✅ Multiple messages spoken successfully")


def test_failure_on_empty_text():
    print_test_header("Empty Text Handling")

    try:
        text_to_speech("")
        assert False, "Expected failure on empty text"
    except Exception:
        print("✅ Properly failed on empty text")


# ===========================
# RUNNER
# ===========================

def run_all_tests():
    test_api_key_present()
    test_simple_macedonian_tts()
    test_multiple_messages()
    test_failure_on_empty_text()

    print("\n✅ ALL TTS TESTS PASSED")


from playsound3 import playsound

def debug_play_audio():
    print("\n🔊 Playing audio locally (DEBUG)")
    audio = text_to_speech("Детектирана банкнота од сто денари")

    path = Path("debug_tts.mp3")
    path.write_bytes(audio)

    playsound(str(path))


# if __name__ == "__main__":
#     debug_play_audio()


if __name__ == "__main__":
    run_all_tests()
