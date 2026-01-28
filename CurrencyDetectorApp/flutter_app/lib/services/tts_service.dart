import 'package:flutter_tts/flutter_tts.dart';

// Сервис за звучно читање на детекцијата
class TtsService {
  final FlutterTts _tts = FlutterTts();
  bool _isInitialized = false;

  TtsService() {
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      // Поставување на јазик
      // Доколку има македонски, ако не успее користи англиски
      for (var code in ['mk-MK', 'mk', 'en-US']) {
        var result = await _tts.setLanguage(code);
        print("Setting TTS language $code: result $result");
        if (result == 1) break;
      }

      await _tts.setSpeechRate(0.45);
      await _tts.setVolume(1.0);
      await _tts.setPitch(1.0);

      await _tts.awaitSpeakCompletion(true);

      _isInitialized = true;
      print("TTS Initialized");
    } catch (e) {
      _isInitialized = false;
      print('TTS init error: $e');
    }
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) await _initialize();
    try {
      await _tts.stop();
      await Future.delayed(const Duration(milliseconds: 50));
      await _tts.speak(text);
    } catch (e) {
      print('TTS speak error: $e');
    }
  }

  void dispose() {
    _tts.stop();
  }
}
