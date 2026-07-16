import '../models/assignment.dart';
import '../models/time_slot.dart';

class TodayTaskAllocation {
  final Assignment assignment;
  final TimeSlot timeSlot;
  final int allocatedMinutes;

  TodayTaskAllocation({
    required this.assignment,
    required this.timeSlot,
    required this.allocatedMinutes,
  });
}

class TodaySuggestions {
  final List<TodayTaskAllocation> allocations;
  final List<Assignment> remainingAssignments;
  final int totalFreeMinutes;
  final int allocatedMinutes;

  TodaySuggestions({
    required this.allocations,
    required this.remainingAssignments,
    required this.totalFreeMinutes,
    required this.allocatedMinutes,
  });
}

class TodayTaskSuggester {
  TodaySuggestions suggest({
    required List<Assignment> sortedAssignments,
    required List<TimeSlot> freeSlots,
  }) {
    List<TodayTaskAllocation> allocations = [];
    List<Assignment> unallocated = [];

    // 未完了の課題のみを対象にする
    final pendingAssignments = sortedAssignments.where((a) => !a.isCompleted).toList();

    // 空き時間のコピーを作成
    List<TimeSlot> availableSlots = freeSlots
        .map((s) => TimeSlot(start: s.start, end: s.end))
        .toList()
      ..sort((a, b) => a.start.compareTo(b.start));

    int totalFreeMinutes = availableSlots.fold(0, (sum, slot) => sum + slot.duration.inMinutes);
    int allocatedMinutes = 0;

    int slotIndex = 0;

    for (final assignment in pendingAssignments) {
      double remainingHours = assignment.estimatedHours;
      int remainingMinutes = (remainingHours * 60).round();

      if (slotIndex >= availableSlots.length) {
        // 空き時間がもうない場合は、残りの未完了課題を全て未割り当てとする
        unallocated.add(assignment);
        continue;
      }

      while (remainingMinutes > 0 && slotIndex < availableSlots.length) {
        final slot = availableSlots[slotIndex];
        final slotMinutes = slot.duration.inMinutes;

        if (slotMinutes <= 0) {
          slotIndex++;
          continue;
        }

        if (slotMinutes >= remainingMinutes) {
          final allocationStart = slot.start;
          final allocationEnd = slot.start.add(Duration(minutes: remainingMinutes));

          allocations.add(TodayTaskAllocation(
            assignment: assignment,
            timeSlot: TimeSlot(start: allocationStart, end: allocationEnd),
            allocatedMinutes: remainingMinutes,
          ));

          allocatedMinutes += remainingMinutes;

          availableSlots[slotIndex] = TimeSlot(
            start: allocationEnd,
            end: slot.end,
          );

          remainingMinutes = 0;
        } else {
          allocations.add(TodayTaskAllocation(
            assignment: assignment,
            timeSlot: slot,
            allocatedMinutes: slotMinutes,
          ));

          allocatedMinutes += slotMinutes;
          remainingMinutes -= slotMinutes;

          slotIndex++;
        }
      }

      if (remainingMinutes > 0) {
        unallocated.add(assignment);
      }
    }

    return TodaySuggestions(
      allocations: allocations,
      remainingAssignments: unallocated,
      totalFreeMinutes: totalFreeMinutes,
      allocatedMinutes: allocatedMinutes,
    );
  }
}
