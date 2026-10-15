from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_DIR = PROJECT_ROOT / "data" / "knowledge"


@dataclass
class Document:
    content: str
    metadata: dict[str, str]

#加载器
def load_markdown_documents(
    directory: Path = DEFAULT_KNOWLEDGE_DIR,
) -> list[Document]:
    if not directory.exists():
        raise FileNotFoundError(f"知识库目录不存在：{directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"知识库路径不是目录：{directory}")

    documents: list[Document] = []

    for file_path in sorted(directory.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        document = Document(
            content=content,
            metadata={"source": file_path.name},
        )
        documents.append(document)

    return documents
