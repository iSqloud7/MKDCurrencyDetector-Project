import 'detection.dart';

// Го претставува целосниот резултат од детекцијата
class DetectionResult {
  final bool success;
  final String? type;
  final List<Detection> detections;
  final int count;
  final String? message;

  // 🗣️ TEXT that will be sent to ElevenLabs on frontend
  final String? ttsText;

  DetectionResult({
    required this.success,
    this.type,
    required this.detections,
    required this.count,
    this.message,
    this.ttsText,
  });

  // Зема JSON објект и го претвора во DetectionResult објект
  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      success: json['success'] ?? true,
      type: json['type'],
      detections: (json['detections'] as List<dynamic>?)
              ?.map((e) => Detection.fromJson(e))
              .toList() ??
          [],
      count: json['count'] ?? 0,
      message: json['message'],
      ttsText: json['tts_text'], // ✅ THIS is what backend sends
    );
  }

  // 🖥️ UI text only
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
