import 'dart:typed_data';
import 'package:audioplayers/audioplayers.dart';

class TtsService {
  final AudioPlayer _player = AudioPlayer();
  bool _isPlaying = false;

  Future<void> playFromBytes(Uint8List audioBytes) async {
    try {
      if (audioBytes.isEmpty) {
        print('❌ TTS: audioBytes is empty');
        return;
      }

      print('🔊 TTS bytes received: ${audioBytes.length}');

      if (_isPlaying) {
        await _player.stop();
        _isPlaying = false;
      }

      _isPlaying = true;

      await _player.play(
        BytesSource(audioBytes),
        volume: 1.0,
      );

      _player.onPlayerComplete.listen((_) {
        _isPlaying = false;
        print('✅ TTS playback completed');
      });
    } catch (e, stack) {
      _isPlaying = false;
      print('❌ TTS playback error: $e');
      print(stack);
    }
  }

  Future<void> dispose() async {
    await _player.dispose();
  }
}
