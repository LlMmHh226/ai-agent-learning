import unittest
from unittest.mock import Mock

from app.rag.dense_retriever import (
    DenseRetriever,
    calculate_cosine_similarity,
)
from app.rag.document_loader import Document
from app.services.embedding_service import EmbeddingService


class DenseRetrieverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.embedding_service = Mock(spec=EmbeddingService)
        self.retriever = DenseRetriever(
            embedding_service=self.embedding_service,
        )
        self.documents = [
            Document(
                content="退货验收后会原路退款。",
                metadata={"source": "after_sales.md"},
            ),
            Document(
                content="星云机械键盘支持热插拔。",
                metadata={"source": "products.md"},
            ),
            Document(
                content="物流轨迹超过 48 小时未更新时可联系人工客服。",
                metadata={"source": "shipping.md"},
            ),
        ]

    def test_returns_top_k_documents_by_cosine_score(self) -> None:
        self.embedding_service.embed_documents.return_value = [
            [0.8, 0.6],
            [0.0, 1.0],
            [1.0, 0.0],
        ]
        self.embedding_service.embed_query.return_value = [1.0, 0.0]

        results = self.retriever.retrieve(
            query="快递两天没动静怎么办？",
            documents=self.documents,
            top_k=2,
        )

        self.assertEqual(
            [result.document.metadata["source"] for result in results],
            ["shipping.md", "after_sales.md"],
        )
        self.assertAlmostEqual(results[0].score, 1.0)
        self.assertAlmostEqual(results[1].score, 0.8)
        self.embedding_service.embed_query.assert_called_once_with(
            "快递两天没动静怎么办？"
        )

    def test_reuses_document_cache_between_queries(self) -> None:
        self.embedding_service.embed_documents.return_value = [
            [0.8, 0.6],
            [0.0, 1.0],
            [1.0, 0.0],
        ]
        self.embedding_service.embed_query.side_effect = [
            [1.0, 0.0],
            [0.0, 1.0],
        ]

        self.retriever.retrieve("物流问题", self.documents, top_k=1)
        self.retriever.retrieve("商品问题", self.documents, top_k=1)

        self.embedding_service.embed_documents.assert_called_once()
        self.assertEqual(self.embedding_service.embed_query.call_count, 2)

    def test_cosine_similarity_rejects_different_dimensions(self) -> None:
        with self.assertRaises(ValueError):
            calculate_cosine_similarity(
                vector_a=[1.0, 0.0],
                vector_b=[1.0, 0.0, 0.0],
            )


if __name__ == "__main__":
    unittest.main()
