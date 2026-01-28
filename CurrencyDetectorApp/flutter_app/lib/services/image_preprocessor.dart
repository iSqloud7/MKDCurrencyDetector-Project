import 'dart:io';
import 'package:image/image.dart' as img;

// Ја прима оригиналната слика и
// враќа нова, обработена слика
Future<File> preprocessImage(File file) async {
  final bytes = await file.readAsBytes();
  img.Image? image = img.decodeImage(bytes);
  if (image == null) return file;

  image = img.bakeOrientation(image);

  if (image.width < 1920) {
    image = img.copyResize(image, width: 1920, interpolation: img.Interpolation.linear);
  }

  final processedFile = File('${file.parent.path}/processed_${file.uri.pathSegments.last}');
  await processedFile.writeAsBytes(img.encodeJpg(image, quality: 95));

  print('Processed image size: ${image.width} x ${image.height}');
  return processedFile;
}
