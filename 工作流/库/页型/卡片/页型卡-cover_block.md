# 页型卡-cover_block

- id: 页型卡-cover_block
- 卡型: 页型卡
- 标题: 封面（图片独立色块）
- 来源轨: 封面版式深调研 encoding（2026-10-06，16 版式分类）
- 生产者: chengge
- 状态: 草案
- 版式族: 封面

## 适用场景

现代商务、编辑风 deck；想用图片又不想被图片“吃掉”版面时。

## 数据字段表（字段/必填/说明）

| 字段 | 必填 | 说明 |
|---|---|---|
| id | 是 | 页 id（如 C3-大字报），HTML 文件名来源 |
| tpl | 是 | 固定值（闭集） |
| img | 是 | 封面主图（素材文件名） |
| eyebrow | 是 | 顶部英文眉题（全大写宽字距） |
| title | 是 | 中文大标题 |
| sub | 是 | 一句话副标题 |
| foot | 是 | 左下注脚 |
| en | 否 | 英文副题 |
| corner | 否 | 右下角标注（通用字段，各主题自定） |
| shape | 否 | 图片块形状：rect/arch/circle（闭集，默认 rect） |

## 纪律

- 图片块占画面 30–45%，shape∈rect/arch/circle，全套统一
- arch/circle 须与主题气质匹配；图与文字保持清晰间距或明确前后层级
- PPTX 近似：图片一律矩形块（arch/circle 仅 HTML）

## 模板对应

程序/页面生成.py `t_cover_block`

## PPTX 说明

声明式映射见 程序/pptx映射.py 映射表[cover_block]；字段引用须与规约一致（K6）。
