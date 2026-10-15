import unittest

from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents


class ChunkerTests(unittest.TestCase):
    def test_splits_text_with_overlap(self) -> None:
        document = Document(
            content="ABCDEFGHIJ",
            metadata={"source": "example.md"},
        )

        chunks = split_documents(
            [document],
            chunk_size=6,
            overlap=2,
        )

        self.assertEqual(
            [chunk.content for chunk in chunks],
            ["ABCDEF", "EFGHIJ"],
        )
        self.assertEqual(
            chunks[1].metadata,
            {
                "source": "example.md",
                "chunk_id": "example.md#chunk-1",
            },
        )

    def test_splits_loaded_knowledge_documents(self) -> None:
        documents = load_markdown_documents()

        chunks = split_documents(documents)

        self.assertGreater(len(chunks), len(documents))
        self.assertTrue(
            all("source" in chunk.metadata for chunk in chunks)
        )
        self.assertTrue(
            all("chunk_id" in chunk.metadata for chunk in chunks)
        )


if __name__ == "__main__":
    unittest.main()
