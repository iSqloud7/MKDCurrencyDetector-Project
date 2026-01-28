import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/detection_result.dart';
import 'image_preprocessor.dart';
import 'package:http_parser/http_parser.dart';

// Комуникација со серверот
// праќа слика до backend
// прима JSON со резултат од детекција
// проверува дали работи серверот
class ApiService {
  Future<DetectionResult?> detectCurrency(File imageFile) async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.detectEndpoint}');
      final request = http.MultipartRequest('POST', uri);
      final processedImage = await preprocessImage(imageFile);

      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          processedImage.path,
          contentType: MediaType('image', 'jpeg'),
        ),
      );

      final streamedResponse = await request.send().timeout(ApiConfig.timeout);
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final jsonData = json.decode(response.body) as Map<String, dynamic>;
        return DetectionResult.fromJson(jsonData);
      } else {
        print('API returned error: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print("API Error: $e");
      return null;
    }
  }

  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse('${ApiConfig.baseUrl}${ApiConfig.healthEndpoint}');
      final response = await http.get(uri).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      print("Health check failed: $e");
      return false;
    }
  }
}
