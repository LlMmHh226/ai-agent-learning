import unittest
from contextlib import redirect_stdout
from io import StringIO

from learning.rag.step_16h_01_ngram_eval_baseline import (
    RetrievalEvalCase,
    evaluate_retriever,
)


class RetrievalEvalTests(unittest.TestCase):
    def test_calculates_recall_and_micro_precision(self) -> None:
        cases = [
            RetrievalEvalCase("问题一", "a.md"),
            RetrievalEvalCase("问题二", "c.md"),
        ]
        results_by_question = {
            "问题一": ["a.md", "b.md"],
            "问题二": ["b.md"],
        }

        with redirect_stdout(StringIO()):
            metrics = evaluate_retriever(
                cases=cases,
                retrieve_sources=lambda question, k: results_by_question[
                    question
                ][:k],
                k=2,
            )

        self.assertEqual(metrics.recall_at_k, 0.5)
        self.assertAlmostEqual(metrics.precision_at_k, 1 / 3)
        self.assertGreaterEqual(metrics.average_latency_ms, 0.0)

    def test_rejects_empty_eval_cases(self) -> None:
        with self.assertRaises(ValueError):
            evaluate_retriever(
                cases=[],
                retrieve_sources=lambda question, k: [],
                k=1,
            )


if __name__ == "__main__":
    unittest.main()
