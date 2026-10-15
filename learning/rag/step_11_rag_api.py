# 课程：step_11_rag_api.md；访问范围：本地运行（无外部模型请求）。
import json
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.api.rag import rag_service
from app.services.rag_service import RAGResult, RAGSource
from main import app


client = TestClient(app)
fake_result = RAGResult(
    answer="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
    sources=[
        RAGSource(
            source="shipping.md",
            chunk_id="shipping.md#chunk-0",
            snippet="物流轨迹超过 48 小时没有更新时，可以联系人工客服核查。",
        )
    ],
)

with patch.object(
    rag_service,
    "chat",
    new=AsyncMock(return_value=fake_result),
):
    response = client.post(
        "/api/rag/chat",
        json={"message": "物流轨迹超过 48 小时没有更新怎么办？"},
    )

print(f"HTTP 状态码：{response.status_code}")
print(json.dumps(response.json(), ensure_ascii=False, indent=2))
