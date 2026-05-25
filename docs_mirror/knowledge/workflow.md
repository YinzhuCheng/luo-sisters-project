# 制作规范与资产规划 | 洛氏姐妹知识库

Source HTML: `knowledge/workflow.html`

## Content
Knowledge 05
# 制作规范与资产规划
日本二次元角色企划制作流程、资产清单、统一检查表和下一步建议。
Production Workflow
## 日本二次元角色企划制作规范
按“概念 -> 线稿 -> 立绘 -> 设定图 -> CG -> 应用素材”的顺序推进。
| 阶段 | 产出 | 检查重点 |
| --- | --- | --- |
| 0. 角色圣经 | 姓名、核心句、主题功能、关系、禁改识别点。 | 一句话能讲清她是谁，三处记忆点稳定。 |
| 1. Moodboard | 服装、发型、配色、材质、道具、场景参考。 | 青悠偏青绿古风与茶；有栖偏蓝白校园与 Alice。 |
| 2. 剪影草案 | 每人 3-6 个小剪影。 | 遮住细节后仍能区分两人。 |
| 3. 线稿探索 | 发型、裙摆、领口、袖口、鞋袜、包袋结构。 | 服装层次清楚，配饰位置稳定。 |
| 4. 彩色小稿 | 3 组配色与明暗测试。 | 主色、辅助色、点缀色用途明确。 |
| 5. 标准立绘 | 全身立绘，正面站姿，透明或浅色背景。 | 可作为后续所有图的母版。 |
| 6. 三视图 | 正面、侧面、背面，含关键结构说明。 | 裙摆、发饰、包带、鞋袜、背面蝴蝶结完整。 |
| 7. 表情差分 | 每人 8-12 个表情。 | 眉、眼、口、头部角度、手势同时拉开。 |
| 8. 姿势设定 | 站姿、坐姿、拍照、写手账、看门、递邀请函。 | 动作服务角色。 |
| 9. 服装变体 | 标准服、日常服、茶会服、雨天服、冬季服、轻便校园服。 | 换装后保留核心识别点。 |
| 10. 配饰物件 | 相机、手账、钥匙、怀表包、邀请函、茶杯、书包。 | 道具能独立讲故事。 |
| 11. 代表 CG | 每人 2 张个人 CG，加 1-2 张双人 KV。 | CG 表现角色主题、关系与成长瞬间。 |
| 12. 应用素材 | 头像、Q版、表情包、社媒横幅、Live2D 拆件草案。 | 用于宣传与后续迭代。 |
Asset List
## 统一资产范围
这些项目已经并入角色配置、资产索引页和 asset_registry.csv，不再只是概述文字。
### 洛青悠资产清单
标准立绘、三视图、表情、拍照/翻手账/递茶/准备雨伞/整理领结姿势、旧相机、青绿色手账、茶杯、干花书签、备用发夹、旧街茶馆光影、雨天计划空白。
### 洛有栖资产清单
标准立绘、三视图、好奇/惊讶/梦游/害羞/委屈/勇敢表情、看门/捏钥匙/写邀请函/晃挂件/踏入门槛姿势、钥匙项链、怀表包、白兔挂件、旧书、音乐盒、蓝色墨水、走廊的门、茶凉之前抵达。
Unified Checklist
## 统一检查表
后续生成、归档和网页引用时反复检查这些规则。
- 青悠换装时保留：青绿色、手账或相机、古风结构线索。
- 有栖换装时保留：蓝白、钥匙或兔子、校园与 Alice 线索。
- 每张图都能回答一个问题：这张图让角色更清楚了吗？
- 每件道具都有叙事功能：能推动关系、表现性格或承载主题。
- CG 优先选择“发生了什么”的瞬间，而非单纯站桩展示。
- 截图歪、过紧或信息不足时，生成阶段可回看完整 source_sheet；只有反复失败才返工 crop_manifest。
Next Step
## 下一步建议
从标准化资料开始，再进入图像生成和人工修正。
### 1. 固定角色卡
确认年龄、身高、生日、学校/社团、家庭关系、说话方式和常用道具。
### 2. 做第一版三视图
优先生成线稿或低色彩草图，先看剪影与结构，再逐步增加材质细节。
### 3. 确定第一张双人 CG
建议从“门与手账”开始：有栖发现门，青悠记录并准备退路。
Related Files
## 相关生产文件
知识库负责说明结构，实际生产仍以工作流、脚本和 CSV 为准。
- [统一资产索引](assets.md) 角色根目录、截图、提示词与计划输出总入口
- [资产生成工作流](../../workflows/asset_generation_workflow.md) 截图到透明资产的完整流程
- [并行 agent 指南](../../workflows/agent_parallel_guide.md) 角色和资产类型严格分工
- [资产登记 CSV](../../logs/asset_registry.csv) 记录资产来源、提示词、输出和状态
- [坑点记忆 CSV](../../logs/issue_memory.csv) 沉淀可召回规避规则

## Page Links
- `html | ok | Chinese asset index` 统一资产索引: [assets.md](assets.md)
- `markdown | ok | asset production workflow` 资产生成工作流: [../../workflows/asset_generation_workflow.md](../../workflows/asset_generation_workflow.md)
- `markdown | ok | parallel-agent ownership guide` 并行 agent 指南: [../../workflows/agent_parallel_guide.md](../../workflows/agent_parallel_guide.md)
- `csv | ok` 资产登记 CSV: [../../logs/asset_registry.csv](../../logs/asset_registry.csv)
- `csv | ok` 坑点记忆 CSV: [../../logs/issue_memory.csv](../../logs/issue_memory.csv)

## Page Anchors
- `viewport`
- `production-flow`
- `asset-list`
- `checklist`
- `next`
- `related-workflows`

## Resource References
(none)
