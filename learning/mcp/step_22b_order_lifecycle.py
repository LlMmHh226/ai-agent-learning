"""22B：独立 FastAPI 应用按模式管理和复用一个本机 MCP 会话。"""

from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from mcp import Client, MCPError, StdioServerParameters
from pydantic import BaseModel, Field

from app.repositories.demo_orders import get_demo_order_status


ORDER_TOOL = "get_order_status"


@asynccontextmanager
async def connect_order_server():
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "-m", "learning.mcp.managed_order_server"],
        cwd=str(Path(__file__).resolve().parents[2]),
    )
    async with Client(parameters, read_timeout_seconds=15) as client:
        yield client


class OrderRequest(BaseModel):
    order_id: str = Field(pattern=r"^[0-9]{5}$", strict=True)


def create_app(backend: Literal["native", "mcp"] = "native") -> FastAPI:
    if backend not in {"native", "mcp"}:
        raise ValueError("backend 只能是 native 或 mcp")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.order_client = None
        if backend == "native":
            yield
            return
        async with connect_order_server() as client:
            listing = await client.list_tools()
            if ORDER_TOOL not in {tool.name for tool in listing.tools}:
                raise RuntimeError("服务端缺少订单工具")
            app.state.order_client = client
            try:
                yield
            finally:
                app.state.order_client = None

    app = FastAPI(title="订单网关生命周期教学", lifespan=lifespan)

    @app.post("/demo/orders/query")
    async def query_order(body: OrderRequest, request: Request) -> dict[str, object]:
        if backend == "native":
            return get_demo_order_status(body.order_id)
        client = getattr(request.app.state, "order_client", None)
        if client is None:
            raise HTTPException(503, "MCP 会话尚未就绪")
        try:
            result = await client.call_tool(ORDER_TOOL, {"order_id": body.order_id})
        except MCPError:
            raise HTTPException(502, "MCP 协议调用失败") from None
        if result.is_error or not isinstance(result.structured_content, dict):
            raise HTTPException(502, "订单工具返回错误")
        return result.structured_content

    return app


def main() -> None:
    mcp_app = create_app("mcp")
    native_app = create_app("native")
    with TestClient(native_app) as client:
        assert native_app.state.order_client is None
        native = client.post("/demo/orders/query", json={"order_id": "10001"})
        assert native.status_code == 200
    with TestClient(mcp_app) as client:
        shared = mcp_app.state.order_client
        found = client.post("/demo/orders/query", json={"order_id": "10001"})
        missing = client.post("/demo/orders/query", json={"order_id": "99999"})
        assert shared is not None and mcp_app.state.order_client is shared
        assert found.status_code == 200 and found.json() == native.json()
        assert missing.status_code == 200 and missing.json()["found"] is False
        print("native / mcp 返回同一条样例事实：", found.json())
        print("共用会话；查无订单：", missing.json())
    assert mcp_app.state.order_client is None
    print("应用退出：会话引用已清理。")


if __name__ == "__main__":
    main()
