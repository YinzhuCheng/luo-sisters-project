# 洛青悠 × 洛有栖

Source HTML: `index.html`

## Content
Character Bible · HTML Sheet System | 0.5-doc-governance
# 洛青悠 × 洛有栖
先让网页成为稳定、美观的展示窗口，再把每一个服饰、配饰、表情和物件拆成可复用透明资产。
[image placeholder: alt="洛青悠" src="../assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png"]
洛青悠
[image placeholder: alt="洛有栖" src="../assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png"]
洛有栖
Stage 01
## 项目当前目标
本阶段把整版设定图拆成结构化网页与资产流水线：文字、边框、色卡和标签交给 HTML/CSS；角色、服饰、配饰和道具使用参考截图重新生成透明 PNG。
### 台前主题
姐妹筹备一场“兔子洞茶会”，通过服装、手账、摄影、旧图书室、邀请函和小物件展现少女日常。
### 人物主题
青悠用秩序保护梦想，有栖用探索寻找梦想。两人的相处从互补走向冲突，再走向共同创造。
### 深层主题
AIGC 在中后期逐渐浮现，放大“被替代”“完美梦境”“选择外包”等焦虑。最终工具回到工具位置，人物把方向、取舍和关系握回自己手中。
角色页
## 角色页
当前页面先用参考截图和占位槽稳定版式；透明 PNG 生成后会自动替换进入对应槽位。
[image placeholder: alt="洛青悠" src="../assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png"]
[image placeholder: alt="洛有栖" src="../assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png"]
工作流
## 网页与资产流水线
- 先完成首页与两张角色 HTML 设定页，让视觉风格稳定下来。
- 从现有整版设定图裁出参考截图，按角色和资产类型严格归档。
- 用参考截图重新生成无文字、无边框、纯色背景版本。
- 通过本地抠图得到透明 PNG，并写入资产登记 CSV。
- 透明资产替换网页占位槽，网页继续承担中文排版、边框和标签。
资料地图
## 资料层级地图
当前首页是轻量展示入口；长内容已经分布到结构化页面、角色数据、工作流和资产登记里。下面按层级进入不同资料。
### 0｜当前展示层
面向浏览和展示，优先呈现美观网页与角色设定页。
- [项目首页](index.md) 当前导航与展示窗口
- [洛青悠 HTML 设定页](character_sheets/qingyou.md) 古风手账式设定页
- [洛有栖 HTML 设定页](character_sheets/arisu.md) 蓝白 Alice 资料页
- [结构化知识库](knowledge/index.md) 结构化阅读与规划入口
- [资产索引页](knowledge/assets.md) 角色根目录、槽位、提示词与输出路径
### 1｜结构化知识库
按任务拆分的知识页与统一资产索引，供结构化阅读和生产定位使用。
- [知识库总目录](knowledge/index.md) 结构化项目页面入口
- [导航与阅读路径](knowledge/navigation.md) 说明该先读哪里、下一跳去哪里
- [统一资产索引](knowledge/assets.md) 所有角色、资产类型、提示词和计划输出
- [角色与人设层](knowledge/characters.md) 两姐妹八层人设与互动关系
- [故事梗概与主题层](knowledge/story.md) 章节推进、AIGC 节奏和场景钩子
- [视觉方向与提示词库](knowledge/visual.md) 美术方向、提示词组和双人 KV
- [制作规范与资产规划](knowledge/workflow.md) 流程、资产清单、检查表和下一步
### 2｜数据与语言层
当前网页由数据和模板生成，文案与前端分离。
- [中文文案数据](../locales/zh-CN.json) 当前网页默认语言
- [英文文案骨架](../locales/en.json) 后续语言切换准备
- [洛青悠角色配置](../characters/qingyou.json) 色卡、版式、资产槽位
- [洛有栖角色配置](../characters/arisu.json) 色卡、版式、资产槽位
- [知识库数据源](../project_data/knowledge_base.json) 结构化页面摘要与工作流文案
- [早期总览数据](../project_data/luo_sisters_overview.json) 保留第一阶段结构化内容
### 3｜生产与记忆层
给多 agent 并行、资产生成、坑点召回和后续 skill 沉淀使用。
- [资产生成工作流](../workflows/asset_generation_workflow.md) 包含截图偏移时回看完整设定图规则
- [并行 agent 指南](../workflows/agent_parallel_guide.md) 按角色与资产类型分工
- [内容保全地图](../docs/content_map.md) 说明哪些内容移动到了哪里
- [进度记录 CSV](../logs/progress_updates.csv) 每次工作追加记录
- [坑点记忆 CSV](../logs/issue_memory.csv) 问题、原因、规避规则
- [资产登记 CSV](../logs/asset_registry.csv) 资产状态与路径
故事
## 故事梗概
姐妹共同筹备一场“兔子洞茶会”。表层是少女日常与茶会企划，中层是生活的秩序与无序、计划与探索的冲突，深层是 AIGC 时代对价值、陪伴、顾问和生成内容的再思考。
1. 第一幕：把梦留一页有栖提出“只有迷路的人才能参加的茶会”，青悠把它写进手账。两人寻找场地、试穿服装、设计邀请函，AI 只是校园里自然存在的新工具。
1. 第二幕：梦被变快同学用 AI 快速生成海报和方案。青悠开始不舒服，有栖被完美 Alice 图景吸引。两人的可爱差异逐渐变成冲突。
1. 第三幕：把迷路也安排好青悠误用 AI 优化邀请函与流程，有栖的奇怪句子被抹平。茶会越来越完整，也越来越失去心跳。
1. 第四幕：重新选择门青悠承认自己害怕失去价值，有栖承认自己害怕打开门。两人重新合作：AI 负责重复劳动，人物负责方向、保留、删改和关系。
1. 终幕：不完美的茶会茶会如期发生，也发生意外。雨、迟到、失焦照片和手账里的空白让这一天成为真正属于她们的记忆。
HTML / CSS / asset workflow generated from structured data. Public pages are Chinese-first with an English mirror and locale separation.

