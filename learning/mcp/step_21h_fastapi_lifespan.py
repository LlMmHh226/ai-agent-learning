# 课程：step_21h_fastapi_lifespan.md；访问范围：本地演示，不请求外部模型。
"""21H：独立FastAPI学习应用管理MCP连接，不修改正式main.app。"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from mcp import Client, MCPError, StdioServerParameters
from pydantic import BaseModel, Field


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI传入当前app；yield前建立连接，yield期间处理请求，退出时关闭。

    app.state存的是当前进程可复用的连接对象，不是用户对话记忆或磁盘存储。
    """
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "-m", "learning.mcp.step_21b_order_server"],
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    async with Client(parameters, read_timeout_seconds=15) as client:
        listing = await client.list_tools()
        if "query_order" not in {item.name for item in listing.tools}:
            raise RuntimeError("MCP服务端没有提供query_order，停止应用启动。")
        app.state.mcp_client = client
        print("应用启动：MCP连接已建立，工具已确认。")
        try:
            yield
        finally:
            app.state.mcp_client = None
    print("应用关闭：MCP连接已清理，SDK已结束本例stdio子进程。")


app = FastAPI(title="MCP连接生命周期学习", lifespan=lifespan)


class OrderRequest(BaseModel):
    """HTTP请求体，字段由调用方JSON提供；本地样例订单号为5位数字字符串。"""

    order_id: str = Field(pattern=r"^\d{5}$", strict=True)


@app.post("/demo/orders/query")
async def query_order_http(body: OrderRequest, request: Request) -> dict[str, object]:
    """FastAPI传入校验后的body和HTTP请求对象；返回业务dict供JSON序列化。

    从request.app取当前应用的共享连接，路由不新建MCP Client。
    """
    client = getattr(request.app.state, "mcp_client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="MCP连接尚未准备好")
    try:
        result = await client.call_tool("query_order", {"order_id": body.order_id})
    except MCPError:
        raise HTTPException(status_code=502, detail="MCP协议调用失败") from None
    if result.is_error:
        raise HTTPException(status_code=502, detail="订单工具执行失败")
    data = result.structured_content
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="订单工具返回格式不符合预期")
    return data


def main() -> None:
    """无参数，进程内HTTP验证启动/复用/关闭；MCP为真实stdio通信。"""
    with TestClient(app) as http_client:
        shared_client = app.state.mcp_client
        first = http_client.post("/demo/orders/query", json={"order_id": "10001"})
        assert first.status_code == 200
        assert first.json()["tracking_number"] == "SF1234567890"
        print("HTTP请求1：", first.status_code, first.json())
        second = http_client.post("/demo/orders/query", json={"order_id": "10002"})
        assert second.status_code == 200 and second.json()["status"] == "待发货"
        assert app.state.mcp_client is shared_client
        print("HTTP请求2：", second.status_code, second.json())
        missing = http_client.post("/demo/orders/query", json={"order_id": "99999"})
        assert missing.status_code == 200 and missing.json()["found"] is False
        invalid = http_client.post("/demo/orders/query", json={"order_id": 10001})
        assert invalid.status_code == 422
        print("检查通过：同一连接处理多次请求；不存在订单为正常业务结果，错误类型被HTTP校验拒绝。")
    assert app.state.mcp_client is None


if __name__ == "__main__":
    main()
