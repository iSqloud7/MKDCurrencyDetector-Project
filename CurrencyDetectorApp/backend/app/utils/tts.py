import asyncio
import time
import edge_tts
from typing import Optional, Dict, Any
from playsound import playsound

class TextToSpeech:
    def __init__(self, language: str = "mk"):
        self.language = language
        self.voice = "mk-MK-MarijaNeural" if language == "mk" else "en-US-GuyNeural"

    def speak(self, text: str, voice: Optional[str] = None) -> bool:
        voice = voice or self.voice
        try:
            filename = f"tts_{int(time.time() * 1000)}.mp3"  # unique file
            asyncio.run(edge_tts.Communicate(text, voice).save(filename))
            playsound(filename)
            return True
        except Exception as e:
            print(f"❌ Edge TTS error: {e}")
            return False

    def generate_currency_message(self, detection_result: dict) -> str:
        MKD_CURRENCY_NAMES = {
            "10_note": "10 денари",
            "50_note": "50 денари",
            "5_coin": "5 денари",
            "1_coin": "1 денар"
        }

        detections = detection_result.get("detections", [])
        if not detections:
            return "Не е детектирана валута" if self.language == "mk" else "No currency detected"

        det_name = detections[0]["class_name"].replace("_", " ")
        if det_name.endswith("note"):
            type_str = "банкнота" if self.language == "mk" else "banknote"
        elif det_name.endswith("coin"):
            type_str = "монета" if self.language == "mk" else "coin"
        else:
            type_str = "валута" if self.language == "mk" else "currency"

        # Map class name to readable MKD currency
        det_name = MKD_CURRENCY_NAMES.get(detections[0]["class_name"], det_name.rsplit(" ", 1)[0])

        count = len(detections)
        if count == 1:
            return f"Детектирана {type_str}: {det_name}" if self.language == "mk" else f"Detected {type_str}: {det_name}"
        else:
            return f"Детектирани {count} {type_str}и" if self.language == "mk" else f"Detected {count} {type_str}s"

    def announce_detection(self, detection_result: Dict[str, Any]) -> bool:
        message = self.generate_currency_message(detection_result)
        print(f"🔊 TTS: {message}")
        return self.speak(message)

_tts_instance: TextToSpeech = None

def get_tts(language: str = "mk") -> TextToSpeech:
    """Return a singleton TTS instance"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech(language=language)
    return _tts_instance