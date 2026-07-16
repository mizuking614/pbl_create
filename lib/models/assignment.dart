class Assignment {
  final String id;
  final String title;
  final String courseName;
  final DateTime dueDate;
  final double estimatedHours; // 推定所要時間 (単位: 時間)
  final int importance; // 重要度 (1〜5)
  bool isCompleted;

  Assignment({
    required this.id,
    required this.title,
    required this.courseName,
    required this.dueDate,
    required this.estimatedHours,
    required this.importance,
    this.isCompleted = false,
  });

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'title': title,
      'courseName': courseName,
      'dueDate': dueDate.toIso8601String(),
      'estimatedHours': estimatedHours,
      'importance': importance,
      'isCompleted': isCompleted ? 1 : 0,
    };
  }

  factory Assignment.fromMap(Map<String, dynamic> map) {
    return Assignment(
      id: map['id'] as String,
      title: map['title'] as String,
      courseName: map['courseName'] as String,
      dueDate: DateTime.parse(map['dueDate'] as String),
      estimatedHours: (map['estimatedHours'] as num).toDouble(),
      importance: map['importance'] as int,
      isCompleted: map['isCompleted'] == 1 || map['isCompleted'] == true,
    );
  }
}
