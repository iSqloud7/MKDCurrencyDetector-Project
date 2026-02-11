import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

import '../services/api_service.dart';
import '../services/tts_service.dart';
import '../services/elevenlabs_service.dart';
import '../models/detection_result.dart';
import '../widgets/capture_button.dart';

class CameraScreen extends StatefulWidget {
  final CameraDescription camera;
  const CameraScreen({super.key, required this.camera});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen>
    with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeCameraFuture;

  final ApiService _api = ApiService();
  final TtsService _tts = TtsService();
  final ElevenLabsService _elevenLabs = ElevenLabsService();

  File? _imageFile;
  bool _isLoading = false;
  String _displayText = "Насочете ја камерата кон валутата";
  DetectionResult? _lastResult;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeCamera();
    _checkApiHealth();
  }

  void _initializeCamera() {
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
      enableAudio: false,
    );
    _initializeCameraFuture = _controller.initialize();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller.dispose();
    _tts.dispose();
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_controller.value.isInitialized) return;

    if (state == AppLifecycleState.inactive) {
      _controller.dispose();
    } else if (state == AppLifecycleState.resumed) {
      _initializeCamera();
      setState(() {});
    }
  }

  // =========================
  // API HEALTH + TTS
  // =========================
  Future<void> _checkApiHealth() async {
    final isHealthy = await _api.checkHealth();

    if (!mounted) return;

    final text = isHealthy
        ? "Поврзан со серверот"
        : "Не може да се поврзе со серверот";

    debugPrint('🗣️ Health TTS: $text');

    final audio = await _elevenLabs.speak(text);
    if (audio != null && audio.isNotEmpty) {
      await _tts.playFromBytes(audio);
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(text),
        backgroundColor: isHealthy ? Colors.green : Colors.orange,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  // =========================
  // CAMERA CAPTURE
  // =========================
  Future<void> _takePicture() async {
    try {
      await _initializeCameraFuture;

      if (!_controller.value.isInitialized) {
        throw Exception('Camera not initialized');
      }

      final image = await _controller.takePicture();

      setState(() {
        _imageFile = File(image.path);
        _isLoading = true;
        _displayText = "Се обработува...";
      });

      await _processImage(_imageFile!);
    } catch (e) {
      debugPrint("Camera error: $e");

      final audio = await _elevenLabs.speak("Грешка со камерата");
      if (audio != null) {
        await _tts.playFromBytes(audio);
      }
    }
  }

  // =========================
  // IMAGE → API → TTS
  // =========================
  Future<void> _processImage(File file) async {
    DetectionResult? result;

    try {
      result = await _api.detectCurrency(file);
    } catch (e) {
      debugPrint('Detection error: $e');
    }

    if (!mounted) return;

    setState(() => _isLoading = false);

    if (result == null) {
      _displayText = "Грешка при поврзување со серверот";
    } else {
      _lastResult = result;
      _displayText = result.toDisplayText();
    }

    setState(() {});

    // 🔊 TTS PIPELINE (THIS WAS THE BUG)
    Future.microtask(() async {
      debugPrint('🗣️ Speaking: $_displayText');

      final audioBytes = await _elevenLabs.speak(_displayText);

      debugPrint('🎧 Audio bytes: ${audioBytes?.length}');

      if (audioBytes != null && audioBytes.isNotEmpty) {
        await _tts.playFromBytes(audioBytes);
      } else {
        debugPrint('❌ No audio returned');
      }
    });
  }

  void _resetCamera() {
    setState(() {
      _imageFile = null;
      _lastResult = null;
      _displayText = "Насочете ја камерата кон валутата";
    });
  }

  // =========================
  // UI
  // =========================
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.orange[50],
      appBar: AppBar(
        title: const Text('MKD Currency Detector'),
        centerTitle: true,
        backgroundColor: Colors.deepOrange,
      ),
      body: Column(
        children: [
          Expanded(
            child: _imageFile != null
                ? Image.file(_imageFile!, fit: BoxFit.contain)
                : FutureBuilder<void>(
                    future: _initializeCameraFuture,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.done &&
                          _controller.value.isInitialized) {
                        return CameraPreview(_controller);
                      }
                      return const Center(child: CircularProgressIndicator());
                    },
                  ),
          ),
          if (_isLoading)
            LinearProgressIndicator(
              color: Colors.deepOrange,
              backgroundColor: Colors.orange[100],
            ),
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.orange[100],
            child: Text(
              _displayText,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: Colors.deepOrange,
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 30),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                CaptureButton(
                  isLoading: _isLoading,
                  onPressed: _takePicture,
                ),
                IconButton(
                  icon: const Icon(Icons.refresh, size: 36),
                  color: Colors.redAccent,
                  onPressed: _resetCamera,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
