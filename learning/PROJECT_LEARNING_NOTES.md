# 项目学习总笔记

[课程目录](README.md) · [完整架构](../docs/architecture.md) · [阶段复盘](../docs/recap.md)

## 从 HTTP 到模型

Schema 校验输入；API 将请求交给 Service 并包装响应；Service 编排业务；Tool 执行明确的本地操作。`POST /api/chat` 是单次原生聊天，`POST /api/chat/conversation` 加会话管理，`POST /api/rag/chat` 先检索再生成。URL由调用方选择，不由模型选择。

原生工具循环中的四条消息：system规则、user问题、assistant提出工具调用、tool返回执行结果。模型选择名称和参数，Python解析校验并执行；最终无 tool_calls 时返回正文。工具结果的 `tool_call_id` 关联提出该调用的ID。

## 会话与上下文

`history` 保存system、用户原话和最终回答；`facts` 保存订单号及有限的独立退款偏好。`model_messages` 是本轮组装的副本；`working_messages` 在工具循环中追加临时工具消息。不能把这四者视为同一份数据。

成功路径：读取已有facts → 组装输入 → 获得回答 → 保存本次事实 → 保存assistant → 裁剪历史。窗口保存十轮，不等于固定Token预算。事实在窗口外保留仍需重新组装进模型输入才能被看到。

自动摘要、通用偏好提取、Token预算裁剪和持久化尚未接入正式会话。学习脚本中的人工摘要、压缩和观测用于解释取舍，不是生产能力声明。

## RAG 的两段流程

离线准备或初始化：Markdown → Document(content, metadata) → chunk；请求时：query → retrieve → 空结果拒答，非空结果构建Prompt、调用模型、构造sources。

正式检索使用字符n-gram，短知识文档默认按文档级chunk处理。阈值控制进入候选的最低分，Top-K限制返回数量；两者都不能判断资料是否具备所有必要事实。例：“换货运费由商家承担”不能推出“退货运费由商家承担”。

Prompt分开系统规则、知识资料、用户问题、输出要求。资料是不可信数据，不得因文档包含“忽略规则”而升级为指令。Python从检索对象构造sources，仍需核对答案断言是否受证据支持。

## 向量与融合

Embedding把文本映射为固定长度浮点向量。知识用document模式，查询用query模式；完整向量参与相似度，前五维只用于预览。单维通常没有稳定的人类语义标签。

Dense Retriever使用文档向量缓存与余弦排序。缓存键应反映内容和模型配置，避免文件内容更新后误用旧向量。Hybrid使用RRF融合两个检索器的排名，避免直接相加不具可比性的原始分数。

这些组件是独立实验，正式RAGService仍用n-gram。向量数据库不是Embedding的必要条件；本例少量向量可内存排序，规模、持久化、更新与过滤需求增长后再评估数据库。

## 评测与证据

Recall看相关资料找回多少，Precision看返回候选里相关项占多少；答案事实支持与引用正确需要额外评测。阈值提高可能减少负例误放，也可能增加正例误拒。调参题与留出题分离，看过结果并据此调规则后，就需要新的独立验证题。

模拟模型验证程序如何处理响应，真实调用验证服务与模型在具体题上的行为；两者都不能单凭少量样本证明生产可靠性。历史分数样例可用来理解取舍，不作为本版本模型效果报告。

## 框架映射

LangChain把消息和工具包装为对象；`bind_tools`只提供工具说明，`create_agent`接管循环。LangGraph通过State、Node、Edge和条件边显式组织执行，Reducer规定字段更新规则，Checkpoint保存图状态。

20M演示中，ConversationService继续负责历史与facts，适配函数把字典消息转成框架消息，图执行后再取正文返回。两个patch分别改变服务入口和模型生成；图和业务工具实际执行，模型选择与回答模拟。详细跟进路线见架构文档。
