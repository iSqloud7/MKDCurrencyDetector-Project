class ApiConfig {
  // За Android емулатор
  // static const String baseUrl = 'http://10.0.2.2:8000';

  // За iOS симулатор
  // static const String baseUrl = 'http://localhost:8000';

  // За физички уред (замени со твојата IP)
  static const String baseUrl = 'http://10.37.134.202:8000';

  static const String detectEndpoint = '/detect';
  static const String healthEndpoint = '/health';

  // Timeout
  static const Duration timeout = Duration(seconds: 60);
}
