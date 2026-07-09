import '../models/assignment.dart';

class PriorityEngine {
  // 優先度スコアを計算し、ソートしたリストを返す
  // importanceWeight: 重要度の重み (1〜10)
  // urgencyWeight: 緊急度（締め切り）の重み (1〜10)
  List<Assignment> calculateAndSort({
    required List<Assignment> assignments,
    double importanceWeight = 5.0,
    double urgencyWeight = 5.0,
  }) {
    final uncompleted = assignments.where((a) => !a.isCompleted).toList();
    final completed = assignments.where((a) => a.isCompleted).toList();

    final now = DateTime.now();

    uncompleted.sort((a, b) {
      final scoreA = calculateScore(a, now, importanceWeight, urgencyWeight);
      final scoreB = calculateScore(b, now, importanceWeight, urgencyWeight);
      return scoreB.compareTo(scoreA); // 降順
    });

    return [...uncompleted, ...completed];
  }

  // 外部テストやバッジ表示でもスコアを使えるようにパブリックメソッドにする
  double calculateScore(
    Assignment assignment,
    DateTime now,
    double importanceWeight,
    double urgencyWeight,
  ) {
    if (assignment.isCompleted) return 0.0;

    // 1. 重要度スコア (1〜5) を 0〜100 に正規化
    final importanceScore = (assignment.importance / 5.0) * 100;

    // 2. 緊急度スコア (0〜100)
    final difference = assignment.dueDate.difference(now);
    double urgencyScore = 0.0;

    if (difference.isNegative) {
      urgencyScore = 100.0;
    } else {
      final hoursRemaining = difference.inHours;
      if (hoursRemaining <= 12) {
        urgencyScore = 100.0; // 12時間以内
      } else if (hoursRemaining <= 24) {
        urgencyScore = 90.0;  // 1日以内
      } else if (hoursRemaining <= 72) {
        urgencyScore = 70.0;  // 3日以内
      } else if (hoursRemaining <= 168) {
        urgencyScore = 40.0;  // 1週間以内
      } else {
        urgencyScore = 10.0;  // それ以上先
      }
    }

    final totalWeight = importanceWeight + urgencyWeight;
    if (totalWeight == 0) return 0.0;

    return (importanceScore * importanceWeight + urgencyScore * urgencyWeight) / totalWeight;
  }
}
