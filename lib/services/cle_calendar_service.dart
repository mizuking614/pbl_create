import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../models/assignment.dart';
import '../models/schedule_event.dart';

class CleCalendarService {
  String lastErrorMessage = '';

  // CLEからのICS取得先を探す順序:
  // 1) SharedPreferencesの 'cle_ics_url' 設定
  // 見つからない場合は従来のダミーデータにフォールバックします。

  Future<String?> _findIcsUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final stored = prefs.getString('cle_ics_url');
      if (stored != null && stored.trim().isNotEmpty) {
        final uri = Uri.tryParse(stored.trim());
        if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
          lastErrorMessage = 'CLE URLの形式が正しくありません。URLを確認してください。';
          return null;
        }
        lastErrorMessage = '';
        return stored.trim();
      }
      lastErrorMessage = 'CLE URLが未設定のため、サンプルデータを表示しています。';
    } catch (_) {
      lastErrorMessage = 'CLE URLの読み込み中にエラーが発生しました。';
    }

    return null;
  }

  DateTime? _parseIcsDate(String raw) {
    // supports formats like: 20260715T090000Z or 20260715T090000 or 20260715
    final r1 = RegExp(r"^(\d{8})T(\d{6})(Z)?");
    final r2 = RegExp(r"^(\d{8})");
    final m1 = r1.firstMatch(raw);
    if (m1 != null) {
      final d = m1.group(1)!; // YYYYMMDD
      final t = m1.group(2)!; // HHMMSS
      final year = int.parse(d.substring(0, 4));
      final month = int.parse(d.substring(4, 6));
      final day = int.parse(d.substring(6, 8));
      final hour = int.parse(t.substring(0, 2));
      final minute = int.parse(t.substring(2, 4));
      final second = int.parse(t.substring(4, 6));
      if (m1.group(3) != null) {
        return DateTime.utc(year, month, day, hour, minute, second).toLocal();
      }
      return DateTime(year, month, day, hour, minute, second);
    }
    final m2 = r2.firstMatch(raw);
    if (m2 != null) {
      final d = m2.group(1)!;
      final year = int.parse(d.substring(0, 4));
      final month = int.parse(d.substring(4, 6));
      final day = int.parse(d.substring(6, 8));
      return DateTime(year, month, day);
    }
    return null;
  }

  List<Map<String, String>> _parseIcs(String data) {
    final events = <Map<String, String>>[];
    final parts = data.split(RegExp(r"BEGIN:VEVENT", multiLine: true));
    for (var i = 1; i < parts.length; i++) {
      final part = parts[i];
      final map = <String, String>{};
      for (final line in part.split(RegExp(r"\r?\n"))) {
        if (line.trim().isEmpty) continue;
        // Handle folded lines (continuation starting with space)
        if (line.startsWith(' ')) {
          // append to last key
          if (map.isNotEmpty) {
            final lastKey = map.keys.last;
            map[lastKey] = (map[lastKey]! + line.trim());
          }
          continue;
        }
        final idx = line.indexOf(':');
        if (idx == -1) continue;
        final key = line.substring(0, idx);
        final value = line.substring(idx + 1);
        map[key] = value;
      }
      events.add(map);
    }
    return events;
  }

  // 課題締め切り情報の取得 — ICSを探してパース、なければダミー
  Future<List<Assignment>> fetchAssignments() async {
    lastErrorMessage = '';
    final icsUrl = await _findIcsUrl();
    if (icsUrl == null) {
      // 以前のダミーを保持
      await Future.delayed(const Duration(milliseconds: 200));
      final now = DateTime.now();
      return [
        Assignment(
          id: 'a_dummy_1',
          title: '情報数学I レポート課題',
          courseName: '情報数学I',
          dueDate: now.add(const Duration(days: 1, hours: 8)),
          estimatedHours: 2.5,
          importance: 4,
        ),
      ];
    }

    try {
      final uri = Uri.tryParse(icsUrl);
      if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
        lastErrorMessage = 'CLE URLの形式が正しくありません。URLを確認してください。';
        return [];
      }
      final res = await http.get(uri);
      if (res.statusCode != 200) {
        lastErrorMessage = 'CLE URLからICSを取得できませんでした。URLを確認してください。';
        return [];
      }
      final events = _parseIcs(res.body);
      final now = DateTime.now();
      final assignmentCutoff = DateTime(
        now.year,
        now.month - 5,
        now.day,
        now.hour,
        now.minute,
        now.second,
      );
      final out = <Assignment>[];
      for (final ev in events) {
        final summary = ev['SUMMARY'] ?? ev['SUMMARY;LANGUAGE=ja'] ?? '';
        final dtstartRaw = ev.entries
            .firstWhere(
              (e) => e.key.startsWith('DTSTART'),
              orElse: () => MapEntry('', ''),
            )
            .value;
        final dtendRaw = ev.entries
            .firstWhere(
              (e) => e.key.startsWith('DTEND'),
              orElse: () => MapEntry('', ''),
            )
            .value;
        final dtstart = dtstartRaw.isNotEmpty
            ? _parseIcsDate(dtstartRaw)
            : null;
        final dtend = dtendRaw.isNotEmpty ? _parseIcsDate(dtendRaw) : null;
        final due = dtend ?? dtstart;
        // 過去の課題も一覧に残し、画面側で「期限超過」と表示する。
        // 簡易ルール: SUMMARYに課題関連の語が含まれるものを課題として扱う。
        if (due != null &&
            due.isAfter(assignmentCutoff) &&
            (summary.contains('課題') ||
                summary.contains('提出') ||
                summary.contains('レポート') ||
                summary.contains('宿題') ||
                summary.toLowerCase().contains('homework') ||
                summary.toLowerCase().contains('assignment'))) {
          out.add(
            Assignment(
              id:
                  ev['UID'] ??
                  ev['SUMMARY'] ??
                  DateTime.now().toIso8601String(),
              title: summary.isNotEmpty ? summary : 'CLE課題',
              courseName: '',
              dueDate: due,
              estimatedHours: 1.5,
              importance: 3,
            ),
          );
        }
      }
      return out;
    } catch (e) {
      lastErrorMessage = 'CLE の読込に失敗しました。URL・接続状態を確認してください。';
      return [];
    }
  }

  // 予定情報の取得 — 指定日のイベントをICSから読み込む
  Future<List<ScheduleEvent>> fetchScheduleEvents(DateTime date) async {
    lastErrorMessage = '';
    final icsUrl = await _findIcsUrl();
    if (icsUrl == null) {
      // フォールバックのダミー
      await Future.delayed(const Duration(milliseconds: 100));
      final baseDate = DateTime(date.year, date.month, date.day);
      final weekday = date.weekday;
      List<ScheduleEvent> events = [];
      if (weekday == DateTime.saturday || weekday == DateTime.sunday) {
        events.add(
          ScheduleEvent(
            id: 'e_pt',
            title: 'アルバイト',
            startTime: baseDate.add(const Duration(hours: 13)),
            endTime: baseDate.add(const Duration(hours: 18)),
            isClass: false,
          ),
        );
      } else {
        events.addAll([
          ScheduleEvent(
            id: 'e_c1',
            title: '1限: 情報数学I',
            startTime: baseDate.add(const Duration(hours: 8, minutes: 50)),
            endTime: baseDate.add(const Duration(hours: 10, minutes: 20)),
            isClass: true,
          ),
          ScheduleEvent(
            id: 'e_c2',
            title: '2限: 物理学基礎',
            startTime: baseDate.add(const Duration(hours: 10, minutes: 30)),
            endTime: baseDate.add(const Duration(hours: 12, minutes: 0)),
            isClass: true,
          ),
        ]);
        if (weekday == DateTime.wednesday || weekday == DateTime.friday) {
          events.add(
            ScheduleEvent(
              id: 'e_c3',
              title: '4限: キャリア設計',
              startTime: baseDate.add(const Duration(hours: 14, minutes: 40)),
              endTime: baseDate.add(const Duration(hours: 16, minutes: 10)),
              isClass: true,
            ),
          );
        }
      }
      return events;
    }

    try {
      final uri = Uri.tryParse(icsUrl);
      if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
        lastErrorMessage = 'CLE URLの形式が正しくありません。URLを確認してください。';
        return [];
      }
      final res = await http.get(uri);
      if (res.statusCode != 200) {
        lastErrorMessage = 'CLE URLから予定を取得できませんでした。URLを確認してください。';
        return [];
      }
      final events = _parseIcs(res.body);
      final targetDayStart = DateTime(date.year, date.month, date.day);
      final targetDayEnd = targetDayStart.add(const Duration(days: 1));
      final out = <ScheduleEvent>[];
      for (final ev in events) {
        final summary = ev['SUMMARY'] ?? ev['SUMMARY;LANGUAGE=ja'] ?? '';
        final dtstartRaw = ev.entries
            .firstWhere(
              (e) => e.key.startsWith('DTSTART'),
              orElse: () => MapEntry('', ''),
            )
            .value;
        final dtendRaw = ev.entries
            .firstWhere(
              (e) => e.key.startsWith('DTEND'),
              orElse: () => MapEntry('', ''),
            )
            .value;
        final dtstart = dtstartRaw.isNotEmpty
            ? _parseIcsDate(dtstartRaw)
            : null;
        final dtend = dtendRaw.isNotEmpty ? _parseIcsDate(dtendRaw) : null;
        if (dtstart != null &&
            dtstart.isBefore(targetDayEnd) &&
            (dtend == null || dtend.isAfter(targetDayStart))) {
          out.add(
            ScheduleEvent(
              id: ev['UID'] ?? summary,
              title: summary.isNotEmpty ? summary : '予定',
              startTime: dtstart,
              endTime: dtend ?? dtstart.add(const Duration(hours: 1)),
              isClass:
                  summary.contains('限') ||
                  summary.contains('授業') ||
                  summary.contains('講義'),
            ),
          );
        }
      }
      return out;
    } catch (e) {
      lastErrorMessage = '予定の読み込みに失敗しました。URLや接続状態を確認してください。';
      return [];
    }
  }
}
