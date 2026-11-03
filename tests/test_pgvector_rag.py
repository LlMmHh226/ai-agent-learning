import threading
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.rag.document_loader import Document
from app.rag.knowledge_retriever import KnowledgeRetrievalError
from app.rag.prompt_builder import RAG_INSUFFICIENT_CONTEXT_RESPONSE
from app.rag.retriever import RetrievalResult
from app.services.llm_service import llm_service
from app.services.rag_service import RAGService
from app.tools.knowledge_tools import search_knowledge_base
from main import app


RESULT = RetrievalResult(
    document=Document(
        content="支持五脚轴热插拔，更换轴体时不需要焊接。",
        metadata={"source": "products.md", "chunk_id": "products.md#section-0"},
    ),
    score=0.8,
)


class PgvectorRAGTests(unittest.IsolatedAsyncioTestCase):
    @patch.object(llm_service, "complete_messages", new_callable=AsyncMock)
    @patch("app.services.rag_service.retrieve_knowledge")
    async def test_database_context_reaches_prompt_and_sources_in_worker(self, retrieve, model):
        loop_thread = threading.get_ident()
        threads = []

        def search(**kwargs):
            threads.append(threading.get_ident())
            return [RESULT]

        retrieve.side_effect = search
        model.return_value = "不需要焊接，支持五脚轴热插拔。"
        service = RAGService(backend="pgvector")
        result = await service.chat("换轴需要焊接吗？")
        self.assertEqual(result.sources[0].chunk_id, "products.md#section-0")
        self.assertEqual(result.sources[0].snippet, RESULT.document.content)
        self.assertIn(RESULT.document.content, model.await_args.kwargs["messages"][1]["content"])
        self.assertNotEqual(threads, [loop_thread])
        self.assertIsNone(service._chunks)
        self.assertEqual(retrieve.call_args.kwargs["backend"], "pgvector")

    @patch.object(llm_service, "complete_messages", new_callable=AsyncMock)
    @patch("app.services.rag_service.retrieve_knowledge", return_value=[])
    async def test_no_evidence_refuses_without_chat_model(self, retrieve, model):
        result = await RAGService(backend="pgvector").chat("没有资料的问题")
        self.assertEqual(result.answer, RAG_INSUFFICIENT_CONTEXT_RESPONSE)
        self.assertEqual(result.sources, [])
        model.assert_not_awaited()


class PgvectorHTTPAndToolTests(unittest.TestCase):
    @patch.object(llm_service, "complete_messages", new_callable=AsyncMock)
    @patch("app.services.rag_service.retrieve_knowledge", return_value=[RESULT])
    def test_formal_http_returns_answer_and_database_section_source(self, retrieve, model):
        model.return_value = "不需要焊接。"
        with TestClient(app) as client:
            response = client.post("/api/rag/chat", json={"message": "换轴需要焊接吗？"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["answer"], "不需要焊接。")
        self.assertEqual(response.json()["sources"][0]["chunk_id"], "products.md#section-0")

    @patch("app.services.rag_service.retrieve_knowledge", side_effect=KnowledgeRetrievalError("unavailable"))
    def test_service_failure_is_http_error_not_a_grounding_refusal(self, retrieve):
        with TestClient(app) as client:
            response = client.post("/api/rag/chat", json={"message": "换轴需要焊接吗？"})
        self.assertEqual(response.status_code, 502)

    @patch("app.tools.knowledge_tools.retrieve_knowledge", return_value=[RESULT])
    def test_agent_tool_uses_shared_retrieval_and_preserves_result_shape(self, retrieve):
        result = search_knowledge_base("换轴需要焊接吗？")
        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["chunk_id"], "products.md#section-0")
        self.assertEqual(result["results"][0]["snippet"], RESULT.document.content)
        retrieve.assert_called_once_with(query="换轴需要焊接吗？")

    @patch("app.tools.knowledge_tools.retrieve_knowledge", side_effect=KnowledgeRetrievalError("unavailable"))
    def test_tool_reports_failure_instead_of_no_evidence(self, retrieve):
        result = search_knowledge_base("换轴需要焊接吗？")
        self.assertIn("error", result)
        self.assertNotIn("found", result)


if __name__ == "__main__":
    unittest.main()
