import unittest

from app.rag.document_loader import Document
from app.rag.retriever import retrieve


class RetrieverTests(unittest.TestCase):
    def test_related_chunk_ranks_before_unrelated_chunk(self) -> None:
        product_chunk = Document(
            content="星云机械键盘支持五脚轴热插拔。",
            metadata={
                "source": "products.md",
                "chunk_id": "products.md#chunk-0",
            },
        )
        after_sales_chunk = Document(
            content="退款通常会在一至三个工作日内原路退回。",
            metadata={
                "source": "after_sales.md",
                "chunk_id": "after_sales.md#chunk-0",
            },
        )

        results = retrieve(
            query="星云机械键盘支持热插拔吗？",
            chunks=[after_sales_chunk, product_chunk],
            top_k=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].document.metadata["chunk_id"],
            "products.md#chunk-0",
        )
        self.assertGreater(results[0].score, 0)


if __name__ == "__main__":
    unittest.main()
