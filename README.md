# 洛青悠 × 洛有栖角色企划包

这是一个面向后续 Codex / 多 agent 协作维护的原创角色企划包。当前阶段重点是把两张整版人设图拆成稳定网页、结构化资产目录、参考截图工作流与可复用日志。

## 快速入口

1. 打开 `index.html` 查看项目总览。
2. 打开 `character_sheets/qingyou.html` 查看洛青悠 HTML 设定页。
3. 打开 `character_sheets/arisu.html` 查看洛有栖 HTML 设定页。
4. 阅读 `AGENTS.md` 获取维护规则。
5. 阅读 `workflows/asset_generation_workflow.md` 获取截图到透明资产的流程。
6. 阅读 `workflows/agent_parallel_guide.md` 获取多 agent 并行规则。

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
3. 把生成图放入 `generated/chroma/<asset_type>/`。
4. 批量抠图生成透明 PNG：

```bash
python tools/remove_chroma_batch.py --character qingyou --asset-type props
```

5. 验证目录、路径边界和透明图：

```bash
python tools/validate_assets.py
```

## 数据与语言

- `characters/qingyou.json` 与 `characters/arisu.json`：角色资产槽位、色卡、版式、路径。
- `locales/zh-CN.json`：中文网页文案，当前默认。
- `locales/en.json`：英文文案骨架，供后续语言切换使用。
- `assets/styles/luo_sisters.css`：首页与角色页共享样式。

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
