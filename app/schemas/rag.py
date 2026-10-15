from pydantic import BaseModel


class RAGSourceResponse(BaseModel):
    source: str
    chunk_id: str
    snippet: str


class RAGChatResponse(BaseModel):
    answer: str
    sources: list[RAGSourceResponse]
