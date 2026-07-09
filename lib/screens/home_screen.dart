import 'package:flutter/material.dart';
import 'learning_priority_screen.dart';
import 'member_a_screen.dart';
import 'member_b_screen.dart';

class MyHomePage extends StatelessWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '学修支援システム ポータル',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF0F172A)),
            ),
            const SizedBox(height: 8),
            const Text(
              '各担当メンバーの機能へアクセスできます。',
              style: TextStyle(fontSize: 14, color: Color(0xFF475569)),
            ),
            const SizedBox(height: 28),
            
            _buildMenuCard(
              context: context,
              title: '学習優先順位AI (あなたの担当)',
              description: 'CLEカレンダーから課題を同期し、生活リズムと空き時間を考慮して「今日やるべきこと」を優先度順に自動算出します。',
              icon: Icons.auto_awesome_rounded,
              color: const Color(0xFF1E3A8A),
              destination: const LearningPriorityScreen(),
            ),
            const SizedBox(height: 16),
            _buildMenuCard(
              context: context,
              title: '学修計画・類題生成 (メンバーA担当)',
              description: '目標に合わせた学習計画を自動生成し、習熟度に合わせた類題を生成して学力を補強します。',
              icon: Icons.menu_book_rounded,
              color: const Color(0xFF0D9488),
              destination: const MemberAScreen(),
            ),
            const SizedBox(height: 16),
            _buildMenuCard(
              context: context,
              title: 'ログイン・授業・資料・DB (メンバーB担当)',
              description: 'ユーザーログイン、授業登録、学習資料のアップロード、要約、重要語句抽出、練習問題の生成およびデータベース管理。',
              icon: Icons.storage_rounded,
              color: const Color(0xFF4F46E5),
              destination: const MemberBScreen(),
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
                  color: color.withOpacity(0.1),
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

