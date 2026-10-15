# 阶段复盘：能运行以后，再检验是否理解

[返回课程目录](../learning/README.md)

每阶段完成后做一次口述和一次小改动。不要以文件数量、测试通过或模型偶然答对代替理解。真实调用控制在当前实验需要的最小次数。

| 阶段 | 口述任务 | 本地练习 | 验收依据 |
| --- | --- | --- | --- |
| 原生 Agent | 解释一个订单问题的两次模型请求 | 在消息列表中区分 assistant Tool Call 和 tool Result | 参数来源、role、关联 ID、返回正文都能说明 |
| 基础 RAG | 从 Markdown 到 answer/sources | 对照物流原话和优惠券问题 | 说明检索空/非空两条分支，来源由Python产生 |
| 向量与评测 | 解释 Dense、RRF 与阈值 | 在固定分数样例上提高阈值 | 同时报告误放和误拒，不把相关度当概率 |
| 上下文 | 解释窗口外的10001如何恢复 | 对照history与facts以及模型副本 | 区分持久保存、输入组装、临时工具消息 |
| 框架 | 比较原生循环与20M | 顺着完整调用链找两个patch位置 | 指出真实业务与模拟模型边界，不误称正式迁移 |

## 原生 Tool Loop 六题

场景：新会话只有 system 和“查询订单10001物流单号”一条 user；模型第一次返回订单 Tool Call，Python 已拿到正确订单结果，但尚未第二次请求模型。

1. working_messages 中应有哪些角色，各自干什么？
2. 谁决定工具名？原生 arguments 是什么类型？谁执行查询？
3. 429 后重试与取得工具结果后再次请求有什么不同？
4. 向 working_messages 追加 tool 会自动更新 history 吗？
5. 最终 `return assistant_message.content` 返回给谁，之后发生什么？
6. 若工具结果正确，模型却说“查不到”，优先检查哪两处数据？

<details>
<summary>参考答案</summary>

1. system规则、user原问题、assistant调用请求、tool执行结果；此时尚无最终回答。
2. 模型提出名称和参数；原生 arguments 是JSON字符串，Python解析、校验并调度订单函数。
3. 重试处理失败请求，通常重发同一输入；工具循环处理成功的调用意图，再发送包含工具结果的新输入。公开版默认不自动重试。
4. 不会，它是副本列表；会话服务只在最终成功后保存assistant正文。
5. 回到 `answer = await llm_service.chat_with_messages(model_messages)`；随后保存事实、保存回答、裁剪并返回API。
6. 先查构造的 tool 消息：content是否正确序列化、tool_call_id是否关联正确；再查第二次实际发送的 messages 是否包含 assistant调用与tool结果。不能仅凭最终话术断言模型能力差。

</details>

## RAG 证据题

“退货运费谁承担？”召回一段只说明“质量问题换货运费由商家承担”的资料，分数很高。能否回答“退货运费由商家承担”？

<details>
<summary>参考答案</summary>

不能。退货与换货的业务条件不同，资料缺少退货运费规则。高分只表明文本相关，不保证答案充分。应区分检索误放、资料缺事实和生成越界。

</details>

## 上下文阶段口述验收（18N）

用自己的话说明：已有十轮历史时追加 user 后多少条；工具往返临时列表多少条；正常回答后多少条；裁剪后多少条；facts何时读写。

<details>
<summary>参考答案</summary>

在每轮只有user/最终assistant且system一条的前提下：history为21→22，工作副本追加一次Tool Call/Result为24；history保存最终回答后23，再裁剪为21。facts在请求前读取并组装，成功回答后写入本次事实。不同消息结构不能机械套用这些数字。

</details>

## 框架阶段设计题

把20M里的patch删掉是否完成正式图服务迁移？

<details>
<summary>参考答案</summary>

不会。删除替换后会调用原生LLMService。正式接入要有明确的图服务入口、真实模型配置、所需工具与对应规则、异常和循环上限、会话适配及回归验证。此课程保留实验，不自动迁移。

</details>
