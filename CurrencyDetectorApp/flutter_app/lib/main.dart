import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'app.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  await dotenv.load(fileName: ".env");
  runApp(App(camera: cameras.first));
}
