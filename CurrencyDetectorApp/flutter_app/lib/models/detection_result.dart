// Го претставува целосниот резултат од детекцијата
class DetectionResult {
  final bool success;
  final String? type;
  final List<Detection> detections;
  final int count;
  final String? message;

  // 🔊 ElevenLabs base64 MP3 audio from backend
  final String? ttsAudio;

  DetectionResult({
    required this.success,
    this.type,
    required this.detections,
    required this.count,
    this.message,
    this.ttsAudio,
  });

  // Зема JSON објект и го претвора во DetectionResult објект
  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      success: json['success'] ?? false,
      type: json['type'],
      detections: (json['detections'] as List<dynamic>?)
              ?.map((e) => Detection.fromJson(e))
              .toList() ??
          [],
      count: json['count'] ?? 0,
      message: json['message'],
      ttsAudio: json['tts_audio'], // 👈 IMPORTANT
    );
  }

  // 🖥️ UI text only (NOT for audio)
  String toDisplayText() {
    if (!success || detections.isEmpty) {
      return message ?? "Не е детектирана валута";
    }

    if (detections.length == 1) {
      final det = detections.first;
      final currencyName = _formatCurrencyName(det.className);
      final typeText = type == 'coin' ? 'монета' : 'банкнота';
      final confidence = (det.confidence * 100).toStringAsFixed(0);
      return 'Детектирана $typeText: $currencyName ($confidence% сигурност)';
    } else {
      final typeText = type == 'coin' ? 'монети' : 'банкноти';
      return 'Детектирани ${detections.length} $typeText';
    }
  }

  // Преведување на името на класата во македонско име
  String _formatCurrencyName(String className) {
    final Map<String, String> currencyMap = {
      '10_note': 'десет денари',
      '50_note': 'педесет денари',
      '100_note': 'сто денари',
      '200_note': 'двесте денари',
      '500_note': 'петстотини денари',
      '1000_note': 'илјада денари',
      '2000_note': 'две илјади денари',
      '1_coin': 'еден денар',
      '2_coin': 'два денари',
      '5_coin': 'пет денари',
      '10_coin': 'десет денари',
      '50_coin': 'педесет денари',
    };
    return currencyMap[className] ?? className.replaceAll('_', ' ');
  }
}

// ==============================
// SINGLE DETECTION
// ==============================
class Detection {
  final int id;
  final String className;
  final double confidence;
  final List<double> bbox;
  final String? image;

  Detection({
    required this.id,
    required this.className,
    required this.confidence,
    required this.bbox,
    this.image,
  });

  factory Detection.fromJson(Map<String, dynamic> json) {
    return Detection(
      id: json['id'] ?? 0,
      className: json['class_name'] ?? 'Unknown',
      confidence: (json['confidence'] ?? 0).toDouble(),
      bbox: (json['bbox'] as List<dynamic>?)
              ?.map((e) => (e as num).toDouble())
              .toList() ??
          [],
      image: json['image'],
    );
  }
}
