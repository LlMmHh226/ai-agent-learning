-- 在agent_learning数据库中启用pgvector并准备知识片段表。
-- 当前Embedding模型为text-embedding-v4，请求显式指定1536维。
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;

CREATE TABLE IF NOT EXISTS public.knowledge_chunks (
    chunk_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL
);
