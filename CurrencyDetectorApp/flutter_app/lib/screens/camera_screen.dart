import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../services/api_service.dart';
import '../services/tts_service.dart';
import '../models/detection_result.dart';
import '../widgets/capture_button.dart';

// Екран за камера и детекција на валута
// оваа класа претставува StatefulWidget бидејќи и се менува состојбата
// како на пример: стартување на камера, сликање, чекање на серверот
// прикажување на резултат и tts
class CameraScreen extends StatefulWidget {
  final CameraDescription camera;
  const CameraScreen({super.key, required this.camera});
  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

// Состојба која преку WidgetsBindingObserver овозможува да следиме life
// Односно апликацијата оди во позадина па се враќа
class _CameraScreenState extends State<CameraScreen> with WidgetsBindingObserver {
  late CameraController _controller;
  late Future<void> _initializeCameraFuture;

  final ApiService _api = ApiService();
  final TtsService _tts = TtsService();

  File? _imageFile;
  bool _isLoading = false;
  String _displayText = "Насочете ја камерата кон валутата";
  DetectionResult? _lastResult;

// Оваа состојба се случува само еднаш, при отварањето на камерата
// Во тој момент се регистрира life-cycle listener
// Се иницијализира камерата и се проверува достапност на серверот
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeCamera();
    _checkApiHealth();
  }
// Користи задна камера со висока резолуција и без аудио
  void _initializeCamera() {
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
      enableAudio: false,
    );
    _initializeCameraFuture = _controller.initialize();
  }

  // Се исклучува камерата, се ослободува TTS и нема memory leaks
  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _controller.dispose();
    _tts.dispose();
    super.dispose();
  }

    // Life-cycle менаџмент, односно кога апликацијата оди во позадина - се исклучува
    // па се враќа - се ре-иницијализира
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

  Future<void> _checkApiHealth() async {
    final isHealthy = await _api.checkHealth();
    if (!isHealthy && mounted) {
      _tts.speak("Не може да се поврзе со серверот");
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Не може да се поврзе со серверот'),
          backgroundColor: Colors.orange,
        ),
      );
    } else if (mounted) {
      _tts.speak("Поврзан со серверот");
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Поврзан со серверот'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 2),
        ),
      );
    }
  }

// Чека да се иницијализира камерата, слика,
// ја зачувува сликата како File, приказ на „Се обработува...“
// ја праќа сликата до серверот
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
      debugPrint("Camera capture error: $e");
      if (mounted) {
        _tts.speak("Грешка со камерата");
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Грешка со камерата: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _processImage(File file) async {
    DetectionResult? result;
    try {
      result = await _api.detectCurrency(file);
    } catch (e) {
      debugPrint('Error detecting currency: $e');
      result = null;
    }
    if (!mounted) return;
    setState(() => _isLoading = false);
    if (result != null) {
      _lastResult = result;
      _displayText = result.toDisplayText();

      Future.microtask(() => _tts.speak(_displayText));

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result.success ? 'Детекција успешна' : 'Не е пронајдена валута'),
          backgroundColor: result.success ? Colors.green : Colors.red,
          duration: const Duration(seconds: 2),
        ),
      );
    } else {
      _displayText = "Грешка при поврзување со серверот";
      Future.microtask(() => _tts.speak(_displayText));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Не може да се поврзе со серверот'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _resetCamera() {
    setState(() {
      _imageFile = null;
      _lastResult = null;
      _displayText = "Насочете ја камерата кон валутата";
    });
  }

  @override
  Widget build(BuildContext context) {
  // Портокалова позадина, AppBar со наслов
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
                ? Stack(
              children: [
                Image.file(
                  _imageFile!,
                  fit: BoxFit.contain,
                  width: double.infinity,
                ),
                if (_lastResult != null && _lastResult!.success)
                  Positioned(
                    top: 16,
                    right: 16,
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Colors.deepOrange,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${_lastResult!.count} детекција',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                  ),
              ],
            )
            // Доколку нема слика, пркажува CameraPreview или loader
                : FutureBuilder<void>(
              future: _initializeCameraFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.done) {
                  if (_controller.value.isInitialized) {
                    return CameraPreview(_controller);
                  } else {
                    return const Center(
                      child: Text('Камерата не е достапна', style: TextStyle(fontSize: 18)),
                    );
                  }
                } else {
                  return const Center(child: CircularProgressIndicator());
                }
              },
            ),
          ),
          // Му кажува на корисникот дека се обработува
          if (_isLoading)
            LinearProgressIndicator(
              color: Colors.deepOrange,
              backgroundColor: Colors.orange[100],
            ),
            // Со _displayText го прикажува текстот
          Container(
            padding: const EdgeInsets.all(16.0),
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
            padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 20),
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
