# 课程：step_09c_refresh_vectors.md；访问范围：当前命令只读或预览；写入/生成选项见下文。
"""第9C步：备份、生成新向量，再在一个事务中写新停旧。"""

import argparse
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from uuid import uuid4

from dotenv import dotenv_values

from app.core.config import get_settings
from app.rag.document_loader import load_markdown_documents
from app.services.embedding_service import EmbeddingService, EmbeddingServiceError
from learning.pgvector.step_03_insert_one_chunk import INSERT_SQL
from learning.pgvector.step_09_section_chunking import build_section_documents
from learning.pgvector.step_09b_refresh_plan import find_obsolete_chunk_ids
from learning.postgresql.step_03_python_order_lookup import connect_learning_db


MODEL = "text-embedding-v4"
DIMENSIONS = 1536
MAX_BATCH_SIZE = 10
HERE = Path(__file__).parent
PROJECT_ROOT = HERE.parents[1]
RECEIPT_PATH = HERE / "results" / "latest_section_refresh_receipt.json"


def digest(value) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sources_of(chunks) -> list[str]:
    sources = []
    for chunk in chunks:
        source = chunk.metadata["source"]
        if source not in sources:
            sources.append(source)
    return sorted(sources)


def read_rows(connection) -> list[dict]:
    # embedding_text只用于本地备份和哈希，绝不放进控制台结果。
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT chunk_id, source, content, embedding::text AS embedding_text, "
            "vector_dims(embedding) AS dimensions, "
            "vector_norm(embedding) > 0 AS nonzero_embedding "
            "FROM public.knowledge_chunks ORDER BY chunk_id"
        )
        return cursor.fetchall()


def order_state(connection) -> dict:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM public.orders ORDER BY order_id")
        rows = cursor.fetchall()
    return {"count": len(rows), "sha256": digest(rows)}


def read_snapshot() -> dict:
    with connect_learning_db() as connection:
        connection.read_only = True
        return {"rows": read_rows(connection), "orders": order_state(connection)}


def scoped_rows(rows, sources) -> list[dict]:
    selected = []
    for row in rows:
        if row["source"] in sources:
            selected.append(row)
    return selected


def make_plan(snapshot, chunks) -> dict:
    if not chunks or len(chunks) > MAX_BATCH_SIZE:
        raise RuntimeError("新候选必须非空，且本次最多10段。")
    ids = []
    for chunk in chunks:
        chunk_id = chunk.metadata["chunk_id"]
        if chunk_id in ids or not chunk.content.strip():
            raise RuntimeError("候选编号重复或正文为空。")
        ids.append(chunk_id)

    sources = sources_of(chunks)
    old_by_id = {}
    for row in snapshot["rows"]:
        old_by_id[row["chunk_id"]] = row
    existing_new_ids = []
    all_content_matches = True
    for chunk in chunks:
        chunk_id = chunk.metadata["chunk_id"]
        row = old_by_id.get(chunk_id)
        if row is None:
            all_content_matches = False
            continue
        existing_new_ids.append(chunk_id)
        if (
            row["source"] != chunk.metadata["source"]
            or row["content"] != chunk.content
            or row["dimensions"] != DIMENSIONS
            or not row["nonzero_embedding"]
        ):
            all_content_matches = False

    receipt_matches = False
    if RECEIPT_PATH.is_file():
        receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
        receipt_matches = (
            receipt.get("model") == MODEL
            and receipt.get("dimensions") == DIMENSIONS
            and receipt.get("sources") == sources
            and receipt.get("scope_fingerprint")
            == digest(scoped_rows(snapshot["rows"], sources))
        )
    obsolete_ids = find_obsolete_chunk_ids(snapshot["rows"], chunks)
    return {
        "sources": sources,
        "new_ids": ids,
        "obsolete_ids": obsolete_ids,
        "existing_new_ids": existing_new_ids,
        "already_current": all_content_matches and not obsolete_ids and receipt_matches,
        "existing_version_needs_review": bool(existing_new_ids) and not receipt_matches,
        "before_fingerprint": digest(snapshot["rows"]),
        "candidate_fingerprint": digest([asdict(chunk) for chunk in chunks]),
    }


