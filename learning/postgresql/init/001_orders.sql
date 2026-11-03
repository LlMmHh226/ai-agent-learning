CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    product TEXT NOT NULL,
    tracking_number TEXT NOT NULL DEFAULT ''
);

INSERT INTO orders (order_id, status, product, tracking_number)
VALUES
    ('10001', '已发货', '机械键盘', 'SF1234567890'),
    ('10002', '待发货', '无线鼠标', ''),
    ('10003', '已完成', '显示器', 'YT9876543210')
ON CONFLICT (order_id) DO NOTHING;
