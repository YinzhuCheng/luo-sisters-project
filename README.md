# 洛青悠 × 洛有栖角色企划包

这是一个面向后续 Codex / 多 agent 协作维护的原创角色企划包。当前阶段重点是把两张整版人设图拆成稳定网页、结构化资产目录、参考截图工作流与可复用日志。

## 快速入口

1. 打开 `index.html` 查看项目总览。
2. 打开 `character_sheets/qingyou.html` 查看洛青悠 HTML 设定页。
3. 打开 `character_sheets/arisu.html` 查看洛有栖 HTML 设定页。
4. 打开 `knowledge/index.html` 查看旧归档拆分后的二级知识库。
5. 阅读 `AGENTS.md` 获取维护规则。
6. 阅读 `docs/content_map.md` 确认第一版长内容的位置与层级入口。
7. 阅读 `workflows/asset_generation_workflow.md` 获取截图到透明资产的流程。
8. 阅读 `workflows/agent_parallel_guide.md` 获取多 agent 并行规则。

## 生成网页

建议使用当前 Codex 工作区的 bundled Python：

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\build_project_html.py
```

普通 Python 环境可用时也可以运行：

```bash
python tools/build_project_html.py
```

生成结果：

- `index.html`
- `character_sheets/qingyou.html`
- `character_sheets/arisu.html`
- `knowledge/index.html`
- `knowledge/characters.html`
- `knowledge/story.html`
- `knowledge/visual.html`
- `knowledge/workflow.html`

## 结构化资产目录

每个角色严格独立：

```text
assets/characters/qingyou/
assets/characters/arisu/
```

每个角色内部保持同构目录：

```text
source_sheet/
crops/
generated/chroma/<asset_type>/
generated/transparent/<asset_type>/
generated/rejected/
prompts/
workflow/
```

当前资产类型：

- `standing`
- `expressions`
- `turnaround`
- `clothing`
- `accessories`
- `props`
- `details`
- `cg`

## 图像工作流

1. 从 `source_sheet/` 裁出参考截图：

```bash
python tools/crop_from_sheet.py --character all --force
```

2. 以 `crops/` 中的截图作为参考图重新生成无文字、无边框、纯 `#ff00ff` 背景图。
3. 如果截图歪、过紧或信息不足，直接回看 `source_sheet/` 中的完整设定图，把完整设定图作为第二参考；只有反复影响生产时才返工 `crop_manifest.csv`。
4. 把生成图放入 `generated/chroma/<asset_type>/`。
5. 批量抠图生成透明 PNG：

```bash
python tools/remove_chroma_batch.py --character qingyou --asset-type props
```

6. 验证目录、路径边界和透明图：

```bash
python tools/validate_assets.py
```

## 数据与语言

- `characters/qingyou.json` 与 `characters/arisu.json`：角色资产槽位、色卡、版式、路径。
- `locales/zh-CN.json`：中文网页文案，当前默认。
- `locales/en.json`：英文文案骨架，供后续语言切换使用。
- `project_data/knowledge_base.json`：第一版归档拆分后的知识库层级、页面、锚点、摘要与迁移状态。
- `assets/styles/luo_sisters.css`：首页与角色页共享样式。

## 内容层级与保全

- `index.html` 是当前轻量展示入口，不承载第一版的全部长文。
- `knowledge/index.html` 与 `knowledge/*.html` 是第一版长内容的结构化二级知识库入口。
- `docs/luo_sisters_project_guide_v2.html` 保留第一版完整内容，包括人设八层、故事推进、AIGC 节奏、提示词组、制作规范、资产清单和下一步。
- `docs/content_map.md` 记录当前网页、第一版归档、结构化数据、工作流和日志之间的层级关系。
- 已核对 `docs/luo_sisters_project_guide_v2.html` 与 `D:\original\luo_sisters_project_files\luo_sisters_project_files\docs\luo_sisters_project_guide_v2.html` 哈希一致，确认旧版长内容没有删除。

## 日志与项目记忆

所有 agent 工作时都应追加 CSV：

- `logs/progress_updates.csv`：进度更新。
- `logs/asset_registry.csv`：资产登记与状态。
- `logs/issue_memory.csv`：遇到的坑、原因、规避方式和可复用规则。

这些 CSV 是后续沉淀 skill 的材料，不要只把经验留在聊天记录里。

## 当前整版参考图

- `assets/images/luo_qingyou_character_sheet_v2.png`
- `assets/images/luo_arisu_character_sheet_v1.png`

两张图也复制到了各自角色目录的 `source_sheet/`，用于裁切参考，不覆盖原始历史资产。
