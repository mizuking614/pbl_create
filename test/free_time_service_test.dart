import 'package:flutter_test/flutter_test.dart';
import 'package:pbl_create/models/user_routine.dart';
import 'package:pbl_create/models/schedule_event.dart';
import 'package:pbl_create/services/free_time_service.dart';

void main() {
  group('FreeTimeService Tests', () {
    final service = FreeTimeService();
    final today = DateTime(2026, 7, 9); // 木曜日

    test('Should calculate correct free time after subtracting routine sleep and meals', () {
      final routine = UserRoutine(
        sleepTime: TimeRange(startHour: 23, startMinute: 0, endHour: 7, endMinute: 0),
        mealTimes: [
          TimeRange(startHour: 12, startMinute: 0, endHour: 13, endMinute: 0),
        ],
      );

      // 固定予定なし
      final freeSlots = service.calculateFreeTimeSlots(
        date: today,
        routine: routine,
        events: [],
      );

      // 期待される空き時間:
      // 00:00 - 07:00 (睡眠) -> 除外されるので、残りは 07:00 - 24:00
      // 12:00 - 13:00 (食事) -> 除外されるので、残りは 07:00 - 12:00 と 13:00 - 23:00
      // 23:00 - 24:00 (睡眠) -> 除外
      
      expect(freeSlots.length, 2);
      
      // 1つ目のスロット: 07:00 - 12:00
      expect(freeSlots[0].start.hour, 7);
      expect(freeSlots[0].end.hour, 12);
      
      // 2つ目のスロット: 13:00 - 23:00
      expect(freeSlots[1].start.hour, 13);
      expect(freeSlots[1].end.hour, 23);
    });

    test('Should subtract fixed events (e.g. classes)', () {
      final routine = UserRoutine(
        sleepTime: TimeRange(startHour: 23, startMinute: 0, endHour: 7, endMinute: 0),
        mealTimes: [],
      );

      // 授業が 9:00 - 10:30 にある
      final events = [
        ScheduleEvent(
          id: '1',
          title: 'Class',
          startTime: DateTime(2026, 7, 9, 9, 0),
          endTime: DateTime(2026, 7, 9, 10, 30),
          isClass: true,
        ),
      ];

      final freeSlots = service.calculateFreeTimeSlots(
        date: today,
        routine: routine,
        events: events,
      );

      // 期待される空き時間:
      // 睡眠除外後: 07:00 - 23:00
      // 授業除外後: 07:00 - 09:00 と 10:30 - 23:00
      expect(freeSlots.length, 2);
      
      expect(freeSlots[0].start.hour, 7);
      expect(freeSlots[0].end.hour, 9);
      
      expect(freeSlots[1].start.hour, 10);
      expect(freeSlots[1].start.minute, 30);
      expect(freeSlots[1].end.hour, 23);
    });
  });
}
