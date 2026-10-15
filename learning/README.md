# 学习路线

按下面顺序阅读。编号沿用课程名称：基础阶段的 19/20 与框架阶段的 19A/20A 是不同内容。每课都标注网络访问范围，先看讲义再运行。

先完成 [安装与首次请求](../README.md)，再从第一阶段开始。只有进入第五阶段才安装框架环境。

## 五阶段成果

| 阶段 | 学完应能做什么 |
| --- | --- |
| 一：基础与原生 Agent | 解释HTTP请求、工具调用和会话保存 |
| 二：基础 RAG（01～14B） | 检索资料、构造Prompt、返回出处与拒答 |
| 三：向量与评测（15A～17G） | 比较n-gram/Dense/Hybrid，分析误放与误拒 |
| 四：上下文工程 | 追踪history/facts/模型输入，分析信息丢失 |
| 五：框架 | 将原生职责映射到LangChain和显式图工作流 |

[阶段复盘与练习](../docs/recap.md) · [完整调用链](../docs/architecture.md) · [面试速查](INTERVIEW_QUICK_REFERENCE.md)

## 阶段一：Python/FastAPI 与原生 Agent

- [01 最小模型对话](steps_01_20/step_01_basic_chat.md) — 真实外部请求（可能收费）
- [02 最小 FastAPI 接口](steps_01_20/step_02_fastapi_chat.md) — 真实外部请求（可能收费）；启动后提交有效问题才调用模型
- [03 输入校验](steps_01_20/step_03_input_validation.md) — 真实外部请求（可能收费）；启动后提交有效问题才调用模型
- [04 多轮会话](steps_01_20/step_04_conversation_memory.md) — 真实外部请求（可能收费）；启动后提交有效问题才调用模型
- [05 第一次工具调用](steps_01_20/step_05_tool_calling.md) — 真实外部请求（可能收费）；启动后提交有效问题才调用模型
- [06 流式输出](steps_01_20/step_06_streaming.md) — 真实外部请求（可能收费）；启动后提交有效问题才调用模型
- [07 正式项目分层](steps_01_20/step_07_project_map.md) — 本地运行（无外部模型请求）
- [08 错误处理](steps_01_20/step_08_error_handling.md) — 本地运行（无外部模型请求）
- [09 首个单元测试](steps_01_20/step_09_first_test.md) — 本地运行（无外部模型请求）
- [10 参数化测试](steps_01_20/step_10_parameterized_test.md) — 本地运行（无外部模型请求）
- [11 模拟模型测试](steps_01_20/step_11_mock_model_test.md) — 本地运行（无外部模型请求）
- [12 真实 API 集成检查](steps_01_20/step_12_real_api_test.md) — 真实外部请求（可能收费）
- [13 HTTP 接口测试](steps_01_20/step_13_fastapi_test.md) — 本地运行（无外部模型请求）
- [14 Agent 工具循环](steps_01_20/step_14_agent_loop.md) — 本地运行（无外部模型请求）
- [15 多个工具](steps_01_20/step_15_multiple_tools.md) — 本地运行（无外部模型请求）
- [16 工具选择评测](steps_01_20/step_16_tool_selection_eval.md) — 真实外部请求（可能收费）
- [17 工具参数评测](steps_01_20/step_17_tool_argument_eval.md) — 真实外部请求（可能收费）
- [18 工具参数安全](steps_01_20/step_18_tool_safety_test.md) — 本地运行（无外部模型请求）
- [19 滑动窗口](steps_01_20/step_19_memory_window.md) — 本地运行（无外部模型请求）
- [20 结构化事实](steps_01_20/step_20_structured_memory.md) — 本地运行（无外部模型请求）

## 阶段二、三：基础 RAG、向量检索与评测

