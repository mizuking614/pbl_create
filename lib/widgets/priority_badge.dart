import 'package:flutter/material.dart';

class PriorityBadge extends StatelessWidget {
  final double score;

  const PriorityBadge({super.key, required this.score});

  @override
  Widget build(BuildContext context) {
    Color color;
    String text;

    if (score >= 70) {
      color = const Color(0xFFD32F2F); // 深い赤
      text = '高優先度';
    } else if (score >= 40) {
      color = const Color(0xFFF57C00); // オレンジ
      text = '中優先度';
    } else if (score > 0) {
      color = const Color(0xFF388E3C); // 緑
      text = '低優先度';
    } else {
      color = Colors.grey.shade600;
      text = '完了';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.5), width: 1),
      ),
      child: Text(
        '$text (${score.toStringAsFixed(0)})',
        style: TextStyle(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
