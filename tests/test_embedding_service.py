import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.core.config import Settings
from app.services.embedding_service import (
    EmbeddingService,
    EmbeddingServiceError,
)


class EmbeddingServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(
            llm_api_key="test-llm-key",
            llm_base_url="https://example.com/v1",
            llm_model="test-model",
            embedding_provider="dashscope",
            embedding_model="text-embedding-v2",
            embedding_dimensions=3,
            dashscope_api_key="test-embedding-key",
        )
        self.service = EmbeddingService(settings=settings)

    @patch("app.services.embedding_service.TextEmbedding.call")
    def test_uses_document_and_query_roles(self, call_mock) -> None:
        call_mock.side_effect = [
            SimpleNamespace(
                status_code=200,
                output={
                    "embeddings": [
                        {"text_index": 0, "embedding": [1.0, 0.0, 0.0]},
                        {"text_index": 1, "embedding": [0.0, 1.0, 0.0]},
                    ]
                },
            ),
            SimpleNamespace(
                status_code=200,
                output={
                    "embeddings": [
                        {"text_index": 0, "embedding": [0.8, 0.2, 0.0]},
                    ]
                },
            ),
        ]

        document_vectors = self.service.embed_documents(["文档一", "文档二"])
        query_vector = self.service.embed_query("用户问题")

        self.assertEqual(len(document_vectors), 2)
        self.assertEqual(query_vector, [0.8, 0.2, 0.0])
        self.assertEqual(
            call_mock.call_args_list[0].kwargs["text_type"],
            "document",
        )
        self.assertEqual(
            call_mock.call_args_list[1].kwargs["text_type"],
            "query",
        )
        self.assertEqual(
            call_mock.call_args_list[0].kwargs["request_timeout"],
            20,
        )

    @patch("app.services.embedding_service.TextEmbedding.call")
    def test_does_not_retry_failed_request(self, call_mock) -> None:
        call_mock.return_value = SimpleNamespace(
            status_code=429,
            code="Throttling",
            message="Too many requests",
        )

        with self.assertRaises(EmbeddingServiceError):
            self.service.embed_query("用户问题")

        call_mock.assert_called_once()

    @patch("app.services.embedding_service.TextEmbedding.call")
    def test_batches_multiple_queries_in_one_request(self, call_mock) -> None:
        call_mock.return_value = SimpleNamespace(
            status_code=200,
            output={
                "embeddings": [
                    {"text_index": 0, "embedding": [1.0, 0.0, 0.0]},
                    {"text_index": 1, "embedding": [0.0, 1.0, 0.0]},
                ]
            },
        )

        vectors = self.service.embed_queries(["问题一", "问题二"])

        self.assertEqual(len(vectors), 2)
        call_mock.assert_called_once()
        self.assertEqual(call_mock.call_args.kwargs["text_type"], "query")
        self.assertEqual(
            call_mock.call_args.kwargs["input"],
            ["问题一", "问题二"],
        )


if __name__ == "__main__":
    unittest.main()
