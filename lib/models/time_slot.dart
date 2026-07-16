class TimeSlot {
  final DateTime start;
  final DateTime end;

  TimeSlot({required this.start, required this.end}) {
    assert(start.isBefore(end) || start.isAtSameMomentAs(end), 'start must be before or equal to end');
  }

  Duration get duration => end.difference(start);

  bool contains(DateTime dateTime) {
    return (dateTime.isAfter(start) || dateTime.isAtSameMomentAs(start)) &&
        dateTime.isBefore(end);
  }

  @override
  String toString() {
    final startStr = '${start.hour.toString().padLeft(2, '0')}:${start.minute.toString().padLeft(2, '0')}';
    final endStr = '${end.hour.toString().padLeft(2, '0')}:${end.minute.toString().padLeft(2, '0')}';
    return '$startStr - $endStr';
  }
}
