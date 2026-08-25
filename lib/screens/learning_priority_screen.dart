import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
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
  String _calendarStatusMessage = '';

  double _importanceWeight = 5.0;
  double _urgencyWeight = 5.0;
  String _assignmentFilter = '';
  String _assignmentCategoryFilter = 'all';

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

    final prefs = await SharedPreferences.getInstance();
    final savedRoutine = prefs.getString('user_routine');
    if (savedRoutine != null) {
      try {
        _routine = UserRoutine.fromMap(jsonDecode(savedRoutine) as Map<String, dynamic>);
      } catch (_) {
        _routine = UserRoutine.defaultRoutine();
      }
    }

    final savedCompletions = <String, bool>{};
    final completionJson = prefs.getString('assignment_completions');
    if (completionJson != null) {
      try {
        final decoded = jsonDecode(completionJson) as Map<String, dynamic>;
        decoded.forEach((id, value) {
          savedCompletions[id] = value == true;
        });
      } catch (_) {
        savedCompletions.clear();
      }
    }

    final today = DateTime.now();
    final assignments = await _calendarService.fetchAssignments();
    final events = await _calendarService.fetchScheduleEvents(today);
    _calendarStatusMessage = _calendarService.lastErrorMessage;
    final savedAssignments = prefs.getStringList('manual_assignments') ?? [];
    for (final encoded in savedAssignments) {
      try {
        assignments.add(Assignment.fromMap(jsonDecode(encoded) as Map<String, dynamic>));
      } catch (_) {}
    }

    for (final assignment in assignments) {
      assignment.isCompleted = savedCompletions[assignment.id] ?? assignment.isCompleted;
    }

    if (!mounted) return;
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
    _saveRoutine();
  }

  void _toggleAssignmentCompleted(String id) {
    setState(() {
      final index = _assignments.indexWhere((a) => a.id == id);
      if (index != -1) {
        _assignments[index].isCompleted = !_assignments[index].isCompleted;
      }
    });
    _saveAssignmentCompletions();
  }

  Future<void> _saveRoutine() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('user_routine', jsonEncode(_routine.toMap()));
  }

  Future<void> _saveAssignmentCompletions() async {
    final prefs = await SharedPreferences.getInstance();
    final completions = {
      for (final assignment in _assignments) assignment.id: assignment.isCompleted,
    };
    await prefs.setString('assignment_completions', jsonEncode(completions));
  }

  Future<void> _saveManualAssignments() async {
    final prefs = await SharedPreferences.getInstance();
    final manual = _assignments
        .where((assignment) => assignment.id.startsWith('manual_'))
        .map((assignment) => jsonEncode(assignment.toMap()))
        .toList();
    await prefs.setStringList('manual_assignments', manual);
  }

  Future<void> _editManualAssignment(Assignment assignment) async {
    if (!assignment.id.startsWith('manual_')) return;
    final titleController = TextEditingController(text: assignment.title);
    final courseController = TextEditingController(text: assignment.courseName);
    final hoursController = TextEditingController(text: assignment.estimatedHours.toString());
    var importance = assignment.importance;
    var dueDate = assignment.dueDate;
    final updated = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('タスクを編集'),
          content: SingleChildScrollView(child: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(controller: titleController, decoration: const InputDecoration(labelText: 'タスク名')),
            TextField(controller: courseController, decoration: const InputDecoration(labelText: 'カテゴリ・授業名')),
            TextField(controller: hoursController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: '所要時間（時間）')),
            ListTile(contentPadding: EdgeInsets.zero, title: const Text('締切'), subtitle: Text('${dueDate.year}/${dueDate.month}/${dueDate.day}'), onTap: () async { final selected = await showDatePicker(context: context, firstDate: DateTime.now().subtract(const Duration(days: 150)), lastDate: DateTime.now().add(const Duration(days: 365)), initialDate: dueDate); if (selected != null) setDialogState(() => dueDate = DateTime(selected.year, selected.month, selected.day, 23, 59)); }),
            DropdownButtonFormField<int>(value: importance, decoration: const InputDecoration(labelText: '重要度'), items: [1, 2, 3, 4, 5].map((value) => DropdownMenuItem(value: value, child: Text('$value / 5'))).toList(), onChanged: (value) => setDialogState(() => importance = value ?? importance)),
          ])),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext, false), child: const Text('キャンセル')),
            FilledButton(onPressed: () { final title = titleController.text.trim(); final hours = double.tryParse(hoursController.text) ?? assignment.estimatedHours; if (title.isNotEmpty) { final index = _assignments.indexWhere((item) => item.id == assignment.id); if (index != -1) { _assignments[index] = Assignment(id: assignment.id, title: title, courseName: courseController.text.trim().isEmpty ? '手入力タスク' : courseController.text.trim(), dueDate: dueDate, estimatedHours: hours.clamp(0.25, 24), importance: importance, isCompleted: assignment.isCompleted); } Navigator.pop(dialogContext, true); } }, child: const Text('保存')),
          ],
        ),
      ),
    );
    titleController.dispose();
    courseController.dispose();
    hoursController.dispose();
    if (updated == true && mounted) {
      setState(() {});
      await _saveManualAssignments();
    }
  }

  Future<void> _deleteManualAssignment(Assignment assignment) async {
    if (!assignment.id.startsWith('manual_')) return;
    setState(() => _assignments.removeWhere((item) => item.id == assignment.id));
    await _saveManualAssignments();
    await _saveAssignmentCompletions();
  }

  Future<void> _showAddAssignmentDialog() async {
    final titleController = TextEditingController();
    final courseController = TextEditingController();
    final hoursController = TextEditingController(text: '1');
    DateTime dueDate = DateTime.now().add(const Duration(days: 1));
    int importance = 3;

    final assignment = await showDialog<Assignment>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('タスクを追加'),
          content: SingleChildScrollView(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              TextField(controller: titleController, decoration: const InputDecoration(labelText: 'タスク名')),
              TextField(controller: courseController, decoration: const InputDecoration(labelText: 'カテゴリ・授業名')),
              TextField(controller: hoursController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: '所要時間（時間）')),
              const SizedBox(height: 12),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('締切'),
                subtitle: Text('${dueDate.year}/${dueDate.month}/${dueDate.day}'),
                trailing: const Icon(Icons.calendar_today),
                onTap: () async {
                  final selected = await showDatePicker(context: context, firstDate: DateTime.now().subtract(const Duration(days: 150)), lastDate: DateTime.now().add(const Duration(days: 365)), initialDate: dueDate);
                  if (selected != null) setDialogState(() => dueDate = DateTime(selected.year, selected.month, selected.day, 23, 59));
                },
              ),
              DropdownButtonFormField<int>(value: importance, decoration: const InputDecoration(labelText: '重要度'), items: [1, 2, 3, 4, 5].map((value) => DropdownMenuItem(value: value, child: Text('$value / 5'))).toList(), onChanged: (value) => setDialogState(() => importance = value ?? 3)),
            ]),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('キャンセル')),
            FilledButton(onPressed: () { final title = titleController.text.trim(); final hours = double.tryParse(hoursController.text) ?? 1; if (title.isNotEmpty) Navigator.pop(dialogContext, Assignment(id: 'manual_${DateTime.now().microsecondsSinceEpoch}', title: title, courseName: courseController.text.trim().isEmpty ? '手入力タスク' : courseController.text.trim(), dueDate: dueDate, estimatedHours: hours.clamp(0.25, 24), importance: importance)); }, child: const Text('追加')),
          ],
        ),
      ),
    );
    titleController.dispose();
    courseController.dispose();
    hoursController.dispose();
    if (assignment == null || !mounted) return;
    setState(() => _assignments.add(assignment));
    await _saveManualAssignments();
    await _saveAssignmentCompletions();
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
          actions: [
            IconButton(onPressed: _showAddAssignmentDialog, icon: const Icon(Icons.add_task), tooltip: 'タスクを追加'),
          ],
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
      body: Column(
        children: [
          if (_calendarStatusMessage.isNotEmpty)
            Container(
              width: double.infinity,
              color: const Color(0xFFFEF2F2),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.info_outline, color: Color(0xFFB91C1C), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _calendarStatusMessage,
                      style: const TextStyle(color: Color(0xFF7F1D1D), fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildTodayTab(suggestions),
                _buildAssignmentsTab(sortedAssignments),
                _buildRoutineTab(freeSlots),
              ],
            ),
          ),
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

  List<String> get _assignmentCategories {
    final categories = <String>{};
    for (final assignment in _assignments) {
      final category = assignment.courseName.trim();
      if (category.isNotEmpty) {
        categories.add(category);
      }
    }
    final sorted = categories.toList()..sort();
    return ['all', ...sorted];
  }

  Widget _buildAssignmentsTab(List<Assignment> assignments) {
    final query = _assignmentFilter.trim().toLowerCase();
    final categoryFilteredAssignments = _assignmentCategoryFilter == 'all'
        ? assignments
        : assignments.where((assignment) => assignment.courseName == _assignmentCategoryFilter).toList();
    final filteredAssignments = query.isEmpty
        ? categoryFilteredAssignments
        : categoryFilteredAssignments.where((assignment) => assignment.title.toLowerCase().contains(query) || assignment.courseName.toLowerCase().contains(query)).toList();
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
            'カテゴリで絞り込み',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF475569)),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: _assignmentCategories.contains(_assignmentCategoryFilter) ? _assignmentCategoryFilter : 'all',
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.filter_list),
            ),
            items: _assignmentCategories.map((category) {
              final label = category == 'all' ? 'すべて' : category;
              return DropdownMenuItem<String>(value: category, child: Text(label));
            }).toList(),
            onChanged: (value) {
              setState(() {
                _assignmentCategoryFilter = value ?? 'all';
              });
            },
          ),
          const SizedBox(height: 16),
          TextField(
            decoration: const InputDecoration(labelText: '課題を検索', hintText: '課題名・授業名', prefixIcon: Icon(Icons.search), border: OutlineInputBorder()),
            onChanged: (value) => setState(() => _assignmentFilter = value),
          ),
          const SizedBox(height: 16),
          const Text(
            '📋 CLEカレンダー課題一覧 (優先度順)',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
          ),
          const SizedBox(height: 12),
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: filteredAssignments.length,
            itemBuilder: (context, index) {
              final a = filteredAssignments[index];
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
                      if (a.id.startsWith('manual_')) ...[
                        IconButton(onPressed: () => _editManualAssignment(a), icon: const Icon(Icons.edit_outlined), tooltip: '編集'),
                        IconButton(onPressed: () => _deleteManualAssignment(a), icon: const Icon(Icons.delete_outline), tooltip: '削除'),
                      ],
                      Checkbox(value: a.isCompleted, activeColor: const Color(0xFF388E3C), onChanged: (_) => _toggleAssignmentCompleted(a.id)),
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
