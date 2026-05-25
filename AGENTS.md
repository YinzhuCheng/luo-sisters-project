# AGENTS.md｜洛青悠 × 洛有栖角色企划导航

本文件给 Codex / 自动化代理提供项目入口、维护原则与创作边界。请优先阅读本文件，再查看 `README.md`、`index.html`、`character_sheets/`、`workflows/` 与 `logs/`。

## 项目目标

构建一组可持续扩展的日本二次元原创角色企划：

- 姐姐：洛青悠，古风 Lolita，规划者、记录者、温柔姐姐。
- 妹妹：洛有栖，JK Lolita，Alice 母题，探索者、梦境入口。
- 表层故事：姐妹共同筹备“兔子洞茶会”。
- 核心主题：生活的秩序与无序、焦虑的对抗、AIGC 时代的迷茫与意义寻找。

## 文件导航

- `index.html`：项目中文导航页，面向人类阅读。
- `character_sheets/qingyou.html`：洛青悠 HTML 设定页，古风手账式风格。
- `character_sheets/arisu.html`：洛有栖 HTML 设定页，蓝白 Alice 资料页风格。
- `characters/qingyou.json`、`characters/arisu.json`：角色资产槽位、色卡、版式与路径配置。
- `locales/zh-CN.json`、`locales/en.json`：网页文案数据。中文为默认，英文用于后续语言切换。
- `assets/styles/luo_sisters.css`：首页与角色页共享样式。
- `assets/characters/qingyou/`、`assets/characters/arisu/`：严格分离的角色资产根目录。
- `docs/content_map.md`：内容层级与保全地图，说明第一版长内容移动到了哪里。
- `workflows/asset_generation_workflow.md`：从设定图截图到透明 PNG 的流程。
- `workflows/agent_parallel_guide.md`：多 agent 并行工作规则。
- `logs/progress_updates.csv`：工作更新记录。
- `logs/asset_registry.csv`：资产登记。
- `logs/issue_memory.csv`：坑点、原因与规避方式。
- `docs/luo_sisters_project_guide_v2.html`：上一版中文 HTML 归档。
- `project_data/luo_sisters_overview.json`：HTML 的主要内容数据源。
- `tools/build_project_html.py`：读取 `characters/` 与 `locales/` 并生成首页和两张角色页。
- `tools/crop_from_sheet.py`：从整版设定图裁切参考截图。
- `tools/remove_chroma_batch.py`：批量把纯色背景生成图转为透明 PNG。
- `tools/validate_assets.py`：检查角色目录、资产路径边界和透明图质量。
- `assets/images/luo_qingyou_character_sheet_v2.png`：洛青悠当前设定图。
- `assets/images/luo_arisu_character_sheet_v1.png`：洛有栖当前设定图。
- `prompts/character_sheet_prompt_notes.md`：后续图像提示词与日系设定图制作规范。

## 运行方式

在项目根目录执行：

```bash
python tools/build_project_html.py
```

生成结果会写入根目录 `index.html` 与 `character_sheets/`。

如果 `python` 在 Windows 上指向 Microsoft Store shim，使用当前 Codex 工作区 bundled Python：

```powershell
& 'C:\Users\cyz19\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' tools\build_project_html.py
```

裁切参考截图：

```bash
python tools/crop_from_sheet.py --character all --force
```

校验目录与资产：

```bash
python tools/validate_assets.py
```

## 写作与 UI 规则

- 所有面向用户的页面、注释标题、角色设定说明优先使用中文。
- 仓库内部工作流文档和提示词允许英文；最终网页中文优先，并保持文案数据与前端模板分离，方便后续加英文或其他语言。
- 文风保持人类可读、美观、清晰，避免堆砌术语。
- 减少密集否定表达，优先使用“建议、保持、优先、适合、可以”。
- HTML 保持自适应：`max-width: 100%`、`overflow-wrap: anywhere`、`auto-fit/minmax` 网格，避免文字和图片溢出卡片。
- 更新网页文案时优先修改 `locales/zh-CN.json`。
- 更新资产槽位、色卡、路径、版式时优先修改 `characters/*.json`。
- 更新完成后运行生成脚本，不手改生成后的 HTML 作为长期来源。
- 当前 `index.html` 是轻量展示入口；第一版完整长文保留在 `docs/luo_sisters_project_guide_v2.html`，不要误判为删除。
- 新增或移动内容时同步更新 `docs/content_map.md` 和首页资料层级地图。