- [01 理解 RAG](rag/step_01_rag_concept.md) — 本地运行（无外部模型请求）
- [02 建立知识库](rag/step_02_knowledge_markdown.md) — 本地运行（无外部模型请求）
- [03 文档加载](rag/step_03_document_loader.md) — 本地运行（无外部模型请求）
- [04 文本切分](rag/step_04_chunker.md) — 本地运行（无外部模型请求）
- [05 字符 n-gram 检索](rag/step_05_ngram_retriever.md) — 本地运行（无外部模型请求）
- [06 分数与 Top-K](rag/step_06_scores_and_top_k.md) — 本地运行（无外部模型请求）
- [07 构建 RAG Prompt](rag/step_07_prompt_context.md) — 本地运行（无外部模型请求）
- [07b_01 Prompt 的区域职责](rag/step_07b_01_prompt_roles.md) — 本地运行（无外部模型请求）
- [07b_02 Grounding](rag/step_07b_02_grounding_rule.md) — 本地运行（无外部模型请求）
- [07b_03 资料不足](rag/step_07b_03_missing_context.md) — 本地运行（无外部模型请求）
- [07b_04 不可信上下文](rag/step_07b_04_untrusted_context.md) — 本地运行（无外部模型请求）
- [07b_05 答案与来源](rag/step_07b_05_answer_and_sources.md) — 本地运行（无外部模型请求）
- [08 RAGService](rag/step_08_rag_service.md) — 真实外部请求（可能收费）
- [09 程序级拒答](rag/step_09_reliable_refusal.md) — 当前固定无资料示例不请求模型；更改问题或知识库后可能进入真实生成分支
- [10 结构化来源](rag/step_10_sources.md) — 本地运行（无外部模型请求）
- [11 RAG HTTP 接口](rag/step_11_rag_api.md) — 本地运行（无外部模型请求）
- [12 回归检查](rag/step_12_route_regression.md) — 本地运行（无外部模型请求）
- [13 知识库工具](rag/step_13_knowledge_tool.md) — 本地运行（无外部模型请求）
- [14 知识库 Tool Loop](rag/step_14_agent_knowledge_loop.md) — 本地运行（无外部模型请求）
- [14b 真实工具选择](rag/step_14b_real_tool_selection.md) — 真实外部请求（可能收费）
- [15a 关键词边界](rag/step_15a_keyword_limit.md) — 本地运行（无外部模型请求）
- [15b Embedding 概念](rag/step_15b_embedding_concept.md) — 本地运行（无外部模型请求）
- [15c 余弦相似度](rag/step_15c_cosine_similarity.md) — 本地运行（无外部模型请求）
- [15d_recall Recall@K](rag/step_15d_recall_at_k.md) — 本地运行（无外部模型请求）
- [15d_precision Precision@K](rag/step_15d_precision_at_k.md) — 本地运行（无外部模型请求）
- [15e 重排](rag/step_15e_rerank.md) — 本地运行（无外部模型请求）
- [15f 幻觉排查](rag/step_15f_hallucination.md) — 本地运行（无外部模型请求）
- [16 检查 Embedding 支持](rag/step_16_check_embedding_support.md) — 真实外部请求（可能收费）
- [16b 百炼 Embedding](rag/step_16b_dashscope_embedding_smoke_test.md) — 真实外部请求（可能收费）
- [16c Query 与 Document](rag/step_16c_query_document_retrieval.md) — 真实外部请求（可能收费）
- [16d EmbeddingService](rag/step_16d_embedding_service.md) — 本地运行（无外部模型请求）
- [16e 文档向量缓存](rag/step_16e_document_embedding_cache.md) — 本地运行（无外部模型请求）
- [16f Dense Retriever](rag/step_16f_dense_retriever.md) — 本地运行（无外部模型请求）
- [16g RRF 混合召回](rag/step_16g_hybrid_retriever.md) — 本地运行（无外部模型请求）
- [16h_01 评测集与基线](rag/step_16h_01_eval_dataset_and_ngram_baseline.md) — 本地运行（无外部模型请求）
- [16h_02 检索器对比](rag/step_16h_02_compare_retrievers.md) — 真实外部请求（可能收费）
- [16i_01 向量库决策](rag/step_16i_01_vector_database_decision.md) — 本地运行（无外部模型请求）
- [16i_02 正式接入决策](rag/step_16i_02_integration_decision.md) — 本地运行（无外部模型请求）
- [17a 无答案负例](rag/step_17a_no_answer_eval.md) — 本地运行（无外部模型请求）
- [17b Dense 分数边界](rag/step_17b_dense_score_eval.md) — 真实外部请求（可能收费）
- [17c_01 阈值取舍](rag/step_17c_01_threshold_tradeoff.md) — 本地运行（无外部模型请求）
- [17c_02 留出验证](rag/step_17c_02_holdout_eval.md) — 本地运行（无外部模型请求）
- [17d Dense 留出题](rag/step_17d_dense_holdout.md) — 真实外部请求（可能收费）
- [17e 证据审计](rag/step_17e_evidence_audit.md) — 本地运行（无外部模型请求）
- [17f RAG 阶段边界](rag/step_17f_rag_stage_boundary.md) — 本地运行（无外部模型请求）
- [17g RAG 代码复盘](rag/step_17g_rag_code_recap.md) — 本地运行（无外部模型请求）

