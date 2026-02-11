class Detection {
  final String className;
  final double confidence;

  Detection({
    required this.className,
    required this.confidence,
  });

  factory Detection.fromJson(Map<String, dynamic> json) {
    return Detection(
      className: json['class_name'] ?? '',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
