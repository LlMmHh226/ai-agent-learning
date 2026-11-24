"""01：用同一请求 ID 串起样例订单请求的日志阶段；无外部模型。"""

from contextvars import ContextVar
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.repositories.demo_orders import get_demo_order_status


logger = logging.getLogger(__name__)
request_id = ContextVar("request_id", default="-")
app = FastAPI(title="请求追踪教学应用")


class OrderQuery(BaseModel):
    order_id: str = Field(pattern=r"^[0-9]{5}$", strict=True)


def log_stage(stage: str) -> None:
    logger.info("request_id=%s stage=%s", request_id.get(), stage)


@app.middleware("http")
async def trace_request(request: Request, call_next):
    token = request_id.set(uuid4().hex)
    started = perf_counter()
    log_stage("request.start")
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id.get()
        logger.info("request_id=%s stage=request.end status=%s elapsed_ms=%.1f",
                    request_id.get(), response.status_code, 1000 * (perf_counter() - started))
        return response
    finally:
        request_id.reset(token)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/demo/orders/query")
async def query_order(body: OrderQuery) -> dict[str, object]:
    log_stage("order.lookup")
    data = get_demo_order_status(body.order_id)
    log_stage("order.result")
    return data


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    with TestClient(app) as client:
        health_check = client.get("/health")
        assert health_check.status_code == 200 and health_check.json() == {"status": "ok"}
        responses = [client.post("/demo/orders/query", json={"order_id": order_id})
                     for order_id in ("10001", "99999")]
    assert [response.status_code for response in responses] == [200, 200]
    assert [response.json()["found"] for response in responses] == [True, False]
    ids = [response.headers["X-Request-ID"] for response in responses]
    assert len(set(ids)) == 2
    print("健康检查：", health_check.json())
    for response in responses:
        print(response.status_code, response.headers["X-Request-ID"], response.json())


if __name__ == "__main__":
    main()
