# 页型卡-compare_bars

对比条：两组数据多维度横向条形对比。

## 适用场景
- 对照意图：我方 vs 竞品、本期 vs 上期、A方案 vs B方案
- 1-6个维度，每个维度两条

## 数据字段
- 必填：brow/no/kick/title/rows/foot
- 选填：a_name/b_name（组名，默认A/B）、concl/bg
- rows每项必填：label（维度名）、a、b（数值）

## 纪律
- a组金色强调，b组灰色；a永远是"我方/本期/推荐项"
- 条形按全局最大值归一化，保证跨行可比
- rows超过6行拆页或换 table_compare
