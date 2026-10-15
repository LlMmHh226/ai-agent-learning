import unittest

from app.rag.document_loader import load_markdown_documents


class DocumentLoaderTests(unittest.TestCase):
    def test_loads_markdown_content_and_source(self) -> None:
        documents = load_markdown_documents()
        documents_by_source = {
            document.metadata["source"]: document
            for document in documents
        }

        self.assertEqual(
            set(documents_by_source),
            {"products.md", "shipping.md", "after_sales.md"},
        )
        self.assertIn(
            "支持五脚轴热插拔",
            documents_by_source["products.md"].content,
        )


if __name__ == "__main__":
    unittest.main()
