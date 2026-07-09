import 'package:flutter/material.dart';

class MemberAScreen extends StatelessWidget {
  const MemberAScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Member A Screen'),
      ),
      body: const Center(
        child: Text(
          'This is Member A\'s workspace.\nStart editing here!',
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
