"""22D：按 SKU 精确查询样例规格与库存；本课先写普通函数。"""

import argparse
import json


SAMPLE_PRODUCT_SKUS = {
    "KB-WHITE-RED": {
        "sku_id": "KB-WHITE-RED", "product_id": "P-KEYBOARD", "product_name": "星云机械键盘",
        "variant": "白色 / 红轴", "price_cents": 29900, "currency": "CNY", "available_stock": 12,
    },
    "KB-BLACK-BROWN": {
        "sku_id": "KB-BLACK-BROWN", "product_id": "P-KEYBOARD", "product_name": "星云机械键盘",
        "variant": "黑色 / 茶轴", "price_cents": 31900, "currency": "CNY", "available_stock": 0,
    },
}


def get_product_sku(sku_id: str) -> dict[str, object]:
    sku = SAMPLE_PRODUCT_SKUS.get(sku_id)
    if sku is None:
        return {"found": False, "message": "没有找到该 SKU"}
    return {"found": True, **sku}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sku-id", help="指定一个 SKU；省略时验证存在、零库存和不存在三种情况")
    args = parser.parse_args()
    if args.sku_id is None:
        assert get_product_sku("KB-WHITE-RED")["available_stock"] == 12
        out_of_stock = get_product_sku("KB-BLACK-BROWN")
        assert out_of_stock["found"] is True and out_of_stock["available_stock"] == 0
        assert get_product_sku("UNKNOWN")["found"] is False
        candidates = ("KB-WHITE-RED", "KB-BLACK-BROWN", "UNKNOWN")
    else:
        candidates = (args.sku_id,)
    for sku_id in candidates:
        print(sku_id, json.dumps(get_product_sku(sku_id), ensure_ascii=False))


if __name__ == "__main__":
    main()
