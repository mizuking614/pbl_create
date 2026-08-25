import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class MemberBScreen extends StatefulWidget {
  const MemberBScreen({super.key});

  @override
  State<MemberBScreen> createState() => _MemberBScreenState();
}

class _MemberBScreenState extends State<MemberBScreen> {
  final _courseController = TextEditingController();
  final _materialController = TextEditingController();
  List<String> _courses = [];
  List<String> _materials = [];
  String _statusMessage = '';
  bool _isUploading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _courseController.dispose();
    _materialController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    final prefs = await SharedPreferences.getInstance();
    _courses = prefs.getStringList('member_b_courses') ?? [];
    _materials = prefs.getStringList('member_b_materials') ?? [];
    try {
      final courses = await http.get(Uri.parse('http://127.0.0.1:8000/api/courses'));
      final materials = await http.get(Uri.parse('http://127.0.0.1:8000/api/materials'));
      if (courses.statusCode == 200 && materials.statusCode == 200) {
        final courseData = jsonDecode(courses.body) as Map<String, dynamic>;
        final materialData = jsonDecode(materials.body) as Map<String, dynamic>;
        _courses = (courseData['courses'] as List<dynamic>).map((item) => (item as Map<String, dynamic>)['name'].toString()).toList();
        _materials = (materialData['materials'] as List<dynamic>).map((item) => (item as Map<String, dynamic>)['name'].toString()).toList();
        _statusMessage = 'ローカルAPIと同期しました。';
      }
    } catch (_) {
      _statusMessage = 'API未接続のため、端末内に保存します。';
    }
    if (!mounted) return;
    setState(() {});
  }

  Future<void> _saveLocal() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList('member_b_courses', _courses);
    await prefs.setStringList('member_b_materials', _materials);
  }

  Future<void> _addRecord(String type, TextEditingController controller, List<String> values) async {
    final value = controller.text.trim();
    if (value.isEmpty || values.contains(value)) return;
    setState(() { values.add(value); controller.clear(); });
    await _saveLocal();
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/$type'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'name': value}),
      );
      if (response.statusCode == 201) {
        setState(() => _statusMessage = 'ローカルAPIへ保存しました。');
      }
    } catch (_) {}
  }

  Future<void> _uploadMaterial() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'txt', 'md', 'csv', 'png', 'jpg', 'jpeg', 'docx', 'bmp', 'tif', 'tiff'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;

    final file = result.files.first;
    final fileBytes = file.bytes;
    if (fileBytes == null) return;

    setState(() => _isUploading = true);
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/extract-text'),
        headers: {
          'X-File-Name': file.name,
          'X-File-Type': _mimeTypeFor(file.name),
        },
        body: fileBytes,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final extractedText = (data['text'] ?? '') as String;
        final materialName = file.name.split('.').first.trim();
        if (materialName.isNotEmpty && !_materials.contains(materialName)) {
          setState(() {
            _materials.add(materialName);
            _statusMessage = '資料をアップロードして本文を抽出しました。';
          });
          await _saveLocal();
        }
        if (extractedText.isNotEmpty) {
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('本文を抽出しました: ${extractedText.length}文字')),
          );
        }
      } else {
        final errorData = jsonDecode(response.body) as Map<String, dynamic>;
        setState(() => _statusMessage = errorData['error']?.toString() ?? '資料のアップロードに失敗しました。');
      }
    } catch (_) {
      setState(() => _statusMessage = 'ローカルAPIに接続できないため、端末内に保存のみ行いました。');
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
  }

  String _mimeTypeFor(String fileName) {
    final extension = fileName.split('.').last.toLowerCase();
    switch (extension) {
      case 'pdf':
        return 'application/pdf';
      case 'txt':
      case 'md':
      case 'csv':
        return 'text/plain';
      case 'jpg':
      case 'jpeg':
        return 'image/jpeg';
      case 'png':
        return 'image/png';
      case 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      default:
        return 'application/octet-stream';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('授業・資料管理'), backgroundColor: const Color(0xFF4F46E5), foregroundColor: Colors.white),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('学習データ', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          const Text('授業と資料を登録すると、学習タスクの整理に利用できます。'),
          const SizedBox(height: 12),
          const Text('ローカルAPIと同期', style: TextStyle(fontWeight: FontWeight.bold)),
          if (_statusMessage.isNotEmpty) Padding(padding: const EdgeInsets.only(top: 8), child: Text(_statusMessage)),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: _isUploading ? null : _uploadMaterial,
            icon: _isUploading ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Icon(Icons.upload_file),
            label: Text(_isUploading ? 'アップロード中...' : '資料アップロード'),
          ),
          const SizedBox(height: 16),
          _buildCollectionCard('授業一覧', _courseController, _courses, 'courses', Icons.school_outlined),
          const SizedBox(height: 16),
          _buildCollectionCard('学習資料', _materialController, _materials, 'materials', Icons.description_outlined),
        ],
      ),
    );
  }

  Widget _buildCollectionCard(String title, TextEditingController controller, List<String> values, String type, IconData icon) {
    return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
      const SizedBox(height: 12),
      Row(children: [Expanded(child: TextField(controller: controller, decoration: InputDecoration(labelText: title == '授業一覧' ? '授業名' : '資料名', border: const OutlineInputBorder()))), const SizedBox(width: 8), IconButton.filled(onPressed: () => _addRecord(type, controller, values), icon: const Icon(Icons.add), tooltip: '追加')]),
      if (values.isEmpty) const Padding(padding: EdgeInsets.only(top: 12), child: Text('まだ登録されていません。')),
      ...values.map((value) => ListTile(contentPadding: EdgeInsets.zero, leading: Icon(icon, color: const Color(0xFF4F46E5)), title: Text(value))),
    ])));
  }
}
