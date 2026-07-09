import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:pbl_create/main.dart';

void main() {
  testWidgets('Portal screen integration test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Verify that the portal screen elements exist.
    expect(find.text('学修支援システム ポータル'), findsOneWidget);
    expect(find.text('学習優先順位AI (あなたの担当)'), findsOneWidget);
    expect(find.text('学修計画・類題生成 (メンバーA担当)'), findsOneWidget);
    expect(find.text('ログイン・授業・資料・DB (メンバーB担当)'), findsOneWidget);
  });
}
