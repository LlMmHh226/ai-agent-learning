# 课程：step_09b_refresh_plan.md；访问范围：本地资料演示，无数据库和模型请求。
"""第9B步：根据固定教学示例，规划本次知识版本中待停用的旧编号。"""

import argparse
import json
from pathlib import Path

from app.rag.document_loader import Document, load_markdown_documents
from learning.pgvector.step_09_section_chunking import build_section_documents


INVENTORY_PATH = Path(__file__).with_name("fixtures") / "old_chunk_inventory.json"


def find_obsolete_chunk_ids(
    saved_rows: list[dict[str, object]],
    new_chunks: list[Document],
) -> list[str]:
    """按本次更新范围筛选旧编号，只返回计划，不修改数据。

    仅停用：来源属于本次new_chunks，且chunk_id不在新编号列表中的旧记录。
    保留其他来源和仍在新版本中的编号；顺序与saved_rows一致，不修改输入。
    new_chunks为空时返回[]。
    """
    # 1. 从新候选中收集：这次更新哪些来源，新编号有哪些。
    target_sources = []
    new_ids = []
    for chunk in new_chunks:
        new_source = chunk.metadata["source"]
        if new_source not in target_sources:
            target_sources.append(new_source)
        new_ids.append(chunk.metadata["chunk_id"])

    # 2. 遍历旧记录，找出本次范围内已经不在新版本中的编号。
    obsolete_ids = []
    for row in saved_rows:
        old_source = row["source"]
        old_id = row["chunk_id"]
        if old_source in target_sources:
            if old_id not in new_ids:
                obsolete_ids.append(old_id)

    # 3. 把编号清单返回给main；这里没有数据库写入。
    return obsolete_ids


def main() -> None:
    parser = argparse.ArgumentParser(description="本地查看盘点输入，或列出待停用旧片段的计划。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="显示快照与新候选；默认模式。")
    mode.add_argument("--plan", action="store_true", help="执行筛选函数，打印旧编号清单。")
    args = parser.parse_args()

    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    saved_rows = inventory["knowledge_rows"]
    new_chunks = build_section_documents(load_markdown_documents())

    saved_summary = []
    for row in saved_rows:
        saved_summary.append({
            "source": row["source"],
            "chunk_id": row["chunk_id"],
            "dimensions": row["dimensions"],
        })

    new_summary = []
    for chunk in new_chunks:
        new_summary.append({
            "source": chunk.metadata["source"],
            "chunk_id": chunk.metadata["chunk_id"],
        })

    # 摘要展开了字段；这里单独展示一个Document原本的content/metadata层次。
    new_chunk_example = None
    if new_chunks:
        first_chunk = new_chunks[0]
        new_chunk_example = {
            "content": first_chunk.content,
            "metadata": first_chunk.metadata,
        }

    print(json.dumps({
        "input_origin": "固定示例，不是当前数据库状态；实时情况用第9C步--preview核对。",
        "inventory_file": str(INVENTORY_PATH),
        "inventory_date": inventory["date"],
        "saved_rows_summary": saved_summary,
        "new_chunks_summary": new_summary,
        "new_chunk_example": new_chunk_example,
        "saved_count": len(saved_rows),
        "new_candidate_count": len(new_chunks),
    }, ensure_ascii=False, indent=2))

    if not args.plan:
        print("预览结束。运行--plan执行编号筛选并查看待停用清单。")
        return

    obsolete_ids = find_obsolete_chunk_ids(saved_rows, new_chunks)
    print("\n本次计划中待停用的旧编号：")
    print(json.dumps({
        "obsolete_count": len(obsolete_ids),
        "obsolete_chunk_ids": obsolete_ids,
        "new_candidate_count": len(new_chunks),
        "model_requests": 0,
        "database_writes": 0,
    }, ensure_ascii=False, indent=2))
    print("这只是计划。本步未生成向量、未连接数据库、未删除或写入任何知识记录。")


if __name__ == "__main__":
    main()
