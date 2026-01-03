import edge_tts
import asyncio
from utils.tts import TextToSpeech
from playsound import playsound

async def list_voices():
    vm = await edge_tts.VoicesManager.create()
    for voice in vm.voices:
        if "mk-MK" in voice["ShortName"]:
            print(voice["ShortName"], "-", voice["Locale"])

asyncio.run(list_voices())

tts = TextToSpeech(language="mk")
detection_result = {
    "success": True,
    "type": "banknote",
    "detections": [{"class_name": "1000 МКД"}]
}
file_path = "temp_edge_tts.mp3"
tts.announce_detection(detection_result, save_to_file=file_path)

# Play the saved MP3
playsound(file_path)