def validate_vectors(chunks, vectors) -> None:
    if len(vectors) != len(chunks):
        raise RuntimeError("片段数与向量数不一致。")
    for vector in vectors:
        if len(vector) != DIMENSIONS:
            raise RuntimeError("新向量维度不是1536。")
        nonzero = False
        for value in vector:
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise RuntimeError("向量含无效数值。")
            if value != 0:
                nonzero = True
        if not nonzero:
            raise RuntimeError("不允许写入零向量。")


def replace_rows(connection, chunks, vectors, obsolete_ids) -> None:
    """事务内核心：逐段写入新记录，再按旧编号和来源范围删除旧记录。"""
    validate_vectors(chunks, vectors)
    sources = sources_of(chunks)
    with connection.cursor() as cursor:
        for chunk, vector in zip(chunks, vectors):
            params = (
                chunk.metadata["chunk_id"],
                chunk.metadata["source"],
                chunk.content,
                json.dumps(vector, allow_nan=False),
            )
            cursor.execute(INSERT_SQL, params)

        if obsolete_ids:
            cursor.execute(
                "DELETE FROM public.knowledge_chunks "
                "WHERE chunk_id = ANY(%s) AND source = ANY(%s)",
                (obsolete_ids, sources),
            )
            if cursor.rowcount != len(obsolete_ids):
                raise RuntimeError("实际移除数量与计划不符，事务应回滚。")


def verify_result(before, after, chunks) -> None:
    sources = sources_of(chunks)
    target = scoped_rows(after["rows"], sources)
    if len(target) != len(chunks):
        raise RuntimeError("更新范围内的记录数与新片段数不符。")
    by_id = {}
    for row in target:
        by_id[row["chunk_id"]] = row
    for chunk in chunks:
        row = by_id.get(chunk.metadata["chunk_id"])
        if (
            row is None
            or row["source"] != chunk.metadata["source"]
            or row["content"] != chunk.content
            or row["dimensions"] != DIMENSIONS
            or not row["nonzero_embedding"]
        ):
            raise RuntimeError("新正文、来源、编号或向量状态核对失败。")
    unrelated_before = []
    unrelated_after = []
    for row in before["rows"]:
        if row["source"] not in sources:
            unrelated_before.append(row)
    for row in after["rows"]:
        if row["source"] not in sources:
            unrelated_after.append(row)
    if digest(unrelated_before) != digest(unrelated_after):
        raise RuntimeError("更新范围以外的知识记录发生变化。")
    if before["orders"] != after["orders"]:
        raise RuntimeError("订单内容或数量发生变化。")


