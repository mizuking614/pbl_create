import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/assignment.dart';
import '../services/cle_calendar_service.dart';

class MemberAScreen extends StatefulWidget {
  const MemberAScreen({super.key});

  @override
  State<MemberAScreen> createState() => _MemberAScreenState();
}

class _MemberAScreenState extends State<MemberAScreen> {
  final _goalController = TextEditingController();
  final _topicController = TextEditingController();
  int _days = 7;
  List<String> _plan = [];
  List<String> _questions = [];
  List<Assignment> _assignments = [];
  List<String> _courses = [];
  List<String> _materials = [];
  String _selectedCourse = 'all';
  String _selectedMaterial = 'all';
  bool _isLoading = true;

  @override
  void dispose() {
    _goalController.dispose();
    _topicController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _loadResults();
    _loadAssignments();
    _loadContextData();
  }

  Future<void> _loadAssignments() async {
    final assignments = await CleCalendarService().fetchAssignments();
    if (!mounted) return;
    setState(() {
      _assignments = assignments.where((assignment) => !assignment.isCompleted).toList();
      _isLoading = false;
    });
  }

  Future<void> _loadContextData() async {
    final prefs = await SharedPreferences.getInstance();
    final courses = prefs.getStringList('member_b_courses') ?? [];
    final materials = prefs.getStringList('member_b_materials') ?? [];
    if (!mounted) return;
    setState(() {
      _courses = courses;
      _materials = materials;
      if (_courses.isNotEmpty && !_courses.contains(_selectedCourse)) {
        _selectedCourse = _courses.first;
      }
      if (_materials.isNotEmpty && !_materials.contains(_selectedMaterial)) {
        _selectedMaterial = _materials.first;
      }
    });
  }