## Page Links
- `html | ok | Chinese Qingyou character sheet` 洛青悠: [character_sheets/qingyou.md](character_sheets/qingyou.md)
- `html | ok | Chinese Arisu character sheet` 洛有栖: [character_sheets/arisu.md](character_sheets/arisu.md)
- `html | ok | Chinese structured knowledge index` 知识库: [knowledge/index.md](knowledge/index.md)
- `html | ok | Chinese asset index` 资产: [knowledge/assets.md](knowledge/assets.md)
- `html | ok | Chinese Qingyou character sheet` 古风 Lolita｜规划者｜记录者｜温柔姐姐 洛青悠Luo Qingyou 用秩序保护梦想的人。她把梦写进手账，给冒险准备茶、伞与回程路。 青绿色古风 Lolita手账与复古相机云肩、盘扣、蕾丝、青瓷色旧街、茶会、窗影、梅枝 打开设定页: [character_sheets/qingyou.md](character_sheets/qingyou.md)
- `html | ok | Chinese Arisu character sheet` JK Lolita｜Alice 母题｜探索者｜梦境入口 洛有栖Luo Arisu 用无序寻找梦想的人。她在校园日常里看见门、钥匙、白兔和未命名的可能性。 蓝白 JK Lolita钥匙项链、白兔挂件、怀表雏菊、旧书、书包、茶杯校园走廊、旧图书室、秘密门 打开设定页: [character_sheets/arisu.md](character_sheets/arisu.md)
- `html | ok | Chinese public showcase` 项目首页: [index.md](index.md)
- `html | ok | Chinese Qingyou character sheet` 洛青悠 HTML 设定页: [character_sheets/qingyou.md](character_sheets/qingyou.md)
- `html | ok | Chinese Arisu character sheet` 洛有栖 HTML 设定页: [character_sheets/arisu.md](character_sheets/arisu.md)
- `html | ok | Chinese structured knowledge index` 结构化知识库: [knowledge/index.md](knowledge/index.md)
- `html | ok | Chinese asset index` 资产索引页: [knowledge/assets.md](knowledge/assets.md)
- `html | ok | Chinese structured knowledge index` 知识库总目录: [knowledge/index.md](knowledge/index.md)
- `html | ok | Chinese structured navigation page` 导航与阅读路径: [knowledge/navigation.md](knowledge/navigation.md)
- `html | ok | Chinese asset index` 统一资产索引: [knowledge/assets.md](knowledge/assets.md)
- `html | ok | Chinese character knowledge page` 角色与人设层: [knowledge/characters.md](knowledge/characters.md)
- `html | ok | Chinese story knowledge page` 故事梗概与主题层: [knowledge/story.md](knowledge/story.md)
- `html | ok | Chinese visual knowledge page` 视觉方向与提示词库: [knowledge/visual.md](knowledge/visual.md)
- `html | ok | Chinese workflow knowledge page` 制作规范与资产规划: [knowledge/workflow.md](knowledge/workflow.md)
- `json | ok` 中文文案数据: [../locales/zh-CN.json](../locales/zh-CN.json)
- `json | ok` 英文文案骨架: [../locales/en.json](../locales/en.json)
- `json | ok` 洛青悠角色配置: [../characters/qingyou.json](../characters/qingyou.json)
- `json | ok` 洛有栖角色配置: [../characters/arisu.json](../characters/arisu.json)
- `json | ok` 知识库数据源: [../project_data/knowledge_base.json](../project_data/knowledge_base.json)
- `json | ok` 早期总览数据: [../project_data/luo_sisters_overview.json](../project_data/luo_sisters_overview.json)
- `markdown | ok | asset production workflow` 资产生成工作流: [../workflows/asset_generation_workflow.md](../workflows/asset_generation_workflow.md)
- `markdown | ok | parallel-agent ownership guide` 并行 agent 指南: [../workflows/agent_parallel_guide.md](../workflows/agent_parallel_guide.md)
- `markdown | ok | content hierarchy map` 内容保全地图: [../docs/content_map.md](../docs/content_map.md)
- `csv | ok` 进度记录 CSV: [../logs/progress_updates.csv](../logs/progress_updates.csv)
- `csv | ok` 坑点记忆 CSV: [../logs/issue_memory.csv](../logs/issue_memory.csv)
- `csv | ok` 资产登记 CSV: [../logs/asset_registry.csv](../logs/asset_registry.csv)

## Page Anchors
- `viewport`
- `overview`
- `characters`
- `workflow`
- `content-map`
- `story`

## Resource References
- `asset | ok` ../assets/characters/qingyou/source_sheet/luo_qingyou_character_sheet_v2.png alt="洛青悠"
- `asset | ok` ../assets/characters/arisu/source_sheet/luo_arisu_character_sheet_v1.png alt="洛有栖"
