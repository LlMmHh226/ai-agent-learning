"""本地观察两个并发请求的耗时；没有MCP、模型或网络端口。"""

import asyncio
import time

import httpx

from learning.web_basics.step_01_hello import app


async def compare_requests() -> None:
    """同一事件循环内并发请求各接口两次，打印观测耗时，不作严格性能断言。"""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://local-test"
    ) as client:
        for path in ("/wait/blocking", "/wait/async"):
            start = time.perf_counter()
            responses = await asyncio.gather(client.get(path), client.get(path))
            elapsed = time.perf_counter() - start
            assert all(response.status_code == 200 for response in responses)
            print(f"{path}：同时发两个请求，总耗时 {elapsed:.2f} 秒")


if __name__ == "__main__":
    asyncio.run(compare_requests())
