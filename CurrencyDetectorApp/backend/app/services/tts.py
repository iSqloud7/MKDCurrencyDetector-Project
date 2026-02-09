# import os
# import time
# import requests
# from pathlib import Path
# from typing import Optional, Dict, Any
#
# # =========================
# # CONFIG
# # =========================
#
# ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
#
# # Free-tier compatible model
# ELEVEN_MODEL = "eleven_turbo_v2"
#
# # Pick ONE voice (works well for Slavic languages)
# VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (most stable)
#
# AUDIO_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "audio"
# AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
#
# # =========================
# # TTS CLASS
# # =========================
#
# class TextToSpeech:
#     MKD_CURRENCY_NAMES = {
#         "2000_note": "две илјади денари",
#         "1000_note": "илјада денари",
#         "500_note": "петстотини денари",
#         "200_note": "двесте денари",
#         "100_note": "сто денари",
#         "50_note": "педесет денари",
#         "10_note": "десет денари",
#         "50_coin": "педесет денари",
#         "10_coin": "десет денари",
#         "5_coin": "пет денари",
#         "2_coin": "два денари",
#         "1_coin": "еден денар",
#     }
#
#     def __init__(self, language: str = "mk"):
#         self.language = language
#
#     # =========================
#     # ELEVENLABS CORE
#     # =========================
#     def speak(self, text: str, filename: Optional[Path] = None) -> bytes:
#         if not ELEVENLABS_API_KEY:
#             raise RuntimeError("ELEVENLABS_API_KEY not set")
#
#         url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
#         headers = {
#             "xi-api-key": ELEVENLABS_API_KEY,
#             "Content-Type": "application/json",
#             "Accept": "audio/mpeg",
#         }
#
#         payload = {
#             "text": text,
#             "model_id": ELEVEN_MODEL,
#             "voice_settings": {
#                 "stability": 0.55,
#                 "similarity_boost": 0.65,
#             },
#         }
#
#         response = requests.post(url, json=payload, headers=headers)
#         if response.status_code != 200:
#             raise RuntimeError(f"ElevenLabs error: {response.text}")
#
#         audio_bytes = response.content
#
#         if filename:
#             filename.write_bytes(audio_bytes)
#
#         return audio_bytes
#
#     # =========================
#     # MESSAGE GENERATION
#     # =========================
#     def generate_currency_message(self, detection_result: dict) -> str:
#         detections = detection_result.get("detections", [])
#
#         if not detections:
#             return "Не е детектирана валута!"
#
#         det_class = detections[0]["class_name"]
#         det_name = self.MKD_CURRENCY_NAMES.get(
#             det_class, det_class.replace("_", " ")
#         )
#
#         count = len(detections)
#
#         if det_class.endswith("note"):
#             type_str = "банкнота"
#         elif det_class.endswith("coin"):
#             type_str = "монета"
#         else:
#             type_str = "валута"
#
#         if count == 1:
#             return f"Детектирана {type_str}: {det_name}"
#         else:
#             return f"Детектирани {count} {type_str}"
#
#     # =========================
#     # FULL PIPELINE
#     # =========================
#     def announce_detection(
#         self,
#         detection_result: Dict[str, Any],
#         filename: Optional[Path] = None,
#     ) -> bytes:
#         message = self.generate_currency_message(detection_result)
#         print(f"TTS: {message}")
#
#         if not filename:
#             filename = AUDIO_OUTPUT_DIR / f"tts_{int(time.time() * 1000)}.mp3"
#
#         return self.speak(message, filename=filename)
#
#
# # =========================
# # SINGLETON
# # =========================
#
# _tts_instance: Optional[TextToSpeech] = None
#
# def get_tts(language: str = "mk") -> TextToSpeech:
#     global _tts_instance
#     if _tts_instance is None:
#         _tts_instance = TextToSpeech(language)
#     return _tts_instance


import os
import requests
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # good default
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

def text_to_speech(text: str) -> bytes:
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.7
        }
    }

    response = requests.post(ELEVENLABS_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise RuntimeError(f"ElevenLabs error: {response.text}")

    return response.content
