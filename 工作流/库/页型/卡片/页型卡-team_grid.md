# 页型卡-team_grid

- id: 页型卡-team_grid
- 卡型: 页型卡
- 标题: 人物介绍（2–4 人）
- 来源轨: 库内装配
- 生产者: Muse
- 状态: 草案（2026-10-06）
- 版式族: 图文

## 适用场景

团队介绍、嘉宾介绍、核心成员展示：2–4 人横向人物卡，
每卡＝肖像（圆形）＋姓名＋职位＋一句话。区别于 testimonial
（testimonial 是单人证言＋结果数字，本页是多人身份展示）。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id |
| tpl | 是 | 固定 `team_grid`（闭集） |
| brow/no/kick | 是 | 页眉左/页眉右页码/金色 kick 眉题 |
| title | 是 | 标题 |
| members | 是 | 数组，2–4 项；每项：photo（肖像图，必填）/ name（姓名，必填）/ role（职位，必填）/ bio（一句话介绍，选填） |
| foot | 是 | 底部右注 |
| bg | 否 | 背景纹理：dots/grid/diagonal/mesh/glow（闭集） |
| mask | 否 | 肖像蒙版：circle/rounded（闭集，默认 circle） |

## 纪律

- members 必须为 2–4 项；单人改用 testimonial。
- 肖像默认真人摄影，默认中国人、中国场景（人物图片纪律）。
- bio 只许一句话，不许写简历段落。

## 模板对应

程序/页面生成.py `t_team_grid`；PPTX 声明式映射见 程序/pptx映射.py `映射表["team_grid"]`
