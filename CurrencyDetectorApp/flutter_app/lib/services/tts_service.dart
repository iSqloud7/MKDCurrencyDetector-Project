import 'dart:convert';
import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';

class TtsService {
  final AudioPlayer _player = AudioPlayer();

  bool _isPlaying = false;

  /// Play ElevenLabs TTS audio (base64 MP3 from backend)
  Future<void> playFromBase64(String? base64Audio) async {
    if (base64Audio == null || base64Audio.isEmpty) {
      print("TTS: No audio received");
      return;
    }

    try {
      // Stop previous audio
      if (_isPlaying) {
        await _player.stop();
      }

      Uint8List audioBytes = base64Decode(base64Audio);

      await _player.play(
        BytesSource(audioBytes),
      );

      _isPlaying = true;
    } catch (e) {
      print("TTS playback error: $e");
    }
  }

  Future<void> stop() async {
    await _player.stop();
    _isPlaying = false;
  }

  void dispose() {
    _player.dispose();
  }
}
