import 'package:flutter/material.dart';

// Го претставува копчето за сликање
class CaptureButton extends StatelessWidget {
  final VoidCallback onPressed;
  final bool isLoading;

  const CaptureButton({super.key, required this.onPressed, this.isLoading = false});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      onPressed: isLoading ? null : onPressed,
      backgroundColor: Colors.green,
      icon: isLoading
          ? const SizedBox(
        width: 20,
        height: 20,
        child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
      )
          : const Icon(Icons.camera_alt, color: Colors.white),
      label: Text(isLoading ? "Се обработува..." : "Сликај", style: const TextStyle(color: Colors.white)),
    );
  }
}