def write_json(path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_backup(snapshot, chunks, plan, purpose="refresh") -> Path:
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S")
    folder = HERE / "backups" / (stamp + "_" + purpose + "_" + uuid4().hex[:8])
    folder.mkdir(parents=True, exist_ok=False)
    write_json(folder / "knowledge_before.json", snapshot)
    write_json(folder / "manifest.json", {
        "purpose": purpose,
        "model": MODEL,
        "dimensions": DIMENSIONS,
        "plan": plan,
        "candidates": [asdict(chunk) for chunk in chunks],
    })
    return folder


def main() -> None:
    parser = argparse.ArgumentParser(description="预览实时向量更新计划，或一次生成新向量并事务替换。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="默认：只读核对实时数据库，不调用模型。")
    mode.add_argument("--write", action="store_true", help="备份后一次请求新向量，同事务写新停旧。")
    parser.add_argument("--expected-candidate-fingerprint", help="核对过的候选指纹；不同则在请求模型前停止。")
    args = parser.parse_args()

    chunks = build_section_documents(load_markdown_documents())
    if (
        args.expected_candidate_fingerprint
        and digest([asdict(chunk) for chunk in chunks]) != args.expected_candidate_fingerprint
    ):
        raise RuntimeError("候选与已核对范围不一致，未请求模型或写入数据库。")
    before = read_snapshot()
    plan = make_plan(before, chunks)
    settings = get_settings()
    root_env = dotenv_values(PROJECT_ROOT / ".env")
    root_key = root_env.get("DASHSCOPE_API_KEY")
    key_matches_root = bool(root_key) and settings.dashscope_api_key == root_key
    print(json.dumps({
        "mode": "write" if args.write else "read_only_preview",
        "configured_embedding_model": settings.embedding_model,
        "configured_dimensions": settings.embedding_dimensions,
        "effective_key_matches_root_env": key_matches_root,
        "knowledge_rows_before": len(before["rows"]),
        "orders_before": before["orders"],
        "plan": plan,
        "outgoing_document_candidates": [asdict(chunk) for chunk in chunks],
    }, ensure_ascii=False, indent=2))
    if not args.write:
        print("实时只读预览完成：未调用模型，未修改数据库。")
        return
    if plan["already_current"]:
        print("数据库与已验收生成记录一致，无需请求模型或写入。")
        return
    if plan["existing_version_needs_review"]:
        raise RuntimeError("新编号已存在但缺少匹配的生成记录，请先核对当前版本。")
    if (
        settings.embedding_provider.lower() != "dashscope"
        or settings.embedding_model != MODEL
        or settings.embedding_dimensions != DIMENSIONS
        or not key_matches_root
    ):
        raise RuntimeError("请核对V4/1536配置及本进程密钥来源，尚未请求Embedding。")

    backup = create_backup(before, chunks, plan)
    service = EmbeddingService(settings=settings)
    texts = []
    for chunk in chunks:
        texts.append(chunk.content)
    vectors = service.embed_documents(texts)
    validate_vectors(chunks, vectors)
    write_json(backup / "generated_vectors.json", {
        "model": MODEL, "dimensions": DIMENSIONS,
        "candidates": [asdict(chunk) for chunk in chunks], "vectors": vectors,
    })
    current_chunks = build_section_documents(load_markdown_documents())
    if digest([asdict(chunk) for chunk in current_chunks]) != plan["candidate_fingerprint"]:
        raise RuntimeError("请求期间本地知识文本变化，新向量已保存在备份目录，请先核对。")

    with connect_learning_db() as connection:
        connection.execute("LOCK TABLE public.knowledge_chunks IN SHARE ROW EXCLUSIVE MODE")
        locked = {"rows": read_rows(connection), "orders": order_state(connection)}
        if digest(locked["rows"]) != plan["before_fingerprint"] or locked["orders"] != before["orders"]:
            raise RuntimeError("请求期间数据库发生变化，未执行替换，请先重新核对。")
        replace_rows(connection, chunks, vectors, plan["obsolete_ids"])
        after_inside = {"rows": read_rows(connection), "orders": order_state(connection)}
        verify_result(before, after_inside, chunks)
    # 成功离开连接的with后才提交；异常离开时由psycopg回滚。
    after = read_snapshot()
    verify_result(before, after, chunks)
    receipt = {
        "model": MODEL, "dimensions": DIMENSIONS, "sources": plan["sources"],
        "scope_fingerprint": digest(scoped_rows(after["rows"], plan["sources"])),
        "candidate_fingerprint": plan["candidate_fingerprint"],
        "backup_directory": str(backup),
        "written_ids": plan["new_ids"], "retired_ids": plan["obsolete_ids"],
        "embedding_request_attempts": 1,
        "knowledge_rows_after": len(after["rows"]),
        "orders_after": after["orders"],
        "independent_readback_verified": True,
    }
    write_json(RECEIPT_PATH, receipt)
    report_path = HERE / "results" / (backup.name + "_refresh_result.json")
    write_json(report_path, receipt)
    print(json.dumps({"result": receipt, "result_file": str(report_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except EmbeddingServiceError as error:
        status = re.search(r"HTTP (\d+)", str(error))
        detail = "，HTTP " + status.group(1) if status else ""
        print("Embedding请求未成功" + detail + "；尚未写入数据库，不自动重试。")
        raise SystemExit(1) from None
    except Exception as error:
        print("执行未确认完成：" + type(error).__name__ + "。先只读核对状态，不要重复请求模型。")
        if isinstance(error, RuntimeError):
            print(str(error))
        raise SystemExit(1) from None
