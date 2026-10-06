# 页型卡-closing_appendix

- id: 页型卡-closing_appendix
- 卡型: 页型卡
- 标题: 转附录（正文→附录过渡）
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 章节

## 适用场景

演讲结束、问答结束后的附录过渡。标准顺序：Conclusion → Thank You → Q&A → Appendix，
本页是最后一环：列出附录条目备查，不演讲、不展开。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `closing_appendix`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题（如"附录"） |
| items | 是 | 数组；每项：t（附录标题）/ d（说明，选填） |
| note | 选填 | 过渡语（如"详细数据见附录，备查"） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |

## 纪律

- 附录页只列标题备查，不展开内容、不演讲。
- items 只列标题＋一句话说明，不许把正文搬进附录过渡页。

## 模板对应

程序/页面生成.py `t_closing_appendix`；PPTX 声明式映射见 程序/pptx映射.py `映射表["closing_appendix"]`
