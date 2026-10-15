from dataclasses import dataclass

from app.rag.document_loader import Document


DEFAULT_NGRAM_SIZE = 2


@dataclass
class RetrievalResult:
    document: Document
    score: float

#去掉标点、空格，英文统一转小写，只保留字母和数字
def normalize_text(text: str) -> str:
    """
    将文本整理成便于字符匹配的形式。

    参数:
        text:
            等待整理的原始文本。它可能来自用户问题，也可能来自
            Document.content。

    返回:
        删除标点和空白、并将英文字母转成小写后的字符串。
    """
    return "".join(character.lower() for character in text if character.isalnum())

#把文本拆成连续的字符组（默认每组 2 个字符）
def build_char_ngrams(
    text: str,
    ngram_size: int = DEFAULT_NGRAM_SIZE,
) -> set[str]:
    """
    从文本中提取连续的中文字符 n-gram。

    参数:
        text:
            等待提取特征的文本。调用者会传入用户问题或 chunk 正文。

        ngram_size:
            每个字符组包含几个连续字符。默认值 2 表示二元字符组，
            例如“热插拔”会得到“热插”和“插拔”。

    返回:
        去重后的字符组集合。集合中的每个元素都是一个字符串。
    """
    if ngram_size <= 0:
        raise ValueError("ngram_size 必须大于 0")

    normalized_text = normalize_text(text)

    if not normalized_text:
        return set()
    if len(normalized_text) <= ngram_size:
        return {normalized_text}

    return {
        normalized_text[start : start + ngram_size]
        for start in range(len(normalized_text) - ngram_size + 1)
    }


def calculate_ngram_similarity(
    query: str,
    chunk_text: str,
    ngram_size: int = DEFAULT_NGRAM_SIZE,
) -> float:
    """
    计算用户问题与一个 chunk 的字符 n-gram 相似度。

    参数:
        query:
            用户输入的问题，由调用检索器的代码传入。

        chunk_text:
            一个候选 chunk 的正文，来自 Document.content。

        ngram_size:
            字符组长度。它会原样传给 build_char_ngrams()。

    返回:
        0.0 到 1.0 之间的分数。分数表示用户问题中的字符组有多大
        比例也出现在候选 chunk 中。
    """
    query_ngrams = build_char_ngrams(query, ngram_size)
    chunk_ngrams = build_char_ngrams(chunk_text, ngram_size)

    if not query_ngrams:
        return 0.0

    matched_ngrams = query_ngrams & chunk_ngrams
    return len(matched_ngrams) / len(query_ngrams)

#检索器
def retrieve(
    query: str,
    chunks: list[Document],
    top_k: int = 3,
    ngram_size: int = DEFAULT_NGRAM_SIZE,
    min_score: float = 0.0,
) -> list[RetrievalResult]:
    """
    从候选 chunks 中返回与用户问题最相关的结果。

    参数:
        query:
            用户问题，例如“星云机械键盘支持热插拔吗？”。

        chunks:
            候选文档片段列表，来自 split_documents() 的返回值。

        top_k:
            最多返回多少个结果。默认返回得分最高的 3 个。

        ngram_size:
            相似度计算使用的字符组长度，默认每组 2 个字符。

        min_score:
            结果需要达到的最低相似度，范围是 0.0 到 1.0。默认值
            0.0 保持原有行为；RAGService 当前传入 0.3。

    返回:
        按 score 从高到低排列的 RetrievalResult 列表。每个结果同时
        保存原 chunk 和相似度分数；零分结果不会返回。
    """
    if top_k <= 0:
        raise ValueError("top_k 必须大于 0")
    if not 0.0 <= min_score <= 1.0:
        raise ValueError("min_score 必须在 0.0 到 1.0 之间")

    results: list[RetrievalResult] = []

    for chunk in chunks:
        score = calculate_ngram_similarity(
            query=query,
            chunk_text=chunk.content,
            ngram_size=ngram_size,
        )
        if score > 0 and score >= min_score:
            results.append(
                RetrievalResult(
                    document=chunk,
                    score=score,
                )
            )

    results.sort(
        key=lambda result: result.score,
        reverse=True,
    )
    return results[:top_k]
