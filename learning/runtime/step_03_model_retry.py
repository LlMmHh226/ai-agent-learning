"""03：用固定 HTTP 响应观察一次模型请求的有限重试；不会连接模型服务。"""

import asyncio
from collections.abc import Awaitable, Callable
import math
from typing import TypeVar

import httpx
from openai import APIStatusError


Result = TypeVar("Result")
PERMANENT_CODES = {"insufficient_quota", "billing_hard_limit_reached", "billing_not_active"}


def retry_delay(error: APIStatusError) -> float | None:
    if isinstance(error.code, str) and error.code in PERMANENT_CODES:
        return None
    if error.response.headers.get("x-should-retry", "").lower() == "false":
        return None
    if error.status_code not in {429, 500, 502, 503, 504}:
        return None
    try:
        delay = float(error.response.headers.get("retry-after", "0.5"))
    except ValueError:
        return None
    return max(0.5, delay) if math.isfinite(delay) and 0 <= delay <= 3 else None


async def request_with_retry(operation: Callable[[], Awaitable[Result]],
                             sleep: Callable[[float], Awaitable[None]] = asyncio.sleep) -> Result:
    try:
        return await operation()
    except APIStatusError as error:
        delay = retry_delay(error)
        if delay is None:
            raise
        await sleep(delay)
    return await operation()


def simulated_error(status: int, code: str | None = None, retry_after: str = "2") -> APIStatusError:
    request = httpx.Request("POST", "https://example.invalid/v1/chat/completions")
    response = httpx.Response(status, headers={"Retry-After": retry_after}, request=request)
    return APIStatusError("本地固定响应", response=response, body={"code": code})


async def run_case(errors: list[APIStatusError]) -> tuple[int, list[float], int | str]:
    outcomes = iter(errors)
    calls = 0
    delays: list[float] = []

    async def operation() -> str:
        nonlocal calls
        calls += 1
        error = next(outcomes, None)
        if error is not None:
            raise error
        return "本地固定回复"

    async def record_delay(seconds: float) -> None:
        delays.append(seconds)

    try:
        result = await request_with_retry(operation, record_delay)
    except APIStatusError as error:
        result = error.status_code
    return calls, delays, result


async def main() -> None:
    cases = [
        ("服务暂时不可用", [simulated_error(503)], (2, [2.0], "本地固定回复")),
        ("额度不足", [simulated_error(429, "insufficient_quota")], (1, [], 429)),
        ("凭证失败", [simulated_error(401)], (1, [], 401)),
        ("等待过长", [simulated_error(429, retry_after="80")], (1, [], 429)),
        ("第二次仍失败", [simulated_error(503), simulated_error(503)], (2, [2.0], 503)),
    ]
    for label, errors, expected in cases:
        result = await run_case(errors)
        assert result == expected
        print(label, "(调用次数, 建议等待, 结果) =", result)


if __name__ == "__main__":
    asyncio.run(main())
