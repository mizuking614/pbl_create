import 'package:flutter/material.dart';

class MemberBScreen extends StatelessWidget {
  const MemberBScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Member B Screen'),
      ),
      body: const Center(
        child: Text(
          'This is Member B\'s workspace.\nStart editing here!',
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
