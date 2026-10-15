import unittest

from app.rag.document_loader import Document
from learning.rag.step_17b_dense_score_eval import (
    DenseScoreCase,
    DenseScoreObservation,
    analyze_score_boundary,
    build_observations,
)


class DenseScoreEvalTests(unittest.TestCase):
    def test_builds_top_one_observation(self) -> None:
        documents = [
            Document("文档一", {"source": "a.md"}),
            Document("文档二", {"source": "b.md"}),
        ]

        observations = build_observations(
            cases=[DenseScoreCase("问题", "a.md")],
            query_vectors=[[1.0, 0.0]],
            documents=documents,
            document_vectors=[[1.0, 0.0], [0.0, 1.0]],
        )

        self.assertEqual(observations[0].top_source, "a.md")
        self.assertAlmostEqual(observations[0].top_score, 1.0)

    def test_finds_candidate_threshold_when_scores_do_not_overlap(self) -> None:
        boundary = analyze_score_boundary(
            [
                DenseScoreObservation("正例一", "a.md", "a.md", 0.8),
                DenseScoreObservation("正例二", "b.md", "b.md", 0.6),
                DenseScoreObservation("负例", None, "a.md", 0.4),
            ]
        )

        self.assertEqual(boundary.minimum_positive_score, 0.6)
        self.assertEqual(boundary.maximum_negative_score, 0.4)
        self.assertEqual(boundary.candidate_threshold, 0.5)

    def test_reports_overlap_without_candidate_threshold(self) -> None:
        boundary = analyze_score_boundary(
            [
                DenseScoreObservation("正例", "a.md", "a.md", 0.5),
                DenseScoreObservation("负例", None, "b.md", 0.7),
            ]
        )

        self.assertIsNone(boundary.candidate_threshold)


if __name__ == "__main__":
    unittest.main()
