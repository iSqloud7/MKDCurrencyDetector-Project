import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ElevenLabsService {
  static const String _voiceId = 'EXAVITQu4vr4xnSDxMaL';

  Future<Uint8List?> speak(String? text) async {
    if (text == null || text.trim().isEmpty) {
      print('TTS skipped: empty text');
      return null;
    }

    final apiKey = dotenv.env['ELEVENLABS_API_KEY'];

    if (apiKey == null) {
      print('❌ API key not found in .env');
      return null;
    }

    final uri = Uri.parse(
      'https://api.elevenlabs.io/v1/text-to-speech/$_voiceId',
    );

    final response = await http.post(
      uri,
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg',
      },
      body: jsonEncode({
        'text': text,
        'model_id': 'eleven_v3',
        'voice_settings': {
          'stability': 0.5,   // колку гласот е стабилен (0-1)
          'similarity_boost': 0.8, // колку да личи на voice sample (0-1)
          'rate': 0.7, // 🐢 забавување на говорот, 1.0 = нормална брзина
          // 'pitch': 1.0, // можеш да промениш и висина ако сакаш
          // 'volume': 1.0,
        },
      }),
    );


    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      print('❌ ElevenLabs error ${response.statusCode}');
      print(response.body);
      return null;
    }
  }
}
