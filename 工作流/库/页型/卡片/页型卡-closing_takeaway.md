# 页型卡-closing_takeaway

- id: 页型卡-closing_takeaway
- 卡型: 页型卡
- 标题: 回顾锚点（一句话核心信息收束）
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 观点

## 适用场景

演讲收束：把全场浓缩成一句话——标准是"听众能转述给老板的一句话"。
Q&A 之后打回本页收束（Q&A 页绝不能是最后一页）。takeaway 超大字居中；
thanks 只许小字致谢；contact 选填。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `closing_takeaway`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| takeaway | 是 | 一句话核心信息（≤30 字，超大字居中） |
| thanks | 选填 | 小字致谢（不许做 headline 级信息主体） |
| contact | 选填 | 联系方式 |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- takeaway 必须是一句话，不许展开成段落；不许引入新论点/新数据。
- "谢谢"不许做 headline 级信息主体（口头致谢或小字 thanks）。
- 问答环节之后必须打回本页（或 CTA 页）收束，不许以 Q&A 页结束。

## 模板对应

程序/页面生成.py `t_closing_takeaway`；PPTX 声明式映射见 程序/pptx映射.py `映射表["closing_takeaway"]`
