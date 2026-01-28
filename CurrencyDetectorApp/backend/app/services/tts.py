import asyncio
import time
from typing import Optional, Dict, Any
from pathlib import Path
from playsound3 import playsound

# Директориум за аудио фајлови
AUDIO_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "audio"
AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Модул кој гласно ја соопштува детектиранта валута, според резултатот од детекцијата
class TextToSpeech:
    # Сите македонски валути
    MKD_CURRENCY_NAMES = {
        "2000_note": "две илјади денари",
        "1000_note": "илјада денари",
        "500_note": "петстотини денари",
        "200_note": "двесте денари",
        "100_note": "сто денари",
        "50_note": "педесет денари",
        "10_note": "десет денари",
        "50_coin": "педесет денари",
        "10_coin": "десет денари",
        "5_coin": "пет денари",
        "2_coin": "два денари",
        "1_coin": "еден денар",
    }

    def __init__(self, language: str = "mk"):
        self.language = language
        self.voice = "mk-MK-MarijaNeural" if language == "mk" else "en-US-GuyNeural"

    # Зборување - Креира уникатер MP3 фајл
    # Преку _save_tts го генерира говорот
    # Го враќа звукот (playsound) и доколку е успешно враќа True
    def speak(self, text: str, voice: Optional[str] = None) -> bool:
        voice = voice or self.voice
        try:
            filename = AUDIO_OUTPUT_DIR / f"tts_{int(time.time() * 1000)}.mp3"
            asyncio.run(self._save_tts(text, voice, filename))
            playsound(str(filename))
            return True
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return False

    async def _save_tts(self, text: str, voice: str, filename: Path):
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(filename))

    # Доколку нема детекција - изговара „Не е детектирана валута!“,
    # Доколку има детекција го зема првиот објект. оној што најдбро е детектиран,
    # Го претвора во природен говор, Прави разлика меѓу банкнота и монета и генерира реченица
    def generate_currency_message(self, detection_result: dict) -> str:
        detections = detection_result.get("detections", [])
        if not detections:
            return "Не е детектирана валута!" if self.language == "mk" else "No currency detected!"

        det_class = detections[0]["class_name"]
        det_name = self.MKD_CURRENCY_NAMES.get(det_class, det_class.replace("_", " ").rsplit(" ", 1)[0])
        count = len(detections)

        if det_class.endswith("note"):
            type_str = "банкнота" if self.language == "mk" else "banknote"
        elif det_class.endswith("coin"):
            type_str = "монета" if self.language == "mk" else "coin"
        else:
            type_str = "валута" if self.language == "mk" else "currency"

        if count == 1:
            return f"Детектирана {type_str}: {det_name}" if self.language == "mk" else f"Detected {type_str}: {det_name}"
        else:
            return f"Детектирани {count} {type_str}" if self.language == "mk" else f"Detected {count} {type_str}s"

    def announce_detection(self, detection_result: Dict[str, Any], filename: Optional[Path] = None, play_audio: bool = True) -> bool:
        message = self.generate_currency_message(detection_result)
        print(f"TTS: {message}")
        if filename:
            try:
                asyncio.run(self._save_tts(message, self.voice, filename))
            except Exception as e:
                print(f"Edge TTS error saving to file: {e}")
                return False
        if play_audio:
            return self.speak(message)
        return True

# Singleton pattern
_tts_instance: Optional[TextToSpeech] = None

def get_tts(language: str = "mk") -> TextToSpeech:
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech(language=language)
    return _tts_instance
