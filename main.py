from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.rag import router as rag_router

# 初始化FastAPI应用
app = FastAPI(
    title="Agent Customer Service",
    description="AI智能客服后端",
    version="0.1.0",
)

app.include_router(chat_router)
app.include_router(rag_router)




