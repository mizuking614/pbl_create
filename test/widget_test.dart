import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:pbl_create/main.dart';

void main() {
  testWidgets('Portal screen integration test', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const MyApp());
    await tester.pump(const Duration(milliseconds: 100));

    // Verify that the portal screen elements exist.
    expect(find.text('AIタスク管理ポータル'), findsOneWidget);
    expect(find.text('学習優先順位AI'), findsOneWidget);
    expect(find.text('学修計画・類題生成'), findsOneWidget);
    expect(find.text('授業・資料管理'), findsOneWidget);
  });

  testWidgets('Task list supports category-based filtering', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const MyApp());
    await tester.pump(const Duration(milliseconds: 100));

    await tester.tap(find.text('学習優先順位AI'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('課題一覧と調整'));
    await tester.pumpAndSettle();

    expect(find.text('カテゴリで絞り込み'), findsOneWidget);
    expect(find.text('すべて'), findsOneWidget);
  });

  testWidgets('Study plan screen shows material-linked context selection', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({
      'member_b_courses': ['情報理論'],
      'member_b_materials': ['第1回資料'],
    });
    await tester.pumpWidget(const MyApp());
    await tester.pump(const Duration(milliseconds: 100));

    await tester.tap(find.text('学修計画・類題生成'));
    await tester.pumpAndSettle();

    expect(find.text('資料連携'), findsOneWidget);
    expect(find.text('情報理論'), findsWidgets);
    expect(find.text('第1回資料'), findsWidgets);
  });

  testWidgets('Materials screen shows upload controls', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(const MyApp());
    await tester.pump(const Duration(milliseconds: 100));

    await tester.ensureVisible(find.text('授業・資料管理'));
    await tester.tap(find.text('授業・資料管理'));
    await tester.pumpAndSettle();

    expect(find.text('資料アップロード'), findsOneWidget);
    expect(find.text('ローカルAPIと同期'), findsWidgets);
  });
}
