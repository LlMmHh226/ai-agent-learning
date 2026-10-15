import unittest
from unittest.mock import Mock

from app.rag.document_loader import Document
from app.rag.embedding_cache import KnowledgeEmbeddingCache
from app.services.embedding_service import EmbeddingService


class KnowledgeEmbeddingCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.embedding_service = Mock(spec=EmbeddingService)
        self.cache = KnowledgeEmbeddingCache(
            embedding_service=self.embedding_service,
        )
        self.shipping_document = Document(
            content="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
            metadata={"source": "shipping.md"},
        )
        self.product_document = Document(
            content="星云机械键盘支持五脚轴热插拔。",
            metadata={"source": "products.md"},
        )

    def test_reuses_cached_document_vectors(self) -> None:
        self.embedding_service.embed_documents.return_value = [
            [1.0, 0.0],
            [0.0, 1.0],
        ]
        documents = [self.shipping_document, self.product_document]

        first_result = self.cache.get_embeddings(documents)
        second_result = self.cache.get_embeddings(documents)

        self.embedding_service.embed_documents.assert_called_once_with(
            texts=[
                self.shipping_document.content,
                self.product_document.content,
            ]
        )
        self.assertEqual(first_result[0].vector, [1.0, 0.0])
        self.assertEqual(second_result[1].vector, [0.0, 1.0])

    def test_requests_only_new_document_content(self) -> None:
        self.embedding_service.embed_documents.side_effect = [
            [[1.0, 0.0]],
            [[0.0, 1.0]],
        ]

        self.cache.get_embeddings([self.shipping_document])
        result = self.cache.get_embeddings(
            [self.shipping_document, self.product_document]
        )

        self.assertEqual(
            self.embedding_service.embed_documents.call_args_list[1].kwargs,
            {"texts": [self.product_document.content]},
        )
        self.assertEqual(result[0].vector, [1.0, 0.0])
        self.assertEqual(result[1].vector, [0.0, 1.0])


if __name__ == "__main__":
    unittest.main()
