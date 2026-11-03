# 课程：step_01_hello.md；访问范围：本地演示，不请求外部模型。
import asyncio
import os
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Path, Request
from pydantic import BaseModel
from app.tools.order_tools import get_order_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("① 应用启动：准备共享数据")
    app.state.greeting = "应用已准备好"
    app.state.visits = 0
    try:
        yield
    finally:
        print("③ 应用关闭：清理共享数据")
        app.state.greeting = None


app = FastAPI(lifespan=lifespan)


@app.get("/hello")
def hello():
    return {"message": "你好，这是我的第一个接口。"}


@app.get("/greet")
def greet(name: str):
    return {"message": f"你好，{name}！"}


@app.get("/orders/{order_id}")
def query_order(order_id: str):
    return get_order_status(order_id)


class GreetingRequest(BaseModel):
    name: str


class GreetingResponse(BaseModel):
    message: str


@app.post("/greetings", response_model=GreetingResponse)
def create_greeting(body: GreetingRequest):
    print("body的类型：", type(body).__name__)
    print("body.name的值：", body.name)
    return {
        "message": f"你好，{body.name}！",
        "internal_note": "只用于说明响应字段过滤的演示文字",
    }


@app.get("/wait/blocking")
async def wait_blocking():
    time.sleep(2)
    return {"message": "阻塞等待结束"}


@app.get("/wait/async")
async def wait_async():
    await asyncio.sleep(2)
    return {"message": "异步等待结束"}


class OrderService:
    def query(self, order_id: str):
        return get_order_status(order_id)


def get_order_service():
    print("① FastAPI执行依赖函数，创建OrderService对象")
    return OrderService()


@app.get("/di/orders/{order_id}")
def query_order_with_service(
    order_id: str,
    service: OrderService = Depends(get_order_service),
):
    print("② 路由收到service：", type(service).__name__)
    return service.query(order_id)


@app.get("/lifecycle")
def show_lifecycle(request: Request):
    print("② 正在处理一条/lifecycle请求")
    return {"message": request.app.state.greeting}


@app.get("/counter")
async def count_visits(request: Request):
    # 教学计数：本函数没有await，单个事件循环内完成读取与加一。
    # 这不是跨进程共享计数器，也不是生产并发计数方案。
    request.app.state.visits += 1
    return {"pid": os.getpid(), "count": request.app.state.visits}


@app.get("/checked-orders/{order_id}")
def query_checked_order(order_id: str = Path(pattern=r"^\d{5}$")):
    print("已通过格式校验，开始查询：", order_id)
    result = get_order_status(order_id)
    if 'error' in result:
        raise HTTPException(status_code=503, detail='订单服务暂时不可用')
    if not result["found"]:
        raise HTTPException(status_code=404, detail="没有找到该订单")
    print("找到订单，准备正常返回")
    return result
