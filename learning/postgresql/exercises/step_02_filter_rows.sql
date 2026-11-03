-- PostgreSQL 第2题：按状态筛选多条订单。
-- 数据库：agent_learning；架构：public；表：orders。
-- 返回列（按此顺序）：order_id、status、product。
-- 筛选条件：状态不是字符串 '已完成'。
-- 提示：<> 表示不等于，文本值使用英文单引号。
-- 先预测会返回哪些订单号，再在下方自己写SQL，以英文分号结束。
-- 本题暂不要求结果行的顺序；写好后选中SQL，按Ctrl+Enter运行。
select order_id,status,product from orders where status != '已完成'
