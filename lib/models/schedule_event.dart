class ScheduleEvent {
  final String id;
  final String title;
  final DateTime startTime;
  final DateTime endTime;
  final bool isClass; // 授業かどうか

  ScheduleEvent({
    required this.id,
    required this.title,
    required this.startTime,
    required this.endTime,
    this.isClass = false,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'startTime': startTime.toIso8601String(),
      'endTime': endTime.toIso8601String(),
      'isClass': isClass ? 1 : 0,
    };
  }

  factory ScheduleEvent.fromMap(Map<String, dynamic> map) {
    return ScheduleEvent(
      id: map['id'] as String,
      title: map['title'] as String,
      startTime: DateTime.parse(map['startTime'] as String),
      endTime: DateTime.parse(map['endTime'] as String),
      isClass: map['isClass'] == 1 || map['isClass'] == true,
    );
  }
}
