import '../models/assignment.dart';
import '../models/schedule_event.dart';

class CleCalendarService {
  // 課題締め切り情報の取得 (ダミーデータ)
  Future<List<Assignment>> fetchAssignments() async {
    // ネットワークやDBアクセスを模した遅延
    await Future.delayed(const Duration(milliseconds: 200));

    final now = DateTime.now();
    return [
      Assignment(
        id: 'a1',
        title: '情報数学I レポート課題',
        courseName: '情報数学I',
        dueDate: now.add(const Duration(days: 1, hours: 8)), // 明日の夕方
        estimatedHours: 2.5,
        importance: 4,
      ),
      Assignment(
        id: 'a2',
        title: 'プログラミング演習II 最終課題',
        courseName: 'プログラミング演習II',
        dueDate: now.add(const Duration(days: 3, hours: 14)), // 3日後
        estimatedHours: 6.0,
        importance: 5,
      ),
      Assignment(
        id: 'a3',
        title: '英語コミュニケーション 小テスト対策',
        courseName: '英語コミュニケーション',
        dueDate: now.add(const Duration(days: 2, hours: 2)), // 2日後
        estimatedHours: 1.0,
        importance: 2,
      ),
      Assignment(
        id: 'a4',
        title: 'キャリア設計 振り返りシート',
        courseName: 'キャリア設計',
        dueDate: now.add(const Duration(days: 5)), // 5日後
        estimatedHours: 1.5,
        importance: 3,
      ),
      Assignment(
        id: 'a5',
        title: '物理学基礎 課題3',
        courseName: '物理学基礎',
        dueDate: now.add(const Duration(hours: 12)), // 今日の夜（残り12時間）
        estimatedHours: 1.5,
        importance: 3,
      ),
    ];
  }

  // 予定情報の取得 (ダミーデータ)
  Future<List<ScheduleEvent>> fetchScheduleEvents(DateTime date) async {
    await Future.delayed(const Duration(milliseconds: 100));
    
    // 対象日の朝8時、夕方6時などを基準に授業や予定を生成
    final baseDate = DateTime(date.year, date.month, date.day);
    
    // 曜日ごとにダミーの予定を変える
    final weekday = date.weekday;
    List<ScheduleEvent> events = [];

    if (weekday == DateTime.saturday || weekday == DateTime.sunday) {
      // 週末の予定 (バイトなど)
      events.add(
        ScheduleEvent(
          id: 'e_pt',
          title: 'アルバイト',
          startTime: baseDate.add(const Duration(hours: 13)), // 13:00
          endTime: baseDate.add(const Duration(hours: 18)),   // 18:00
          isClass: false,
        ),
      );
    } else {
      // 平日の予定 (授業)
      events.addAll([
        ScheduleEvent(
          id: 'e_c1',
          title: '1限: 情報数学I',
          startTime: baseDate.add(const Duration(hours: 8, minutes: 50)), // 8:50
          endTime: baseDate.add(const Duration(hours: 10, minutes: 20)),   // 10:20
          isClass: true,
        ),
        ScheduleEvent(
          id: 'e_c2',
          title: '2限: 物理学基礎',
          startTime: baseDate.add(const Duration(hours: 10, minutes: 30)), // 10:30
          endTime: baseDate.add(const Duration(hours: 12, minutes: 0)),    // 12:00
          isClass: true,
        ),
      ]);

      if (weekday == DateTime.wednesday || weekday == DateTime.friday) {
        events.add(
          ScheduleEvent(
            id: 'e_c3',
            title: '4限: キャリア設計',
            startTime: baseDate.add(const Duration(hours: 14, minutes: 40)), // 14:40
            endTime: baseDate.add(const Duration(hours: 16, minutes: 10)),   // 16:10
            isClass: true,
          ),
        );
      }
    }

    return events;
  }
}
