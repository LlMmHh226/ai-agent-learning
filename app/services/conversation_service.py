import re

from app.services.llm_service import llm_service, DEFAULT_SYSTEM_PROMPT


MAX_HISTORY_TURNS = 10
ORDER_ID_PATTERN = re.compile(r"(?<!\d)\d{5}(?!\d)")
REFUND_PREFERENCE_STATEMENTS = {
    "暂不申请退款": "暂不申请退款",
    "现在申请退款": "现在申请退款",
}


def extract_refund_preference(message: str) -> str | None:
    """识别本步支持的完整独立声明，不猜测自由文本中的意图。

    参数：message来自当前用户输入；str。允许前后空白及句末句号/叹号。
    返回：支持的规范偏好字符串，供事实保存或消息组装使用；其余输入返回None。
        提问、否定、引用、条件句及复合句不会因为包含关键词就命中。
    """
    statement = message.strip().rstrip("。.!！").strip()
    return REFUND_PREFERENCE_STATEMENTS.get(statement)


class ConversationService:
    def __init__(self) -> None:
        self.histories: dict[str, list[dict[str, str]]] = {}
        self.facts: dict[str, dict[str, str]] = {}

    def _get_history(
            self,
            conversation_id: str,
    ) -> list[dict[str, str]]:
        if conversation_id not in self.histories:
            self.histories[conversation_id] = [
                {
                    "role": "system",
                    "content": DEFAULT_SYSTEM_PROMPT
                }
            ]
        return self.histories[conversation_id]

    async def chat(
            self,
            conversation_id: str,
            message: str
    ) -> str:
        history = self._get_history(conversation_id)
        history.append(
            {
                "role": "user",
                "content": message
            }
        )
        try:
            model_messages = self._build_model_messages(
                conversation_id,
                history,
            )
            answer = await llm_service.chat_with_messages(model_messages)
        except Exception:
            history.pop()
            raise
        self._remember_facts(conversation_id, message)
        history.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
        self._trim_history(history)
        return answer

    def _trim_history(
            self,
            history: list[dict[str, str]],
    ) -> None:
        # 每轮包含一条 user 和一条 assistant；system 消息始终保留。
        max_regular_messages = MAX_HISTORY_TURNS * 2
        if len(history) > max_regular_messages + 1:
            del history[1:-max_regular_messages]

    def _remember_facts(
            self,
            conversation_id: str,
            message: str,
    ) -> None:
        """成功回复后记录当前输入的订单号与已选订单的明确退款偏好。

        conversation_id为当前会话ID，message为当前用户字符串；均由chat传入。
        原地更新facts，返回None。订单变化时清除旧订单偏好，避免带到另一个订单。
        只记录用户意愿，不代表已执行或授权退款。
        """
        order_ids = ORDER_ID_PATTERN.findall(message)
        if order_ids:
            conversation_facts = self.facts.setdefault(conversation_id, {})
            if conversation_facts.get("current_order_id") != order_ids[-1]:
                conversation_facts.pop("current_refund_preference", None)
            conversation_facts["current_order_id"] = order_ids[-1]

        refund_preference = extract_refund_preference(message)
        conversation_facts = self.facts.get(conversation_id, {})
        if refund_preference is not None and conversation_facts.get("current_order_id"):
            conversation_facts["current_refund_preference"] = refund_preference

    def _build_model_messages(
            self,
            conversation_id: str,
            history: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """从当前会话历史复制模型消息，再加入该会话的结构化背景。

        conversation_id和history由chat传入；前者选facts，后者含当前user消息。
        返回新列表给model_messages，不改保存的原历史。编号入system副本；
        历史退款偏好入最后user的数据区，当前明确声明或换订单时不注入旧偏好。
        """
        messages = [dict(item) for item in history]
        conversation_facts = self.facts.get(conversation_id, {})
        current_order_id = conversation_facts.get("current_order_id")

        if current_order_id:
            messages[0]["content"] += (
                f"\n会话重要事实：当前关注的订单编号是 {current_order_id}。"
                "涉及该订单状态或物流时，请调用订单查询工具获取最新信息。"
            )

        refund_preference = conversation_facts.get("current_refund_preference")
        if refund_preference and current_order_id and messages[-1]["role"] == "user":
            current_message = messages[-1]["content"]
            current_statement = extract_refund_preference(current_message)
            mentioned_order_ids = ORDER_ID_PATTERN.findall(current_message)
            selects_other_order = (
                bool(mentioned_order_ids) and mentioned_order_ids[-1] != current_order_id
            )
            if current_statement is None and not selects_other_order:
                messages[-1]["content"] = (
                    "【此前明确表达的订单偏好（历史数据，当前表达优先）】\n"
                    f"订单{current_order_id}：{refund_preference}。\n"
                    "这项历史数据不代表已经执行或授权退款。\n\n"
                    f"【当前用户问题】\n{current_message}"
                )

        return messages

    def clear(self, conversation_id: str) -> bool:
        cleared = self.histories.pop(conversation_id, None) is not None
        self.facts.pop(conversation_id, None)
        return cleared


conversation_service = ConversationService()
