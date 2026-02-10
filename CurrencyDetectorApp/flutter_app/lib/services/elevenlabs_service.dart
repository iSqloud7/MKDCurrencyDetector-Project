import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class ElevenLabsService {
  static const String _apiKey = 'ELEVENLABS_API_KEY';
  static const String _voiceId = 'EXAVITQu4vr4xnSDxMaL';

  Future<Uint8List?> speak(String? text) async {
    if (text == null || text.trim().isEmpty) {
      print('TTS skipped: empty text');
      return null;
    }

    final uri = Uri.parse(
      'https://api.elevenlabs.io/v1/text-to-speech/$_voiceId',
    );

    final response = await http.post(
      uri,
      headers: {
        'xi-api-key': _apiKey,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg',
      },
      body: jsonEncode({
        'text': text,
        'model_id': 'eleven_multilingual_v2',
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
