import unittest

from learning.rag.step_17b_dense_score_eval import DenseScoreObservation
from learning.rag.step_17c_01_threshold_tradeoff import evaluate_threshold


class ThresholdTradeoffTests(unittest.TestCase):
    def test_equal_score_is_passed_and_labels_are_counted_separately(self) -> None:
        observations = [
            DenseScoreObservation("正例", "shipping.md", "shipping.md", 0.40),
            DenseScoreObservation("负例", None, "shipping.md", 0.40),
            DenseScoreObservation("另一负例", None, "products.md", 0.20),
        ]

        result = evaluate_threshold(observations, threshold=0.40)

        self.assertEqual(result.positive_passed, 1)
        self.assertEqual(result.positive_rejected, 0)
        self.assertEqual(result.negative_passed, 1)
        self.assertEqual(result.negative_rejected, 1)


if __name__ == "__main__":
    unittest.main()
