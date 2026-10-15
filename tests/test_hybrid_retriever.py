import unittest
from unittest.mock import Mock

from app.rag.dense_retriever import DenseRetrievalResult, DenseRetriever
from app.rag.document_loader import Document
from app.rag.hybrid_retriever import HybridRetriever


class HybridRetrieverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.after_sales_document = Document(
            content="退货验收通过后，退款会原路退回。",
            metadata={"source": "after_sales.md"},
        )
        self.product_document = Document(
            content="星云机械键盘支持五脚轴热插拔。",
            metadata={"source": "products.md"},
        )
        self.shipping_document = Document(
            content="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
            metadata={"source": "shipping.md"},
        )
        self.documents = [
            self.after_sales_document,
            self.product_document,
            self.shipping_document,
        ]
        self.dense_retriever = Mock(spec=DenseRetriever)
        self.hybrid_retriever = HybridRetriever(
            dense_retriever=self.dense_retriever,
        )

    def test_dense_recalls_semantic_match_missed_by_ngram(self) -> None:
        self.dense_retriever.retrieve.return_value = [
            DenseRetrievalResult(
                document=self.shipping_document,
                score=0.32,
            ),
            DenseRetrievalResult(
                document=self.after_sales_document,
                score=0.09,
            ),
        ]

        results = self.hybrid_retriever.retrieve(
            query="快递两天没动静怎么办？",
            documents=self.documents,
            top_k=1,
        )

        self.assertEqual(
            results[0].document.metadata["source"],
            "shipping.md",
        )

    def test_document_found_by_both_routes_receives_both_rrf_scores(self) -> None:
        self.dense_retriever.retrieve.return_value = [
            DenseRetrievalResult(
                document=self.shipping_document,
                score=0.9,
            ),
            DenseRetrievalResult(
                document=self.product_document,
                score=0.8,
            ),
        ]

        results = self.hybrid_retriever.retrieve(
            query="星云机械键盘支持热插拔吗？",
            documents=self.documents,
            top_k=2,
        )

        self.assertEqual(
            results[0].document.metadata["source"],
            "products.md",
        )
        expected_product_score = (1 / 61) + (1 / 62)
        self.assertAlmostEqual(results[0].score, expected_product_score)

    def test_rejects_non_positive_rrf_k(self) -> None:
        with self.assertRaises(ValueError):
            HybridRetriever(
                dense_retriever=self.dense_retriever,
                rrf_k=0,
            )


if __name__ == "__main__":
    unittest.main()
