# ppt studio · PPT 工作室

> AI 生成教学 PPT 的完整工作区：知识卡驱动 + 数据化页面 + 程序复用。
> 本仓库是「SODIUM · 活性之源」高中化学课件《钠及其化合物》的生产全程。

## 三层结构
```
库/       主题唯一真源 theme-sodium.css（配色/页眉/结构件）
程序/     截图.py（批量 HTML→PNG）｜页面生成.py（数据→HTML，5 种页型模板）
          gemini生图.py（Playwright 驱动 Gemini 网页，canvas 通道取原图）｜千问生图.py（dashscope API）
项目/化学-钠及其化合物/
          页/pages.json ← 做新页只改这个数据文件
          页/*.png      成品页（1920×1080）
          素材/*.png    Gemini 生成配图
```

## 用法
```
python 程序/页面生成.py                        # pages.json → 全部 HTML
python 程序/截图.py "项目/化学-钠及其化合物/页"  # 批量 HTML → PNG
```

## 设计体系
「SODIUM · 活性之源」：矿物暖白 #F5F3ED / 金属炭黑 #252C2B / 焰色金黄 #E9AE38（核心强调）
/ 金属银灰 #C5C9C6 / 过氧化物淡金 #D8B85B / 矿物墨绿 #526D61。
知识页纪律：色块标签 + 金边结论条 + 编号圆 + 因果箭头 + 发丝线（每个点缀件须答得出"去掉损失什么"）。
