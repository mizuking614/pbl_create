class TimeRange {
  final int startHour;
  final int startMinute;
  final int endHour;
  final int endMinute;

  TimeRange({
    required this.startHour,
    required this.startMinute,
    required this.endHour,
    required this.endMinute,
  });

  Map<String, dynamic> toMap() {
    return {
      'startHour': startHour,
      'startMinute': startMinute,
      'endHour': endHour,
      'endMinute': endMinute,
    };
  }

  factory TimeRange.fromMap(Map<String, dynamic> map) {
    return TimeRange(
      startHour: map['startHour'] as int,
      startMinute: map['startMinute'] as int,
      endHour: map['endHour'] as int,
      endMinute: map['endMinute'] as int,
    );
  }
}

class UserRoutine {
  final TimeRange sleepTime;
  final List<TimeRange> mealTimes;

  UserRoutine({
    required this.sleepTime,
    required this.mealTimes,
  });

  Map<String, dynamic> toMap() {
    return {
      'sleepTime': sleepTime.toMap(),
      'mealTimes': mealTimes.map((e) => e.toMap()).toList(),
    };
  }

  factory UserRoutine.fromMap(Map<String, dynamic> map) {
    return UserRoutine(
      sleepTime: TimeRange.fromMap(map['sleepTime'] as Map<String, dynamic>),
      mealTimes: (map['mealTimes'] as List<dynamic>)
          .map((e) => TimeRange.fromMap(e as Map<String, dynamic>))
          .toList(),
    );
  }

  // デフォルトの生活リズムを設定するヘルパー
  factory UserRoutine.defaultRoutine() {
    return UserRoutine(
      sleepTime: TimeRange(startHour: 23, startMinute: 0, endHour: 7, endMinute: 0), // 23:00 〜 7:00 睡眠
      mealTimes: [
        TimeRange(startHour: 8, startMinute: 0, endHour: 9, endMinute: 0),   // 朝食: 8:00〜9:00
        TimeRange(startHour: 12, startMinute: 0, endHour: 13, endMinute: 0), // 昼食: 12:00〜13:00
        TimeRange(startHour: 19, startMinute: 0, endHour: 20, endMinute: 0), // 夕食: 19:00〜20:00
      ],
    );
  }
}