## 人设核心

### 洛青悠

- 关键词：青绿色古风 Lolita、手账、相机、茶点、旧街、云肩、盘扣、青瓷色。
- 记忆句：那就给这场梦订个日期吧。
- 辅助口癖：茶和退路，我来准备。
- 成长方向：有弹性的秩序。她学会使用 LLM 与 AIGC 搬开重复劳动，把方向、判断和心意握在自己手里。

### 洛有栖

- 关键词：蓝白 JK Lolita、钥匙、白兔、怀表、旧图书室、秘密门、雏菊、Alice 母题。
- 记忆句：姐姐，你有没有觉得，这扇门今天不太一样？
- 辅助口癖：钥匙还在，所以门一定也在。
- 成长方向：有锚点的自由。她学会亲手打开门，把幻想带进会发生意外的现实。

## 故事处理原则

- AIGC 在前期作为生活背景出现，中后期成为人物焦虑的放大器。
- 故事台前优先呈现：姐妹互动、服装、茶会、校园、旧街、手账、摄影、误会与和解。
- AIGC 可以作为工具、陪伴、顾问、生成梦境存在。主角主线以“工具与方向”为主，配角可承载陪伴与顾问面向。
- 结尾方向：工具帮助搬开重复劳动，人物亲手选择山顶、保留意外、经历不完美生活。

## 图像资产与生成规范

- 当前生成图保存在 `assets/images/`，后续版本使用 `v1/v2/v3` 命名保留历史。
- 新的角色子资产必须进入 `assets/characters/<角色>/`，不要混放。
- 青悠与有栖资产文件夹严格隔离；多个 agent 并行时按角色与资产类型分工。
- 生图路线固定为：从整版设定图裁切参考截图 → 以截图为参考重新生成纯色背景图 → 本地抠图生成透明 PNG。
- 参考截图是工作手柄，不是唯一真相。若截图歪、过紧、缺上下文或导致生图失败，优先回看 `source_sheet/` 中的完整设定图，并把完整设定图作为第二参考。
- 只有当同一个截图反复阻碍生产时，才更新 `crop_manifest.csv`；临时修正图使用新版本号，不覆盖旧截图。
- 纯色背景默认使用 `#ff00ff`，并保留 `generated/chroma/` 中的中间图。
- 透明成品进入 `generated/transparent/<asset_type>/`，失败或不稳定版本进入 `generated/rejected/`。
- 图像生成阶段尽量减少密集文字，把清晰中文说明交给 HTML、SVG 或 PIL 后期排版。
- 表情差分必须拉开：眼睛、眉毛、嘴型、头部角度、手势、身体姿态。仅改变标签会导致差分辨识度不足。
- 日系设定制作建议覆盖：草图、线稿、色稿、三视图、表情、衣着差分、配饰、物件、姿势表、代表 CG。

## 工作记录规则

- 每次新增、修改、生成、拒绝资产，都追加 `logs/progress_updates.csv`。
- 每次资产状态变化，都追加或更新 `logs/asset_registry.csv`。
- 遇到可复用的问题、失败原因、规避方式，追加 `logs/issue_memory.csv`。
- 发现内容疑似缺失时，先查 `docs/content_map.md`、`docs/luo_sisters_project_guide_v2.html`、`project_data/luo_sisters_overview.json`；仍找不到再查 Git 或 `D:\original\luo_sisters_project_files\luo_sisters_project_files`。
- CSV 是未来沉淀 skill 的入口材料，不要只把经验留在聊天记录里。

## 推荐下一步任务

1. 先运行 `tools/crop_from_sheet.py` 产出第一批参考截图。
2. 让不同 agent 分别处理 `standing`、`expressions`、`turnaround`、`clothing`、`accessories`、`props`、`details`。
3. 生成透明 PNG 后运行 `tools/validate_assets.py` 并重建 HTML。
4. 根据 `logs/issue_memory.csv` 抽取稳定规则，后续沉淀为 skill。
