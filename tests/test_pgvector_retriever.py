import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import psycopg
from pydantic import SecretStr

from app.rag.knowledge_retriever import KnowledgeRetrievalError, retrieve_knowledge
from app.rag.pgvector_retriever import PgvectorRetriever
from app.repositories.knowledge_repository import (
    KnowledgeRepositoryError,
    search_knowledge_chunks,
)


QUERY_VECTOR = [0.1] * 1536
ROW = {
    "chunk_id": "products.md#section-0",
    "source": "products.md",
    "content": "支持五脚轴热插拔，更换轴体时不需要焊接。",
    "distance": 0.2,
}


class KnowledgeRepositoryTests(unittest.TestCase):
    def setUp(self):
        settings_patch = patch("app.repositories.knowledge_repository.get_settings")
        self.settings = settings_patch.start()
        self.addCleanup(settings_patch.stop)
        self.settings.return_value = SimpleNamespace(
            postgres_host="localhost", postgres_port=15432,
            postgres_db="agent_learning", postgres_user="root",
            postgres_password=SecretStr("unit-test-only"),
        )
        connect_patch = patch("app.repositories.knowledge_repository.psycopg.connect")
        self.connect = connect_patch.start()
        self.addCleanup(connect_patch.stop)
        self.connection = self.connect.return_value.__enter__.return_value
        self.cursor = self.connection.cursor.return_value.__enter__.return_value

    def test_query_is_read_only_parameterized_and_limits_results(self):
        self.cursor.fetchall.return_value = [ROW]
        self.assertEqual(search_knowledge_chunks(QUERY_VECTOR, 3), [ROW])
        self.assertTrue(self.connection.read_only)
        sql, params = self.cursor.execute.call_args.args
        self.assertIn("embedding <=> %s::vector(1536)", sql)
        self.assertIn("ORDER BY distance ASC", sql)
        self.assertIn("LIMIT %s", sql)
        self.assertEqual(json.loads(params[0]), QUERY_VECTOR)
        self.assertEqual(params[1], 3)

    def test_empty_query_result_is_not_a_service_failure(self):
        self.cursor.fetchall.return_value = []
        self.assertEqual(search_knowledge_chunks(QUERY_VECTOR, 3), [])

    def test_invalid_vectors_never_connect_to_database(self):
        for vector in ([0.1] * 10, [0.0] * 1536, [True] * 1536, [float("nan")] * 1536):
            with self.subTest(first_value=repr(vector[0])):
                with self.assertRaises(ValueError):
                    search_knowledge_chunks(vector, 3)
        self.connect.assert_not_called()

    def test_missing_password_does_not_connect(self):
        self.settings.return_value.postgres_password = None
        with self.assertRaises(KnowledgeRepositoryError):
            search_knowledge_chunks(QUERY_VECTOR, 3)
        self.connect.assert_not_called()

    def test_database_failure_is_not_returned_as_an_empty_list(self):
        self.connect.side_effect = psycopg.OperationalError("database unavailable")
        with self.assertRaises(KnowledgeRepositoryError) as raised:
            search_knowledge_chunks(QUERY_VECTOR, 3)
        self.assertNotIn("unit-test-only", str(raised.exception))


class PgvectorRetrieverTests(unittest.TestCase):
    def setUp(self):
        self.embedding = SimpleNamespace(
            model="text-embedding-v4", dimensions=1536,
            embed_query=Mock(return_value=QUERY_VECTOR),
        )
        self.retriever = PgvectorRetriever(self.embedding)

    @patch("app.rag.pgvector_retriever.search_knowledge_chunks")
    def test_converts_distance_and_preserves_database_sources(self, search):
        search.return_value = [ROW, {**ROW, "distance": 0.8}]
        results = self.retriever.retrieve(" 换轴需要焊接吗？ ", 3, 0.5)
        self.embedding.embed_query.assert_called_once_with("换轴需要焊接吗？")
        search.assert_called_once_with(QUERY_VECTOR, 3)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0].score, 0.8)
        self.assertEqual(results[0].document.content, ROW["content"])
        self.assertEqual(results[0].document.metadata["chunk_id"], ROW["chunk_id"])

    @patch("app.rag.pgvector_retriever.search_knowledge_chunks")
    def test_empty_question_does_not_request_embedding(self, search):
        self.assertEqual(self.retriever.retrieve("   "), [])
        self.embedding.embed_query.assert_not_called()
        search.assert_not_called()

    def test_model_mismatch_stops_before_embedding(self):
        self.embedding.model = "text-embedding-v2"
        with self.assertRaises(ValueError):
            self.retriever.retrieve("换轴需要焊接吗？")
        self.embedding.embed_query.assert_not_called()

    @patch("app.rag.pgvector_retriever.search_knowledge_chunks")
    def test_non_finite_distance_cannot_reach_prompt(self, search):
        search.return_value = [{**ROW, "distance": float("nan")}]
        with self.assertRaises(ValueError):
            self.retriever.retrieve("换轴需要焊接吗？")

    @patch("app.rag.knowledge_retriever.retrieve")
    @patch("app.rag.knowledge_retriever.PgvectorRetriever")
    @patch("app.rag.knowledge_retriever.get_settings")
    def test_shared_entry_does_not_silently_fall_back_on_database_failure(
        self, settings, retriever, ngram,
    ):
        settings.return_value = SimpleNamespace(
            knowledge_retrieval_backend="pgvector", pgvector_top_k=3, pgvector_min_score=0.5,
        )
        retriever.return_value.retrieve.side_effect = KnowledgeRepositoryError("unavailable")
        with self.assertRaises(KnowledgeRetrievalError):
            retrieve_knowledge("换轴需要焊接吗？")
        ngram.assert_not_called()


if __name__ == "__main__":
    unittest.main()
