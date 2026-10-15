# 阶段二、三：基础 RAG、向量检索与评测

[返回总目录](../README.md)

材料包含正式模块、本地教学实验与真实服务实验；是否联网以每课说明为准。

- [理解 RAG](step_01_rag_concept.md) — 本地运行（无外部模型请求）
- [建立知识库](step_02_knowledge_markdown.md) — 本地运行（无外部模型请求）
- [文档加载](step_03_document_loader.md) — 本地运行（无外部模型请求）
- [文本切分](step_04_chunker.md) — 本地运行（无外部模型请求）
- [字符 n-gram 检索](step_05_ngram_retriever.md) — 本地运行（无外部模型请求）
- [分数与 Top-K](step_06_scores_and_top_k.md) — 本地运行（无外部模型请求）
- [构建 RAG Prompt](step_07_prompt_context.md) — 本地运行（无外部模型请求）
- [Prompt 的区域职责](step_07b_01_prompt_roles.md) — 本地运行（无外部模型请求）
- [Grounding](step_07b_02_grounding_rule.md) — 本地运行（无外部模型请求）
- [资料不足](step_07b_03_missing_context.md) — 本地运行（无外部模型请求）
- [不可信上下文](step_07b_04_untrusted_context.md) — 本地运行（无外部模型请求）
- [答案与来源](step_07b_05_answer_and_sources.md) — 本地运行（无外部模型请求）
- [RAGService](step_08_rag_service.md) — 真实外部请求（可能收费）
- [程序级拒答](step_09_reliable_refusal.md) — 当前固定无资料示例不请求模型；更改问题或知识库后可能进入真实生成分支
- [结构化来源](step_10_sources.md) — 本地运行（无外部模型请求）
- [RAG HTTP 接口](step_11_rag_api.md) — 本地运行（无外部模型请求）
- [回归检查](step_12_route_regression.md) — 本地运行（无外部模型请求）
- [知识库工具](step_13_knowledge_tool.md) — 本地运行（无外部模型请求）
- [知识库 Tool Loop](step_14_agent_knowledge_loop.md) — 本地运行（无外部模型请求）
- [真实工具选择](step_14b_real_tool_selection.md) — 真实外部请求（可能收费）
- [关键词边界](step_15a_keyword_limit.md) — 本地运行（无外部模型请求）
- [Embedding 概念](step_15b_embedding_concept.md) — 本地运行（无外部模型请求）
- [余弦相似度](step_15c_cosine_similarity.md) — 本地运行（无外部模型请求）
- [Recall@K](step_15d_recall_at_k.md) — 本地运行（无外部模型请求）
- [Precision@K](step_15d_precision_at_k.md) — 本地运行（无外部模型请求）
- [重排](step_15e_rerank.md) — 本地运行（无外部模型请求）
- [幻觉排查](step_15f_hallucination.md) — 本地运行（无外部模型请求）
- [检查 Embedding 支持](step_16_check_embedding_support.md) — 真实外部请求（可能收费）
- [百炼 Embedding](step_16b_dashscope_embedding_smoke_test.md) — 真实外部请求（可能收费）
- [Query 与 Document](step_16c_query_document_retrieval.md) — 真实外部请求（可能收费）
- [EmbeddingService](step_16d_embedding_service.md) — 本地运行（无外部模型请求）
- [文档向量缓存](step_16e_document_embedding_cache.md) — 本地运行（无外部模型请求）
- [Dense Retriever](step_16f_dense_retriever.md) — 本地运行（无外部模型请求）
- [RRF 混合召回](step_16g_hybrid_retriever.md) — 本地运行（无外部模型请求）
- [评测集与基线](step_16h_01_eval_dataset_and_ngram_baseline.md) — 本地运行（无外部模型请求）
- [检索器对比](step_16h_02_compare_retrievers.md) — 真实外部请求（可能收费）
- [向量库决策](step_16i_01_vector_database_decision.md) — 本地运行（无外部模型请求）
- [正式接入决策](step_16i_02_integration_decision.md) — 本地运行（无外部模型请求）
- [无答案负例](step_17a_no_answer_eval.md) — 本地运行（无外部模型请求）
- [Dense 分数边界](step_17b_dense_score_eval.md) — 真实外部请求（可能收费）
- [阈值取舍](step_17c_01_threshold_tradeoff.md) — 本地运行（无外部模型请求）
- [留出验证](step_17c_02_holdout_eval.md) — 本地运行（无外部模型请求）
- [Dense 留出题](step_17d_dense_holdout.md) — 真实外部请求（可能收费）
- [证据审计](step_17e_evidence_audit.md) — 本地运行（无外部模型请求）
- [RAG 阶段边界](step_17f_rag_stage_boundary.md) — 本地运行（无外部模型请求）
- [RAG 代码复盘](step_17g_rag_code_recap.md) — 本地运行（无外部模型请求）
