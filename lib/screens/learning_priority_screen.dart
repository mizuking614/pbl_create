import 'package:flutter/material.dart';
import '../models/assignment.dart';
import '../models/schedule_event.dart';
import '../models/user_routine.dart';
import '../models/time_slot.dart';
import '../services/cle_calendar_service.dart';
import '../services/free_time_service.dart';
import '../services/priority_engine.dart';
import '../services/today_task_suggester.dart';
import '../widgets/priority_badge.dart';

class LearningPriorityScreen extends StatefulWidget {
  const LearningPriorityScreen({super.key});

  @override
  State<LearningPriorityScreen> createState() => _LearningPriorityScreenState();
}

class _LearningPriorityScreenState extends State<LearningPriorityScreen> with SingleTickerProviderStateMixin {
  final _calendarService = CleCalendarService();
  final _freeTimeService = FreeTimeService();
  final _priorityEngine = PriorityEngine();
  final _suggester = TodayTaskSuggester();

  late TabController _tabController;

  List<Assignment> _assignments = [];
  List<ScheduleEvent> _events = [];
  UserRoutine _routine = UserRoutine.defaultRoutine();
  bool _isLoading = true;

  double _importanceWeight = 5.0;
  double _urgencyWeight = 5.0;

  int _sleepStartHour = 23;
  int _sleepEndHour = 7;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
    });

    final today = DateTime.now();
    final assignments = await _calendarService.fetchAssignments();
    final events = await _calendarService.fetchScheduleEvents(today);

    setState(() {
      _assignments = assignments;
      _events = events;
      _sleepStartHour = _routine.sleepTime.startHour;
      _sleepEndHour = _routine.sleepTime.endHour;
      _isLoading = false;
    });
  }

  void _updateSleepTime(int startHour, int endHour) {
    setState(() {
      _sleepStartHour = startHour;
      _sleepEndHour = endHour;
      _routine = UserRoutine(
        sleepTime: TimeRange(
          startHour: startHour,
          startMinute: 0,
          endHour: endHour,
          endMinute: 0,
        ),
        mealTimes: _routine.mealTimes,
      );
    });
  }

  void _toggleAssignmentCompleted(String id) {
    setState(() {
      final index = _assignments.indexWhere((a) => a.id == id);
      if (index != -1) {
        _assignments[index].isCompleted = !_assignments[index].isCompleted;
      }
    });
  }

  String _formatRemainingTime(DateTime dueDate) {
    final difference = dueDate.difference(DateTime.now());
    if (difference.isNegative) {
      return '期限超過';
    }
    final days = difference.inDays;
    final hours = difference.inHours % 24;
    if (days > 0) {
      return '残り $days日 $hours時間';
    } else if (hours > 0) {
      return '残り $hours時間';
    } else {
      final minutes = difference.inMinutes % 60;
      return '残り $minutes分';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('学習優先順位AI', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          backgroundColor: const Color(0xFF1E3A8A),
          elevation: 0,
        ),
        body: const Center(
          child: CircularProgressIndicator(color: Color(0xFF1E3A8A)),
        ),
      );
    }

    final today = DateTime.now();

    final sortedAssignments = _priorityEngine.calculateAndSort(
      assignments: _assignments,
      importanceWeight: _importanceWeight,
      urgencyWeight: _urgencyWeight,
    );

    final freeSlots = _freeTimeService.calculateFreeTimeSlots(
      date: today,
      routine: _routine,
      events: _events,
    );

    final suggestions = _suggester.suggest(
      sortedAssignments: sortedAssignments,
      freeSlots: freeSlots,
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          '学習優先順位AI',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: const Color(0xFF1E3A8A),
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        bottom: TabBar(
          controller: _tabController,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white60,
          indicatorColor: const Color(0xFFF59E0B), // 暖かいオレンジ/ゴールド
          indicatorWeight: 3,
          tabs: const [
            Tab(icon: Icon(Icons.auto_awesome), text: '今日やるべきこと'),
            Tab(icon: Icon(Icons.assignment), text: '課題一覧と調整'),
            Tab(icon: Icon(Icons.schedule), text: '生活リズムと予定'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildTodayTab(suggestions),
          _buildAssignmentsTab(sortedAssignments),
          _buildRoutineTab(freeSlots),
        ],
      ),
    );
  }

  Widget _buildTodayTab(TodaySuggestions suggestions) {
    final totalFreeMins = suggestions.totalFreeMinutes;
    final allocatedMins = suggestions.allocatedMinutes;
    final usageRate = totalFreeMins > 0 ? allocatedMins / totalFreeMins : 0.0;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 概要カード
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                gradient: const LinearGradient(
                  colors: [Color(0xFF1E3A8A), Color(0xFF3B82F6)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
              ),
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '今日の学修キャパシティ',
                    style: TextStyle(color: Colors.white70, fontSize: 14, fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${(allocatedMins / 60).toStringAsFixed(1)} / ${(totalFreeMins / 60).toStringAsFixed(1)} 時間割り当て済み',
                        style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        '${(usageRate * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(color: Color(0xFFF59E0B), fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: usageRate,
                      backgroundColor: Colors.white24,
                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFF59E0B)),
                      minHeight: 8,
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'AIが生活リズムと空き時間を分析し、優先度の高い課題を最適な時間帯に配置しました。',
                    style: TextStyle(color: Colors.white70, fontSize: 12, height: 1.4),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            '⏰ 本日のタイムスケジュール提案',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 12),
          if (suggestions.allocations.isEmpty)
            _buildEmptyState('今日の予定や空き時間に割り当てるべき未完了の課題はありません。すばらしい！')
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: suggestions.allocations.length,
              itemBuilder: (context, index) {
                final allocation = suggestions.allocations[index];
                final startStr = '${allocation.timeSlot.start.hour.toString().padLeft(2, '0')}:${allocation.timeSlot.start.minute.toString().padLeft(2, '0')}';
                final endStr = '${allocation.timeSlot.end.hour.toString().padLeft(2, '0')}:${allocation.timeSlot.end.minute.toString().padLeft(2, '0')}';
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 1,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // 時間表示
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            children: [
                              Text(startStr, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF1D4ED8), fontSize: 16)),
                              const Icon(Icons.arrow_downward, size: 12, color: Color(0xFF3B82F6)),
                              Text(endStr, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF1D4ED8), fontSize: 16)),
                            ],
                          ),
                        ),
                        const SizedBox(width: 16),
                        // 課題詳細
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                allocation.assignment.courseName,
                                style: const TextStyle(color: Color(0xFF64748B), fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                allocation.assignment.title,
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF0F172A)),
                              ),
                              const SizedBox(height: 8),
                              Row(
                                children: [
                                  const Icon(Icons.timer_outlined, size: 14, color: Color(0xFF94A3B8)),
                                  const SizedBox(width: 4),
                                  Text(
                                    '取り組み時間: ${allocation.allocatedMinutes}分',
                                    style: const TextStyle(fontSize: 13, color: Color(0xFF475569)),
                                  ),
                                  const Spacer(),
                                  Checkbox(
                                    value: allocation.assignment.isCompleted,
                                    activeColor: const Color(0xFF388E3C),
                                    onChanged: (_) => _toggleAssignmentCompleted(allocation.assignment.id),
                                  ),
                                  const Text('完了', style: TextStyle(fontSize: 13, color: Color(0xFF475569))),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
          const SizedBox(height: 24),
          const Text(
            '⚠️ 今日割り当て切れなかった課題',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 12),
          if (suggestions.remainingAssignments.isEmpty)
            _buildEmptyState('すべての課題がスケジュール内に割り当てられました。')
          else
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: suggestions.remainingAssignments.length,
              itemBuilder: (context, index) {
                final assignment = suggestions.remainingAssignments[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  elevation: 1,
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    title: Text(assignment.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    subtitle: Text('${assignment.courseName} • 推定: ${assignment.estimatedHours}時間\n${_formatRemainingTime(assignment.dueDate)}'),
                    isThreeLine: true,
                    trailing: Checkbox(
                      value: assignment.isCompleted,
                      activeColor: const Color(0xFF388E3C),
                      onChanged: (_) => _toggleAssignmentCompleted(assignment.id),
                    ),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }

  Widget _buildAssignmentsTab(List<Assignment> assignments) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 重み調整パネル
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.tune, color: Color(0xFF1E3A8A)),
                      SizedBox(width: 8),
                      Text(
                        '優先度計算の重みカスタマイズ (AI調整)',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E3A8A)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text('重要度の重み: ${_importanceWeight.toStringAsFixed(1)} (講義における重要性)'),
                  Slider(
                    value: _importanceWeight,
                    min: 0,
                    max: 10,
                    divisions: 10,
                    activeColor: const Color(0xFF1E3A8A),
                    onChanged: (val) {
                      setState(() {
                        _importanceWeight = val;
                      });
                    },
                  ),
                  Text('緊急度（締め切り）の重み: ${_urgencyWeight.toStringAsFixed(1)} (残り時間)'),
                  Slider(
                    value: _urgencyWeight,
                    min: 0,
                    max: 10,
                    divisions: 10,
                    activeColor: const Color(0xFF1E3A8A),
                    onChanged: (val) {
                      setState(() {
                        _urgencyWeight = val;
                      });
                    },
                  ),
                  const Text(
                    '※ 重みを変更すると、課題の優先度スコアがリアルタイムに更新され、今日のスケジュール配置が動的に切り替わります。',
                    style: TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.4),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            '📋 CLEカレンダー課題一覧 (優先度順)',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 12),
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: assignments.length,
            itemBuilder: (context, index) {
              final a = assignments[index];
              final score = _priorityEngine.calculateScore(a, DateTime.now(), _importanceWeight, _urgencyWeight);
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: a.isCompleted
                      ? BorderSide.none
                      : BorderSide(color: Colors.grey.shade200, width: 1),
                ),
                elevation: a.isCompleted ? 0.5 : 1,
                color: a.isCompleted ? const Color(0xFFF1F5F9) : Colors.white,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  a.courseName,
                                  style: TextStyle(
                                    color: a.isCompleted ? Colors.grey : const Color(0xFF475569),
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const Spacer(),
                                PriorityBadge(score: score),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              a.title,
                              style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.bold,
                                color: a.isCompleted ? Colors.grey : const Color(0xFF0F172A),
                                decoration: a.isCompleted ? TextDecoration.lineThrough : null,
                              ),
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: [
                                Icon(Icons.event, size: 14, color: a.isCompleted ? Colors.grey : const Color(0xFFE57373)),
                                const SizedBox(width: 4),
                                Text(
                                  _formatRemainingTime(a.dueDate),
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: a.isCompleted ? Colors.grey : const Color(0xFFE57373),
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(width: 16),
                                Icon(Icons.timer_outlined, size: 14, color: a.isCompleted ? Colors.grey : const Color(0xFF64748B)),
                                const SizedBox(width: 4),
                                Text(
                                  '所要: ${a.estimatedHours}時間',
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: a.isCompleted ? Colors.grey : const Color(0xFF475569),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Checkbox(
                        value: a.isCompleted,
                        activeColor: const Color(0xFF388E3C),
                        onChanged: (_) => _toggleAssignmentCompleted(a.id),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildRoutineTab(List<TimeSlot> freeSlots) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 生活リズムシミュレータ
          Card(
            elevation: 2,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.bedtime, color: Color(0xFF1E3A8A)),
                      SizedBox(width: 8),
                      Text(
                        '生活リズムシミュレーター (睡眠時間)',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Color(0xFF1E3A8A)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text('就寝時刻 (目安): $_sleepStartHour:00'),
                  Slider(
                    value: _sleepStartHour.toDouble(),
                    min: 18,
                    max: 24,
                    divisions: 6,
                    activeColor: const Color(0xFF1E3A8A),
                    onChanged: (val) {
                      _updateSleepTime(val.toInt(), _sleepEndHour);
                    },
                  ),
                  Text('起床時刻 (目安): $_sleepEndHour:00'),
                  Slider(
                    value: _sleepEndHour.toDouble(),
                    min: 4,
                    max: 11,
                    divisions: 7,
                    activeColor: const Color(0xFF1E3A8A),
                    onChanged: (val) {
                      _updateSleepTime(_sleepStartHour, val.toInt());
                    },
                  ),
                  const Text(
                    '※ 睡眠時間を変更すると、日中の活動可能時間（空き時間）が自動計算され、今日やるべきことのタイムスケジュールが即座に調整されます。',
                    style: TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.4),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            '📅 本日の固定予定 (授業・アルバイトなど)',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 8),
          const Text(
            'これらの時間帯は「今日やるべきこと」の学修時間から自動で除外されます。',
            style: TextStyle(fontSize: 12, color: Color(0xFF64748B)),
          ),
          const SizedBox(height: 12),
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _events.length,
            itemBuilder: (context, index) {
              final event = _events[index];
              final startStr = '${event.startTime.hour.toString().padLeft(2, '0')}:${event.startTime.minute.toString().padLeft(2, '0')}';
              final endStr = '${event.endTime.hour.toString().padLeft(2, '0')}:${event.endTime.minute.toString().padLeft(2, '0')}';
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                elevation: 1,
                child: ListTile(
                  leading: Icon(
                    event.isClass ? Icons.school : Icons.work,
                    color: event.isClass ? const Color(0xFF3B82F6) : const Color(0xFFF59E0B),
                  ),
                  title: Text(event.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  subtitle: Text('$startStr - $endStr'),
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: event.isClass ? const Color(0xFFEFF6FF) : const Color(0xFFFFFBEB),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      event.isClass ? '授業' : 'その他',
                      style: TextStyle(
                        fontSize: 11,
                        color: event.isClass ? const Color(0xFF1D4ED8) : const Color(0xFFB45309),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
          const SizedBox(height: 24),
          const Text(
            '🔍 計算された空き時間スロット',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 12),
          if (freeSlots.isEmpty)
            _buildEmptyState('今日は空き時間がありません。生活リズムを見直すか、予定を調整してください。')
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: freeSlots.map((slot) {
                return Chip(
                  backgroundColor: const Color(0xFFF0FDF4),
                  side: const BorderSide(color: Color(0xFFBBF7D0)),
                  label: Text(
                    '${slot.toString()} (${slot.duration.inMinutes}分)',
                    style: const TextStyle(color: Color(0xFF166534), fontSize: 13, fontWeight: FontWeight.bold),
                  ),
                  avatar: const Icon(Icons.check_circle_outline, color: Color(0xFF166534), size: 16),
                );
              }).toList(),
            ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(String text) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Center(
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: const TextStyle(color: Color(0xFF64748B), fontSize: 13, height: 1.4),
        ),
      ),
    );
  }
}
