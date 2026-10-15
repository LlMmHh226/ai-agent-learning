import unittest

from learning.rag.step_17b_dense_score_eval import DenseScoreObservation
from learning.rag.step_17d_dense_holdout import (
    FIXED_THRESHOLDS,
    evaluate_fixed_threshold,
)


class DenseHoldoutTests(unittest.TestCase):
    def test_fixed_thresholds_match_previously_discussed_values(self) -> None:
        self.assertEqual(FIXED_THRESHOLDS, (0.30, 0.40, 0.46))

    def test_wrong_source_is_not_counted_as_correct_positive(self) -> None:
        observations = [
            DenseScoreObservation("正例一", "a.md", "a.md", 0.5),
            DenseScoreObservation("正例二", "a.md", "b.md", 0.5),
            DenseScoreObservation("正例三", "a.md", "a.md", 0.2),
            DenseScoreObservation("负例一", None, "a.md", 0.5),
            DenseScoreObservation("负例二", None, "a.md", 0.2),
        ]

        metrics = evaluate_fixed_threshold(observations, threshold=0.4)

        self.assertEqual(metrics.positive_correct, 1)
        self.assertEqual(metrics.positive_wrong_source, 1)
        self.assertEqual(metrics.positive_rejected, 1)
        self.assertEqual(metrics.negative_passed, 1)
        self.assertEqual(metrics.negative_rejected, 1)


if __name__ == "__main__":
    unittest.main()
