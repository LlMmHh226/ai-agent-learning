from typing import Literal

from dashscope import TextEmbedding

from app.core.config import Settings, get_settings


EmbeddingTextType = Literal["document", "query"]


class EmbeddingServiceError(RuntimeError):
    """Embedding 服务调用或返回数据不符合预期。"""


class EmbeddingService:
    """统一管理 Embedding 配置、百炼请求和返回值校验。"""

    def __init__(self, settings: Settings | None = None) -> None:
        if settings is None:
            settings = get_settings()

        provider = settings.embedding_provider.lower()
        if provider != "dashscope":
            raise ValueError(f"暂不支持 Embedding Provider：{provider}")
        if not settings.dashscope_api_key:
            raise ValueError("缺少 DASHSCOPE_API_KEY")
        if settings.embedding_dimensions <= 0:
            raise ValueError("EMBEDDING_DIMENSIONS 必须大于 0")

        self.provider = provider
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions
        self.api_key = settings.dashscope_api_key

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量生成知识文档向量。"""
        if not texts:
            raise ValueError("texts 不能为空")
        if any(not text.strip() for text in texts):
            raise ValueError("文档文本不能为空字符串")

        return self._request_embeddings(
            texts=texts,
            text_type="document",
        )

    def embed_query(self, text: str) -> list[float]:
        """生成一个用户查询向量。"""
        return self.embed_queries([text])[0]

    def embed_queries(self, texts: list[str]) -> list[list[float]]:
        """批量生成用户查询向量。"""
        if not texts:
            raise ValueError("texts 不能为空")
        if any(not text.strip() for text in texts):
            raise ValueError("查询文本不能为空字符串")

        return self._request_embeddings(
            texts=texts,
            text_type="query",
        )

    def _request_embeddings(
        self,
        texts: list[str],
        text_type: EmbeddingTextType,
    ) -> list[list[float]]:
        """向当前 Provider 发起一次请求；失败时不自动重试。"""
        try:
            response = TextEmbedding.call(
                model=self.model,
                input=texts,
                api_key=self.api_key,
                text_type=text_type,
                request_timeout=20,
            )
        except Exception as error:
            raise EmbeddingServiceError(
                f"Embedding {text_type} 请求异常：{type(error).__name__}"
            ) from error

        if response.status_code != 200:
            code = getattr(response, "code", "unknown")
            raise EmbeddingServiceError(
                f"Embedding {text_type} 请求失败："
                f"HTTP {response.status_code}，错误码 {code}"
            )

        try:
            embedding_items = sorted(
                response.output["embeddings"],
                key=lambda item: item.get("text_index", 0),
            )
            vectors = [item["embedding"] for item in embedding_items]
        except (KeyError, TypeError) as error:
            raise EmbeddingServiceError("Embedding 返回结构无效") from error

        if len(vectors) != len(texts):
            raise EmbeddingServiceError(
                f"Embedding 返回数量异常：输入 {len(texts)}，返回 {len(vectors)}"
            )
        if any(len(vector) != self.dimensions for vector in vectors):
            raise EmbeddingServiceError(
                f"Embedding 返回维度与配置值 {self.dimensions} 不一致"
            )

        return vectors
