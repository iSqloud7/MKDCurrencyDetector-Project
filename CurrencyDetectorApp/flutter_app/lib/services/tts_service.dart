Future<void> playFromBytes(Uint8List audioBytes) async {
  try {
    if (_isPlaying) {
      await _player.stop();
    }

    _isPlaying = true;

    await _player.play(BytesSource(audioBytes));

    _player.onPlayerComplete.listen((_) {
      _isPlaying = false;
    });
  } catch (e) {
    _isPlaying = false;
    print("TTS playback error: $e");
  }
}
