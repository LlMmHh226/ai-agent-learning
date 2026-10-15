from dataclasses import dataclass

from app.rag.document_loader import Document
from app.services.embedding_service import EmbeddingService


@dataclass
class EmbeddedDocument:
    document: Document
    vector: list[float]


class KnowledgeEmbeddingCache:
    """在当前 Python 进程中复用内容未变化的知识文档向量。"""

    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self._vectors_by_content: dict[str, list[float]] = {}

    def get_embeddings(
        self,
        documents: list[Document],
    ) -> list[EmbeddedDocument]:
        """只请求尚未缓存的文档，并按输入顺序返回文档与向量。"""
        missing_contents = list(
            dict.fromkeys(
                document.content
                for document in documents
                if document.content not in self._vectors_by_content
            )
        )

        if missing_contents:
            missing_vectors = self.embedding_service.embed_documents(
                texts=missing_contents,
            )
            if len(missing_vectors) != len(missing_contents):
                raise ValueError("文档数量与向量数量不一致")

            for content, vector in zip(missing_contents, missing_vectors):
                self._vectors_by_content[content] = list(vector)

        return [
            EmbeddedDocument(
                document=document,
                vector=list(self._vectors_by_content[document.content]),
            )
            for document in documents
        ]
