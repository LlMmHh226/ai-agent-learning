"""02：一次 HTTP 请求内两段异步工作共享一个时间预算；无外部模型。"""

import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


app = FastAPI(title="请求总预算教学应用")


async def simulate_two_stages(stall: bool, stages: list[str]) -> None:
    await asyncio.sleep(0)
    stages.append("order.checked")
    if stall:
        await asyncio.Event().wait()
    stages.append("answer.ready")


@app.get("/demo/budget")
async def use_budget(stall: bool = False) -> JSONResponse:
    stages: list[str] = []
    try:
        async with asyncio.timeout(0.25):
            await simulate_two_stages(stall, stages)
    except TimeoutError:
        return JSONResponse({"detail": "请求处理超时", "stages": stages}, status_code=504)
    return JSONResponse({"stages": stages})


def main() -> None:
    with TestClient(app) as client:
        normal = client.get("/demo/budget")
        stalled = client.get("/demo/budget", params={"stall": True})
    assert normal.status_code == 200 and normal.json()["stages"] == ["order.checked", "answer.ready"]
    assert stalled.status_code == 504 and stalled.json()["stages"] == ["order.checked"]
    for response in (normal, stalled):
        print("HTTP", response.status_code, response.json())


if __name__ == "__main__":
    main()
