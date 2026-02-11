Future<void> playFromBytes(Uint8List audioBytes) async {
  try {
    if (audioBytes.isEmpty) {
      print('❌ TTS: empty audio');
      return;
    }

    print('🔊 Playing TTS (${audioBytes.length} bytes)');

    await _player.setAudioContext(
      AudioContext(
        android: AudioContextAndroid(
          isSpeakerphoneOn: true,
          stayAwake: true,
          contentType: AndroidContentType.speech,
          usageType: AndroidUsageType.media,
          audioFocus: AndroidAudioFocus.gain,
        ),
      ),
    );

    if (_isPlaying) {
      await _player.stop();
    }

    _isPlaying = true;
    await _player.play(BytesSource(audioBytes));
  } catch (e) {
    _isPlaying = false;
    print("❌ TTS playback error: $e");
  }
}
