# 课程：step_09_section_chunking.md；访问范围：本地资料演示，无数据库和模型请求。
"""第9步：按Markdown二级标题切分，先在本地核对片段边界。"""

import argparse
from dataclasses import asdict
import json

from app.rag.chunker import split_documents
from app.rag.document_loader import Document, load_markdown_documents


NEGATIVE_SENTENCE = "- 本商品没有标注防水或防泼溅能力。"


def split_by_heading(text: str) -> list[str]:
    """独立实现：按行首'## '划分章节，返回按原顺序排列的完整片段文本。

    每个二级标题和正文放在同一片段；首个标题前的内容保留在第一片段。
    空白输入返回[]；没有二级标题时将完整非空原文作为一个片段。
    可以去除片段首尾空白，不删除或重复原文的非空行。
    """
    lines = text.splitlines()

    chunks = []  # 已经完成的片段
    current_lines = []  # 正在收集的这一节
    heading_count = 0  # 已经遇到的二级标题数量

    for line in lines:
        if line.startswith("## "):
            heading_count = heading_count + 1

            # 遇到第二个及后续标题，说明上一节结束了
            if heading_count > 1:
                chunk_text = "\n".join(current_lines).strip()
                if chunk_text:
                    chunks.append(chunk_text)

                current_lines = []

        # 将当前行放进这一节，包括刚遇到的新标题
        current_lines.append(line)

    # 文件读完后，保存最后一节
    chunk_text = "\n".join(current_lines).strip()
    if chunk_text:
        chunks.append(chunk_text)

    return chunks


def build_section_documents(documents: list[Document]) -> list[Document]:
    """辅助包装：为切分函数返回的片段附上来源和独立的section编号。"""
    chunks: list[Document] = []
    for document in documents:
        sections = split_by_heading(document.content)
        for index, text in enumerate(sections):
            metadata = document.metadata.copy()
            metadata["chunk_id"] = f"{metadata['source']}#section-{index}"
            chunks.append(Document(content=text, metadata=metadata))
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="复现旧切分问题，或本地预览按章节生成的新片段。")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preview", action="store_true", help="展示旧问题与输入结构；默认模式。")
    mode.add_argument("--split", action="store_true", help="执行你写的split_by_heading并打印新片段。")
    args = parser.parse_args()

    documents = load_markdown_documents()
    old_chunks = split_documents(documents)
    problem_chunk = next(
        (chunk for chunk in old_chunks if chunk.metadata["chunk_id"] == "products.md#chunk-1"),
        None,
    )
    heading_counts = {
        document.metadata["source"]: sum(line.startswith("## ") for line in document.content.splitlines())
        for document in documents
    }
    print(json.dumps({
        "input_origin": "当前本地Markdown；未连接数据库。",
        "document_count": len(documents),
        "old_chunk_size": 120,
        "old_overlap": 20,
        "old_chunk_count": len(old_chunks),
        "old_problem_chunk": asdict(problem_chunk) if problem_chunk is not None else None,
        "complete_sentence_to_keep": NEGATIVE_SENTENCE,
        "h2_heading_counts": heading_counts,
        "expected_new_chunk_count": sum(count or 1 for count in heading_counts.values()),
    }, ensure_ascii=False, indent=2))

    if not args.split:
        print("预览结束。完成split_by_heading后运行--split，才会构造新片段。")
        return

    new_chunks = build_section_documents(documents)
    print("\n按章节构造的新候选片段：")
    print(json.dumps({
        "new_chunk_count": len(new_chunks),
        "chunks": [asdict(chunk) for chunk in new_chunks],
    }, ensure_ascii=False, indent=2))
    print("这里只打印本地候选；未请求模型、未更新数据库向量、未切换正式切分器。")


if __name__ == "__main__":
    main()
