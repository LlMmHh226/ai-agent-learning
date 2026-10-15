import unittest
from contextlib import redirect_stdout
from io import StringIO

from learning.rag.step_17c_02_holdout_eval import (
    HOLDOUT_CASES,
    HoldoutCase,
    evaluate_holdout,
    validate_holdout_cases,
)
from learning.rag.step_17b_dense_score_eval import SCORE_CASES


class HoldoutEvalTests(unittest.TestCase):
    def test_holdout_questions_do_not_repeat_development_questions(self) -> None:
        validate_holdout_cases(
            HOLDOUT_CASES,
            {case.question for case in SCORE_CASES},
        )

    def test_counts_positive_hits_and_negative_empty_results_separately(self) -> None:
        cases = [
            HoldoutCase("有答案", "a.md", "资料包含答案"),
            HoldoutCase("无答案", None, "资料缺少答案"),
        ]

        with redirect_stdout(StringIO()):
            metrics = evaluate_holdout(
                cases,
                lambda question: ["a.md"] if question == "有答案" else [],
            )

        self.assertEqual(metrics.positive_correct, 1)
        self.assertEqual(metrics.positive_total, 1)
        self.assertEqual(metrics.negative_correct, 1)
        self.assertEqual(metrics.negative_total, 1)


if __name__ == "__main__":
    unittest.main()
