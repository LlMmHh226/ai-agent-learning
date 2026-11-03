-- PostgreSQL 第1题：由你写一条 SELECT 查询。
-- 数据表：orders
-- 需要返回的列（按此顺序）：order_id、status、product、tracking_number
-- 只取 order_id 等于字符串 '10001' 的那一行。
-- 预期：1行，订单10001、已发货、机械键盘、SF1234567890。
-- 在下面写SQL，以英文分号结束。可以参考讲义中的 books 示例。
select  order_id,status,product,tracking_number from orders where order_id = '10001';
