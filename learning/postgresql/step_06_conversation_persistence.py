"""06：在独立教学表保存最近问答与会话事实；默认预览，无外部模型。"""

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
from uuid import uuid4

import psycopg
from dotenv import dotenv_values
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


SELECT = "SELECT messages, facts, revision FROM public.lesson_conversations WHERE conversation_id = %s"
INSERT = (
    "INSERT INTO public.lesson_conversations (conversation_id, messages, facts, revision) "
    "VALUES (%s, %s, %s, %s) ON CONFLICT (conversation_id) DO NOTHING RETURNING revision"
)
UPDATE = (
    "UPDATE public.lesson_conversations SET messages = %s, facts = %s, revision = %s "
    "WHERE conversation_id = %s AND revision = %s::uuid RETURNING revision"
)
DELETE = "DELETE FROM public.lesson_conversations WHERE conversation_id = %s RETURNING conversation_id"
SAMPLE_MESSAGES = [
    {"role": "user", "content": "请查询订单10001的物流。"},
    {"role": "assistant", "content": "样例订单10001已发货。"},
]
SAMPLE_FACTS = {"last_order_id": "10001"}


@dataclass(frozen=True)
class Snapshot:
    messages: list[dict[str, str]]
    facts: dict[str, str]
    revision: str


class RevisionConflict(RuntimeError):
    """写入期间，读取的会话版本已经变化。"""


def connect():
    values = dotenv_values(Path(__file__).resolve().parents[2] / ".env")
    password = os.environ.get("POSTGRES_PASSWORD", values.get("POSTGRES_PASSWORD"))
    port = os.environ.get("POSTGRES_PORT", values.get("POSTGRES_PORT") or "25432")
    if not password:
        raise ValueError("请先在根目录 .env 配置教学库的 POSTGRES_PASSWORD。")
    if not re.fullmatch(r"[0-9]{1,5}", port) or not 0 < int(port) <= 65535:
        raise ValueError("教学库的 POSTGRES_PORT 必须是有效端口。")
    return psycopg.connect(
        host="127.0.0.1", port=int(port), dbname="agent_learning", user="learner",
        password=password, row_factory=dict_row, connect_timeout=5,
        options="-c statement_timeout=5000",
    )


def load(conversation_id: str) -> Snapshot | None:
    with connect() as connection:
        result = connection.execute(SELECT, (conversation_id,)).fetchone()
    if result is None:
        return None
    return Snapshot(result["messages"], result["facts"], str(result["revision"]))


def save(conversation_id: str, messages: list[dict[str, str]], facts: dict[str, str],
         expected_revision: str | None) -> str:
    revision = uuid4()
    with connect() as connection:
        if expected_revision is None:
            result = connection.execute(INSERT, (conversation_id, Jsonb(messages), Jsonb(facts), revision))
        else:
            result = connection.execute(
                UPDATE, (Jsonb(messages), Jsonb(facts), revision, conversation_id, expected_revision),
            )
        if result.fetchone() is None:
            raise RevisionConflict("版本冲突：请重新读取，旧快照没有覆盖新数据。")
    return str(revision)


def clear(conversation_id: str) -> bool:
    with connect() as connection:
        return connection.execute(DELETE, (conversation_id,)).fetchone() is not None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("preview", "write", "read", "conflict", "clear"), default="preview")
    parser.add_argument("--conversation-id")
    args = parser.parse_args()
    if args.mode == "preview":
        print("离线预览：一行保存成对的问答、事实字典和一个版本号。")
        print(json.dumps({"messages": SAMPLE_MESSAGES, "facts": SAMPLE_FACTS}, ensure_ascii=False))
        print("并发更新条件：", UPDATE)
        return 0

    conversation_id = args.conversation_id
    if not conversation_id or not re.fullmatch(r"lesson-[a-z0-9-]{1,48}", conversation_id):
        parser.error("请指定独立教学会话 ID，例如 --conversation-id lesson-demo-06。")
    try:
        if args.mode == "clear":
            print("教学记录已清理" if clear(conversation_id) else "没有此教学记录")
            return 0
        snapshot = load(conversation_id)
        if args.mode == "read":
            print(json.dumps(asdict(snapshot) if snapshot else None, ensure_ascii=False, indent=2))
        elif args.mode == "write":
            print("保存成功，revision =", save(
                conversation_id, SAMPLE_MESSAGES, SAMPLE_FACTS, snapshot.revision if snapshot else None,
            ))
        elif snapshot is None:
            print("请先对这个 ID 运行 --mode write。")
            return 1
        else:
            save(conversation_id, snapshot.messages, snapshot.facts, snapshot.revision)
            try:
                save(conversation_id, snapshot.messages, snapshot.facts, snapshot.revision)
            except RevisionConflict:
                print("版本检查通过：第二次写入使用旧 revision，被拒绝。")
            else:
                raise AssertionError("旧 revision 不应覆盖已经提交的新版本")
    except ValueError as error:
        print(str(error))
        return 1
    except RevisionConflict as error:
        print(str(error))
        return 1
    except psycopg.Error:
        print("教学库操作失败。请检查容器、端口、密码和教学表是否已创建。")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
