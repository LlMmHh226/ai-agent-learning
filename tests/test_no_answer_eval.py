import unittest
from contextlib import redirect_stdout
from io import StringIO

from learning.rag.step_17a_no_answer_eval import (
    NoAnswerEvalCase,
    evaluate_no_answer_cases,
)


class NoAnswerEvalTests(unittest.TestCase):
    def test_counts_empty_results_as_refusal(self) -> None:
        cases = [
            NoAnswerEvalCase("没有答案的问题一", "未收录"),
            NoAnswerEvalCase("没有答案的问题二", "未收录"),
        ]

        with redirect_stdout(StringIO()):
            metrics = evaluate_no_answer_cases(
                cases=cases,
                retrieve_sources=lambda question: (
                    [] if question.endswith("一") else ["irrelevant.md"]
                ),
            )

        self.assertEqual(metrics.correctly_rejected, 1)
        self.assertEqual(metrics.total, 2)
        self.assertEqual(metrics.refusal_rate, 0.5)

    def test_requires_at_least_one_case(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_no_answer_cases([], lambda question: [])


if __name__ == "__main__":
    unittest.main()