  Future<void> _loadResults() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) return;
    setState(() {
      _plan = prefs.getStringList('study_plan') ?? [];
      _questions = prefs.getStringList('study_questions') ?? [];
    });
  }

  Future<void> _saveResults() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('study_plan', _plan);
    await prefs.setStringList('study_questions', _questions);
  }

  List<Assignment> _getContextAssignments() {
    if (_selectedCourse == 'all' && _selectedMaterial == 'all') {
      return _assignments;
    }

    final courseFilter = _selectedCourse == 'all' ? null : _selectedCourse;
    final materialFilter = _selectedMaterial == 'all' ? null : _selectedMaterial;

    return _assignments.where((assignment) {
      final matchesCourse = courseFilter == null ||
          assignment.courseName == courseFilter ||
          assignment.courseName.toLowerCase().contains(courseFilter.toLowerCase());
      final matchesMaterial = materialFilter == null ||
          assignment.title.toLowerCase().contains(materialFilter.toLowerCase()) ||
          materialFilter.toLowerCase().contains(assignment.title.toLowerCase());
      return matchesCourse && matchesMaterial;
    }).toList();
  }

  void _createPlan() {
    final goal = _goalController.text.trim();
    if (goal.isEmpty) return;

    final contextAssignments = _getContextAssignments();
    final selectedCourseText = _selectedCourse == 'all' ? '全体' : _selectedCourse;
    final selectedMaterialText = _selectedMaterial == 'all' ? '学習資料' : _selectedMaterial;

    setState(() {
      if (contextAssignments.isEmpty) {
        _plan = [
          '1日目: $goal の全体像を確認する（対象: $selectedCourseText / $selectedMaterialText）',
          '2〜${(_days / 2).ceil()}日目: 基本用語と重要概念を整理する',
          '${(_days / 2).ceil() + 1}〜${_days - 1}日目: 例題と関連資料を確認しながら復習する',
          '最終日: 間違いを整理して理解度を確認する',
        ];
      } else {
        final tasks = [...contextAssignments]..sort((a, b) => a.dueDate.compareTo(b.dueDate));
        _plan = tasks.take(_days).toList().asMap().entries.map((entry) {
          final assignment = entry.value;
          return '${entry.key + 1}日目: ${assignment.title} (${assignment.courseName}) に取り組む・締切 ${assignment.dueDate.month}/${assignment.dueDate.day}';
        }).toList();
      }
    });
    _saveResults();
  }

  void _createQuestions() {
    final topic = _topicController.text.trim();
    if (topic.isEmpty) return;

    final contextAssignments = _getContextAssignments();
    final contextLabel = _selectedMaterial == 'all'
        ? (_selectedCourse == 'all' ? '学習全体' : _selectedCourse)
        : _selectedMaterial;

    setState(() {
      _questions = [
        '「$topic」とは何か、${contextLabel}の観点から自分の言葉で説明してください。',
        '「$topic」が必要になる具体的な場面を1つ挙げ、${contextLabel}との関係を説明してください。',
        '「$topic」と関連する概念との違いを、${contextLabel}を例に挙げて説明してください。',
      ];
      for (final assignment in contextAssignments.where((item) => item.title.toLowerCase().contains(topic.toLowerCase())).take(2)) {
        _questions.add('課題「${assignment.title}」で扱う内容を、$topic と${contextLabel}の関係で説明してください。');
      }
    });
    _saveResults();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('学修計画・類題生成'), backgroundColor: const Color(0xFF0D9488), foregroundColor: Colors.white),
        body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('学習計画を作成', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('目標と期間を設定すると、取り組む順序を整理できます。'),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('資料連携', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  if (_courses.isNotEmpty)
                    DropdownButtonFormField<String>(
                      value: _courses.contains(_selectedCourse) ? _selectedCourse : 'all',
                      decoration: const InputDecoration(labelText: '授業', border: OutlineInputBorder()),
                      items: ['all', ..._courses].map((course) => DropdownMenuItem(
                        value: course,
                        child: Text(course == 'all' ? 'すべての授業' : course),
                      )).toList(),
                      onChanged: (value) => setState(() => _selectedCourse = value ?? 'all'),
                    ),
                  if (_courses.isNotEmpty) const SizedBox(height: 12),
                  if (_materials.isNotEmpty)
                    DropdownButtonFormField<String>(
                      value: _materials.contains(_selectedMaterial) ? _selectedMaterial : 'all',
                      decoration: const InputDecoration(labelText: '資料', border: OutlineInputBorder()),
                      items: ['all', ..._materials].map((material) => DropdownMenuItem(
                        value: material,
                        child: Text(material == 'all' ? 'すべての資料' : material),
                      )).toList(),
                      onChanged: (value) => setState(() => _selectedMaterial = value ?? 'all'),
                    ),
                  if (_courses.isEmpty && _materials.isEmpty)
                    const Text('保存済みの授業・資料がまだありません。授業・資料管理画面で登録すると、ここに反映されます。'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          TextField(controller: _goalController, decoration: const InputDecoration(labelText: '学習目標', hintText: '例: 情報理論の基礎を理解する', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          Row(children: [
            const Text('学習期間'),
            Expanded(child: Slider(value: _days.toDouble(), min: 2, max: 30, divisions: 28, label: '$_days日', onChanged: (value) => setState(() => _days = value.round()))),
            Text('$_days日'),
          ]),
          FilledButton.icon(onPressed: _createPlan, icon: const Icon(Icons.event_note), label: const Text('計画を作成')),
          if (_plan.isNotEmpty) ...[
            const SizedBox(height: 16),
            ..._plan.map((item) => Card(child: ListTile(leading: const Icon(Icons.check_circle_outline, color: Color(0xFF0D9488)), title: Text(item)))),
          ],
          const Divider(height: 36),
          const Text('類題を作成', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('練習したいテーマから確認問題を作成します。'),
          const SizedBox(height: 12),
          TextField(controller: _topicController, decoration: const InputDecoration(labelText: '学習テーマ', hintText: '例: エントロピー', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          FilledButton.icon(onPressed: _createQuestions, icon: const Icon(Icons.quiz_outlined), label: const Text('類題を作成')),
          if (_questions.isNotEmpty) ...[
            const SizedBox(height: 16),
            ..._questions.asMap().entries.map((entry) => Card(child: ListTile(leading: CircleAvatar(child: Text('${entry.key + 1}')), title: Text(entry.value)))),
          ],
        ],
      ),
    );
  }
}
