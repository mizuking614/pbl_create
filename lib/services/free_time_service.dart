import '../models/user_routine.dart';
import '../models/schedule_event.dart';
import '../models/time_slot.dart';

class FreeTimeService {
  // 指定された日の空き時間を計算する
  List<TimeSlot> calculateFreeTimeSlots({
    required DateTime date,
    required UserRoutine routine,
    required List<ScheduleEvent> events,
  }) {
    final startOfDay = DateTime(date.year, date.month, date.day, 0, 0);
    final endOfDay = DateTime(date.year, date.month, date.day, 23, 59, 59, 999);

    List<TimeSlot> freeSlots = [TimeSlot(start: startOfDay, end: endOfDay)];

    // 1. 睡眠時間を除外
    final sleepSlots = _getSleepSlotsForDate(date, routine.sleepTime);
    for (final sleep in sleepSlots) {
      freeSlots = _subtractSlotFromList(freeSlots, sleep);
    }

    // 2. 食事時間を除外
    final mealSlots = _getMealSlotsForDate(date, routine.mealTimes);
    for (final meal in mealSlots) {
      freeSlots = _subtractSlotFromList(freeSlots, meal);
    }

    // 3. 固定予定（授業、バイトなど）を除外
    for (final event in events) {
      final eventStart = event.startTime.isBefore(startOfDay) ? startOfDay : event.startTime;
      final eventEnd = event.endTime.isAfter(endOfDay) ? endOfDay : event.endTime;

      if (eventStart.isBefore(eventEnd)) {
        final eventSlot = TimeSlot(start: eventStart, end: eventEnd);
        freeSlots = _subtractSlotFromList(freeSlots, eventSlot);
      }
    }

    // 10分未満の非常に短い隙間時間は除外する
    return freeSlots.where((slot) => slot.duration.inMinutes >= 10).toList();
  }

  // 特定の日における睡眠時間スロットの取得
  List<TimeSlot> _getSleepSlotsForDate(DateTime date, TimeRange sleepTime) {
    List<TimeSlot> slots = [];
    final year = date.year;
    final month = date.month;
    final day = date.day;

    if (sleepTime.startHour > sleepTime.endHour || 
        (sleepTime.startHour == sleepTime.endHour && sleepTime.startMinute > sleepTime.endMinute)) {
      // 睡眠が日を跨ぐ場合 (例: 23:00 〜 7:00)
      // 00:00 〜 7:00 と 23:00 〜 24:00 の2つに分割して除外
      final morningEnd = DateTime(year, month, day, sleepTime.endHour, sleepTime.endMinute);
      slots.add(TimeSlot(start: DateTime(year, month, day, 0, 0), end: morningEnd));

      final nightStart = DateTime(year, month, day, sleepTime.startHour, sleepTime.startMinute);
      slots.add(TimeSlot(start: nightStart, end: DateTime(year, month, day, 23, 59, 59, 999)));
    } else {
      // 日を跨がない睡眠
      final sleepStart = DateTime(year, month, day, sleepTime.startHour, sleepTime.startMinute);
      final sleepEnd = DateTime(year, month, day, sleepTime.endHour, sleepTime.endMinute);
      slots.add(TimeSlot(start: sleepStart, end: sleepEnd));
    }

    return slots;
  }

  // 特定の日における食事時間スロットの取得
  List<TimeSlot> _getMealSlotsForDate(DateTime date, List<TimeRange> mealTimes) {
    final year = date.year;
    final month = date.month;
    final day = date.day;

    return mealTimes.map((meal) {
      return TimeSlot(
        start: DateTime(year, month, day, meal.startHour, meal.startMinute),
        end: DateTime(year, month, day, meal.endHour, meal.endMinute),
      );
    }).toList();
  }

  // 複数のTimeSlotリストから、特定のTimeSlot（除外領域）を引く
  List<TimeSlot> _subtractSlotFromList(List<TimeSlot> sourceList, TimeSlot exclude) {
    List<TimeSlot> result = [];

    for (final slot in sourceList) {
      // 重複がない場合
      if (slot.end.isBefore(exclude.start) || slot.start.isAfter(exclude.end) || 
          slot.end.isAtSameMomentAs(exclude.start) || slot.start.isAtSameMomentAs(exclude.end)) {
        result.add(slot);
        continue;
      }

      // 完全被覆（slotがexcludeに完全に含まれる）
      if ((slot.start.isAfter(exclude.start) || slot.start.isAtSameMomentAs(exclude.start)) &&
          (slot.end.isBefore(exclude.end) || slot.end.isAtSameMomentAs(exclude.end))) {
        continue;
      }

      // 中間被覆（excludeがslotの中に完全に収まり、前後が余る）
      if (slot.start.isBefore(exclude.start) && slot.end.isAfter(exclude.end)) {
        result.add(TimeSlot(start: slot.start, end: exclude.start));
        result.add(TimeSlot(start: exclude.end, end: slot.end));
        continue;
      }

      // 左側重複（excludeがslotの開始部分に被る）
      if (slot.start.isAfter(exclude.start) || slot.start.isAtSameMomentAs(exclude.start)) {
        if (exclude.end.isBefore(slot.end)) {
          result.add(TimeSlot(start: exclude.end, end: slot.end));
        }
        continue;
      }

      // 右側重複（excludeがslotの終了部分に被る）
      if (slot.end.isBefore(exclude.end) || slot.end.isAtSameMomentAs(exclude.end)) {
        if (slot.start.isBefore(exclude.start)) {
          result.add(TimeSlot(start: slot.start, end: exclude.start));
        }
        continue;
      }
    }

    return result;
  }
}
