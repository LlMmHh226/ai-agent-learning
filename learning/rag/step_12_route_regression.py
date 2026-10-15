# 课程：step_12_route_regression.md；访问范围：本地运行（无外部模型请求）。
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router
from main import app


expected_routes = [
    ("POST", "/api/chat"),
    ("POST", "/api/chat/stream"),
    ("POST", "/api/chat/conversation"),
    ("DELETE", "/api/chat/conversation/{conversation_id}"),
    ("POST", "/api/rag/chat"),
]

registered_routes = {
    (method, route.path)
    for router in (chat_router, rag_router)
    for route in router.routes
    for method in getattr(route, "methods", set())
}

for method, path in expected_routes:
    exists = (method, path) in registered_routes
    print(f"{method:6} {path:45} 已注册={exists}")
