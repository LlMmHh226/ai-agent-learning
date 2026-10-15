# 课程：step_17e_evidence_audit.md；访问范围：本地运行（无外部模型请求）。
from dataclasses import dataclass

from app.rag.document_loader import load_markdown_documents


@dataclass(frozen=True)
class EvidenceAuditCase:
    question: str
    top_source: str
    recorded_score: float
    required_fact: str
    source_excerpt: str
    human_conclusion: str


# 分数与 Top-1 来源来自第 17D 步的真实评测；本脚本不重新请求百炼。
AUDIT_CASES = [
    EvidenceAuditCase(
        question="预售商品按什么时候发货？",
        top_source="shipping.md",
        recorded_score=0.5604,
        required_fact="预售商品的发货时间规则",
        source_excerpt="预售商品按照商品页面标注的日期发货。",
        human_conclusion="足够：可以回答按商品页面标注日期发货",
    ),
    EvidenceAuditCase(
        question="星云机械键盘能同时连接几台设备？",
        top_source="products.md",
        recorded_score=0.5615,
        required_fact="同时连接设备的数量",
        source_excerpt="支持 USB-C 有线连接和蓝牙 5.0 连接。",
        human_conclusion="不足：只说明连接方式，未说明同时连接数量",
    ),
    EvidenceAuditCase(
        question="物流由哪家快递公司配送？",
        top_source="shipping.md",
        recorded_score=0.5786,
        required_fact="承运快递公司的名称",
        source_excerpt="商品发出后，用户可以在订单详情页查看物流单号和最新轨迹。",
        human_conclusion="不足：只说明在哪里查轨迹，未说明快递公司名称",
    ),
]


def main() -> None:
    documents = load_markdown_documents()
    documents_by_source = {
        document.metadata["source"]: document
        for document in documents
    }

    for case in AUDIT_CASES:
        document = documents_by_source[case.top_source]
        if case.source_excerpt not in document.content:
            raise ValueError(
                f"标注片段不在真实知识文档中：{case.top_source}"
            )

        print(f"问题：{case.question}")
        print(f"Dense Top-1：{case.top_source}，记录分数：{case.recorded_score:.4f}")
        print(f"回答所需事实：{case.required_fact}")
        print(f"文档实际片段：{case.source_excerpt}")
        print(f"人工核对：{case.human_conclusion}\n")


if __name__ == "__main__":
    main()
