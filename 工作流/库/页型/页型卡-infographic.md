# 页型卡-infographic

信息图：图标+数字+说明，2-4项横向高光展示。

## 适用场景
- 亮点页：2-4个关键数字，每个配图标和一句话说明
- 比 kpi_hero 更"图"，图标是视觉锚点

## 数据字段
- 必填：brow/no/kick/title/items/foot
- 选填：concl/bg/mask
- items每项必填：icon（图标库中文名，`程序/图标.py --列表`）、v（数字）、label
- items每项选填：d（说明）

## 纪律
- items 2-4项，超出拆页
- icon 必须用库内图标，不许 emoji
- 数字用 tabular-nums，label 不超过6字
