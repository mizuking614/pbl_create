import 'package:flutter_test/flutter_test.dart';
import 'package:pbl_create/models/assignment.dart';
import 'package:pbl_create/services/priority_engine.dart';

void main() {
  group('PriorityEngine Tests', () {
    final engine = PriorityEngine();
    final now = DateTime.now();

    test('Should calculate higher score for higher importance when urgency is equal', () {
      final aHigh = Assignment(
        id: '1',
        title: 'High Importance',
        courseName: 'Test',
        dueDate: now.add(const Duration(days: 2)),
        estimatedHours: 2.0,
        importance: 5,
      );

      final aLow = Assignment(
        id: '2',
        title: 'Low Importance',
        courseName: 'Test',
        dueDate: now.add(const Duration(days: 2)),
        estimatedHours: 2.0,
        importance: 1,
      );

      final scoreHigh = engine.calculateScore(aHigh, now, 5.0, 5.0);
      final scoreLow = engine.calculateScore(aLow, now, 5.0, 5.0);

      expect(scoreHigh, greaterThan(scoreLow));
    });

    test('Should calculate higher score for closer due date when importance is equal', () {
      final aSoon = Assignment(
        id: '1',
        title: 'Due Soon',
        courseName: 'Test',
        dueDate: now.add(const Duration(hours: 5)),
        estimatedHours: 2.0,
        importance: 3,
      );

      final aLater = Assignment(
        id: '2',
        title: 'Due Later',
        courseName: 'Test',
        dueDate: now.add(const Duration(days: 5)),
        estimatedHours: 2.0,
        importance: 3,
      );

      final scoreSoon = engine.calculateScore(aSoon, now, 5.0, 5.0);
      final scoreLater = engine.calculateScore(aLater, now, 5.0, 5.0);

      expect(scoreSoon, greaterThan(scoreLater));
    });

    test('Should sort assignments with uncompleted first, then by priority score', () {
      final assignments = [
        Assignment(id: '1', title: 'Low Priority', courseName: 'Test', dueDate: now.add(const Duration(days: 5)), estimatedHours: 1.0, importance: 1),
        Assignment(id: '2', title: 'Completed High Priority', courseName: 'Test', dueDate: now.add(const Duration(hours: 2)), estimatedHours: 1.0, importance: 5, isCompleted: true),
        Assignment(id: '3', title: 'High Priority', courseName: 'Test', dueDate: now.add(const Duration(hours: 2)), estimatedHours: 1.0, importance: 5),
      ];

      final sorted = engine.calculateAndSort(assignments: assignments, importanceWeight: 5.0, urgencyWeight: 5.0);

      expect(sorted.length, 3);
      expect(sorted[0].id, '3'); // High Priority (uncompleted)
      expect(sorted[1].id, '1'); // Low Priority (uncompleted)
      expect(sorted[2].id, '2'); // Completed (always last)
    });
  });
}
