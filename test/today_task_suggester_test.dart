import 'package:flutter_test/flutter_test.dart';
import 'package:pbl_create/models/assignment.dart';
import 'package:pbl_create/models/time_slot.dart';
import 'package:pbl_create/services/today_task_suggester.dart';

void main() {
  test('excludes assignments overdue by seven days or more from today suggestions', () {
    final now = DateTime.now();
    final overdue = Assignment(
      id: 'overdue',
      title: 'Old assignment',
      courseName: 'Test',
      dueDate: now.subtract(const Duration(days: 8)),
      estimatedHours: 1,
      importance: 5,
    );
    final current = Assignment(
      id: 'current',
      title: 'Current assignment',
      courseName: 'Test',
      dueDate: now.add(const Duration(days: 1)),
      estimatedHours: 1,
      importance: 3,
    );

    final suggestions = TodayTaskSuggester().suggest(
      sortedAssignments: [overdue, current],
      freeSlots: [
        TimeSlot(start: now, end: now.add(const Duration(hours: 2))),
      ],
    );

    expect(suggestions.allocations.map((item) => item.assignment.id), ['current']);
    expect(suggestions.remainingAssignments, isEmpty);
  });
}