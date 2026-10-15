# 课程：step_17c_01_threshold_tradeoff.md；访问范围：本地运行（无外部模型请求）。
from dataclasses import dataclass

from learning.rag.step_17b_dense_score_eval import DenseScoreObservation


# 2026-09-23 第 17B 步的真实 Top-1 结果，保留四位小数供本地教学。
# 这里不存 API Key 或向量；阈值也避开了这些分数的舍入边界。
RECORDED_OBSERVATIONS = [
    DenseScoreObservation("键盘支持蓝牙吗？", "products.md", "products.md", 0.3870),
    DenseScoreObservation("鼠标续航多久？", "products.md", "products.md", 0.3248),
    DenseScoreObservation("物流超过48小时没更新怎么办？", "shipping.md", "shipping.md", 0.5054),
    DenseScoreObservation("质量问题换货运费谁承担？", "after_sales.md", "after_sales.md", 0.3938),
    DenseScoreObservation("退款多久？", "after_sales.md", "after_sales.md", 0.5257),
    DenseScoreObservation("购买商品什么时候寄出？", "shipping.md", "shipping.md", 0.5619),
    DenseScoreObservation("快递两天没动静怎么办？", "shipping.md", "shipping.md", 0.3220),
    DenseScoreObservation("商品有优惠券吗？", None, "after_sales.md", 0.2708),
    DenseScoreObservation("能开增值税专用发票吗？", None, "after_sales.md", 0.1022),
    DenseScoreObservation("下单后能修改收货地址吗？", None, "shipping.md", 0.3873),
    DenseScoreObservation("退货运费谁承担？", None, "after_sales.md", 0.4516),
    DenseScoreObservation("轻风无线鼠标的电池能单独更换吗？", None, "products.md", 0.4205),
]


@dataclass(frozen=True)
class ThresholdTradeoff:
    threshold: float
    positive_passed: int
    positive_rejected: int
    negative_passed: int
    negative_rejected: int


def evaluate_threshold(
    observations: list[DenseScoreObservation],
    threshold: float,
) -> ThresholdTradeoff:
    """按 Top-1 分数比较阈值，统计正负例被放行或拒答的数量。"""
    if not observations:
        raise ValueError("评测观察值不能为空")

    positive_passed = 0
    positive_rejected = 0
    negative_passed = 0
    negative_rejected = 0

    for observation in observations:
        passed = observation.top_score >= threshold
        is_positive = observation.expected_source is not None

        if is_positive and passed:
            positive_passed += 1
        elif is_positive:
            positive_rejected += 1
        elif passed:
            negative_passed += 1
        else:
            negative_rejected += 1

    return ThresholdTradeoff(
        threshold=threshold,
        positive_passed=positive_passed,
        positive_rejected=positive_rejected,
        negative_passed=negative_passed,
        negative_rejected=negative_rejected,
    )


def main() -> None:
    print("规则：Top-1 分数 >= 阈值则放行，否则程序级拒答。")
    print("以下仅复算第 17B 步记录的 12 个分数，不请求百炼。\n")

    for threshold in (0.30, 0.40, 0.46):
        result = evaluate_threshold(
            observations=RECORDED_OBSERVATIONS,
            threshold=threshold,
        )
        print(
            f"阈值={result.threshold:.2f} "
            f"正例放行={result.positive_passed}/7 "
            f"正例误拒={result.positive_rejected}/7 "
            f"负例误放={result.negative_passed}/5 "
            f"负例拒答={result.negative_rejected}/5"
        )


if __name__ == "__main__":
    main()
