import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'learning_priority_screen.dart';
import 'member_a_screen.dart';
import 'member_b_screen.dart';

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final TextEditingController _urlController = TextEditingController();
  String _currentUrl = '';
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUrl();
  }

  Future<void> _loadUrl() async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString('cle_ics_url') ?? '';
    if (!mounted) return;
    setState(() {
      _currentUrl = stored;
      _urlController.text = stored;
      _isLoading = false;
    });
  }

  Future<void> _saveUrl() async {
    final url = _urlController.text.trim();
    final prefs = await SharedPreferences.getInstance();
    if (url.isEmpty) {
      await prefs.remove('cle_ics_url');
    } else {
      await prefs.setString('cle_ics_url', url);
    }
    if (!mounted) return;
    setState(() {
      _currentUrl = url;
    });
    final message = url.isEmpty ? 'CLE URLをクリアしました。' : 'CLE URLを保存しました。';
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _copyUrl() async {
    if (_currentUrl.isEmpty) return;
    await Clipboard.setData(ClipboardData(text: _currentUrl));
    if (!mounted) return;
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('CLE URLをコピーしました。')));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        title: Text(
          widget.title,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF0F172A)),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'AIタスク管理ポータル',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '日々の学習とタスクを管理するための機能へアクセスできます。',
                    style: TextStyle(fontSize: 14, color: Color(0xFF475569)),
                  ),
                  const SizedBox(height: 24),
                  _buildUrlCard(),
                  const SizedBox(height: 28),
                  _buildMenuCard(
                    context: context,
                    title: '学習優先順位AI',
                    description:
                        'CLEカレンダーから課題を同期し、生活リズムと空き時間を考慮して「今日やるべきこと」を優先度順に自動算出します。',
                    icon: Icons.auto_awesome_rounded,
                    color: const Color(0xFF1E3A8A),
                    destination: const LearningPriorityScreen(),
                  ),
                  const SizedBox(height: 16),
                  _buildMenuCard(
                    context: context,
                    title: '学修計画・類題生成',
                    description: '目標に合わせた学習計画を自動生成し、習熟度に合わせた類題を生成して学力を補強します。',
                    icon: Icons.menu_book_rounded,
                    color: const Color(0xFF0D9488),
                    destination: const MemberAScreen(),
                  ),
                  const SizedBox(height: 16),
                  _buildMenuCard(
                    context: context,
                    title: '授業・資料管理',
                    description: '授業と学習資料を登録し、端末またはローカルAPIへ保存して学習タスクの整理に利用します。',
                    icon: Icons.storage_rounded,
                    color: const Color(0xFF4F46E5),
                    destination: const MemberBScreen(),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildUrlCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'CLE共有URLの設定',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0F172A),
              ),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'https://www.cle.osaka-u.ac.jp/.../learn.ics',
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                ElevatedButton(
                  onPressed: _saveUrl,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0F172A),
                  ),
                  child: const Text('保存'),
                ),
                const SizedBox(width: 12),
                OutlinedButton(
                  onPressed: () {
                    setState(() {
                      _urlController.text = _currentUrl;
                    });
                  },
                  child: const Text('リセット'),
                ),
                const SizedBox(width: 12),
                if (_currentUrl.isNotEmpty)
                  IconButton(
                    onPressed: _copyUrl,
                    icon: const Icon(Icons.copy, color: Color(0xFF0F172A)),
                    tooltip: 'URLをコピー',
                  ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              _currentUrl.isEmpty
                  ? '現在CLE共有URLは設定されていません。'
                  : '現在のCLE URL: $_currentUrl',
              style: const TextStyle(color: Color(0xFF475569)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuCard({
    required BuildContext context,
    required String title,
    required String description,
    required IconData icon,
    required Color color,
    required Widget destination,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => destination),
          );
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(icon, color: color, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      description,
                      style: const TextStyle(
                        fontSize: 13,
                        color: Color(0xFF64748B),
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8),
              const Icon(Icons.chevron_right, color: Color(0xFF94A3B8)),
            ],
          ),
        ),
      ),
    );
  }
}