## 阶段四：上下文工程

- [18a 轮数与 Token](context/step_18a_turn_window_vs_token_budget.md) — 本地运行（无外部模型请求）
- [18b 裁剪切片](context/step_18b_trim_history_slice.md) — 本地运行（无外部模型请求）
- [18c 跨窗口事实](context/step_18c_structured_fact_retention.md) — 本地运行（无外部模型请求）
- [18d 摘要记忆](context/step_18d_summary_memory_role.md) — 本地运行（无外部模型请求）
- [18e 摘要触发](context/step_18e_summary_trigger.md) — 本地运行（无外部模型请求）
- [18f 工具结果压缩](context/step_18f_tool_result_compression.md) — 本地运行（无外部模型请求）
- [18g 上下文信任边界](context/step_18g_context_trust_boundary.md) — 本地运行（无外部模型请求）
- [18h 上下文组装](context/step_18h_context_assembly.md) — 本地运行（无外部模型请求）
- [18i 上下文回归](context/step_18i_context_regression_eval.md) — 本地运行（无外部模型请求）
- [18j 上下文复盘](context/step_18j_context_stage_recap.md) — 本地运行（无外部模型请求）
- [18k 上下文观测](context/step_18k_context_metrics.md) — 本地运行（无外部模型请求）
- [18l 有限退款偏好](context/step_18l_long_dialogue_failure.md) — 本地运行（无外部模型请求）
- [18m HTTP 上下文演示](context/step_18m_http_context_demo.md) — 本地运行（无外部模型请求）

## 阶段五：LangChain / LangGraph

- [19a LangChain 接口映射](frameworks/step_19a_langchain_interfaces.md) — 本地运行（无外部模型请求）
- [19b LangChain 单次请求](frameworks/step_19b_langchain_single_call.md) — 真实外部请求（可能收费）
- [19c 单工具往返](frameworks/step_19c_langchain_order_tool.md) — 真实外部请求（可能收费）
- [19d 工具对象](frameworks/step_19d_langchain_tool_object.md) — 本地运行（无外部模型请求）
- [19e 工具对象往返](frameworks/step_19e_tool_object_roundtrip.md) — 真实外部请求（可能收费）
- [19f Agent 运行器](frameworks/step_19f_agent_runner.md) — 真实外部请求（可能收费）
- [20a State](frameworks/step_20a_langgraph_state.md) — 本地运行（无外部模型请求）
- [20b Node](frameworks/step_20b_langgraph_node.md) — 本地运行（无外部模型请求）
- [20c Edge](frameworks/step_20c_langgraph_edge.md) — 本地运行（无外部模型请求）
- [20d 条件边](frameworks/step_20d_conditional_route.md) — 本地运行（无外部模型请求）
- [20e Checkpoint](frameworks/step_20e_checkpoint.md) — 本地运行（无外部模型请求）
- [20f 中断与恢复](frameworks/step_20f_interrupt_resume.md) — 本地运行（无外部模型请求）
- [20g 节点失败](frameworks/step_20g_node_failure.md) — 本地运行（无外部模型请求）
- [20h Reducer](frameworks/step_20h_message_reducer.md) — 本地运行（无外部模型请求）
- [20i 显式工具循环图](frameworks/step_20i_tool_loop_graph.md) — 真实外部请求（可能收费）
- [20j 原生与图对照](frameworks/step_20j_native_graph_comparison.md) — 本地运行（无外部模型请求）
- [20k 会话接图](frameworks/step_20k_graph_conversation.md) — 本地运行（无外部模型请求）
- [20l 图版 HTTP 演示](frameworks/step_20l_http_graph_demo.md) — 本地运行（无外部模型请求）
- [20m 订单与知识双工具](frameworks/step_20m_knowledge_tool.md) — 本地运行（无外部模型请求）

