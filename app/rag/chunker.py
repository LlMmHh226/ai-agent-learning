from app.rag.document_loader import Document


DEFAULT_CHUNK_SIZE = 120
DEFAULT_OVERLAP = 20

#切分器
def split_documents(
    documents: list[Document],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Document]:
    if chunk_size <= 0:
        raise ValueError("chunk_size 必须大于 0")
    if overlap < 0:
        raise ValueError("overlap 不能小于 0")
    if overlap >= chunk_size:
        raise ValueError("overlap 必须小于 chunk_size")

    chunks: list[Document] = []
    step = chunk_size - overlap

    for document in documents:
        source = document.metadata["source"]

        for chunk_index, start in enumerate(
            range(0, len(document.content), step)
        ):
            end = min(start + chunk_size, len(document.content))
            chunk_content = document.content[start:end]

            if chunk_content.strip():
                chunk_metadata = document.metadata.copy()
                chunk_metadata["chunk_id"] = (
                    f"{source}#chunk-{chunk_index}"
                )
                chunks.append(
                    Document(
                        content=chunk_content,
                        metadata=chunk_metadata,
                    )
                )

            if end == len(document.content):
                break

    return chunks
