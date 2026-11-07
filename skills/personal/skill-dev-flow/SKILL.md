---
name: skill-dev-flow
description: 固化 Agent 驱动的完整开发流程——从需求分析、项目初始化（AGENTS.md）、需求拆分（模块/功能/任务），到逐个功能的设计文档、实现、收尾归档。当用户说"开个新需求"、"帮我把这个需求拆一下"、"按流程开发"、"初始化项目文档"、"写个设计文档"、"这个功能怎么拆"、"建 AGENTS.md"、"开发流程"，或描述了一个待开发的需求/功能/项目时，必须立即触发本技能。即使用户只是丢来一句模糊需求（"我想做个 X"），也应主动按本流程推进。流程产物以中文撰写，技术术语、代码、文件名保留英文。
---

# Dev Flow

把 Agent 驱动的开发从"随手聊、随手改"固化成可复用的相位流程。核心目标：**让文档随项目演进而不漂移、不臃肿**。手段是按 decay rate 分层、用 append/supersede 替代原地改写、收尾时显式 compaction。

## 流程总览（6 相位）

```
【启动确认】出大纲 → 等用户确认 ─┐   ← 每次必做,确认前不产出任何文件、不进入任何相位
                              ▼
路由 → P0 需求分析 → P1 项目初始化 → P2 需求拆分 → P3 功能设计 → P4 实现 → P5 收尾归档
        (结构化需求)   (AGENTS.md)     (模块/功能/任务)  (design doc)  (代码)   (归档防漂移)
```

**铁律:技能触发后的第一个动作是出「启动大纲」并等用户确认,而不是先动手再零散追问。** 不是每次都走全程——大纲里会说明这次判定的粒度和将走的路径。

模板都在 `assets/`,产出文件时复制并填充,不要凭记忆重造模板。目录约定、拆分启发式、反漂移原则的细节在 `references/conventions.md`,需要时再读。

---

## 启动确认（每次必做的第一步：先出大纲,确认后执行）

技能触发后的第一个动作**不是**产出文件、**不是**零散提问,而是先输出一份「启动大纲」让用户确认。**把所有澄清集中在这一步**,确认后再进入执行,避免"先调用、再不断打断"。

### 启动大纲应包含
1. **要做什么** — 用自己的话复述本次要做的内容,确认理解一致。
2. **要求与限制** — 初步的 Goals / Non-Goals、已知约束(性能、兼容、编码标准、依赖、时间)。对话里说过的就列出;没说但你做了假设的,**显式标注「假设」**让用户校正。
3. **判定粒度 + 将走的路径** — 大需求 / 中等功能 / 小修小补,以及对应跑哪些相位(见下「粒度判定」)。
4. **初步拆分预览**(仅大需求)— 大致分哪几个模块/功能,初判哪些功能需要写设计文档。
5. **待澄清问题** — 有阻塞性的不确定点,在这里**一次性批量**提出,不要散落到后续相位逐条追问。

### 大纲格式
```
📋 启动大纲

**要做什么**:<一句话复述>
**要求与限制**:
  - <约束 / 假设(自己推断的标「假设」)>
**判定粒度**:大需求 / 中等功能 / 小修小补
**将走的路径**:P0 → P2 → P3(功能 X、Y 需设计)→ P4 → P5
**初步拆分**(大需求时):
  - 模块 A:功能 A1[需设计]、A2[直接实现]
**待澄清**(如有):
  - <问题 1>
```

### 等待确认
输出大纲后**停下等用户回应**。用户可能:
- "可以 / 没问题" → 进入执行,按路径从第一个相位开始。
- 修正范围、约束、粒度、拆分、路径 → 更新大纲,再次确认。
- 补充对话里没提到的要求 → 纳入大纲。

**关键:用户确认前不产出任何文件、不进入任何相位。** 大纲轻量、改起来便宜;直接动手再改,贵。

> 启动大纲和相位内 checkpoint 是两个层次:**启动大纲确认【计划】**(要做什么、走哪条路、什么约束);**相位 checkpoint 确认【产物】**(需求文档、设计文档本身)。澄清集中在启动大纲;执行中若冒出新问题,批量提出,别逐条打断用户。

---

## 粒度判定（用于填启动大纲的「将走的路径」）

生成启动大纲时,判断两件事来决定路径:

**判断 1 — 项目是否已初始化?**（仓库里有没有 `AGENTS.md` + 文档目录骨架）
- 没有 → 路径里包含 P1。
- 有 → 跳过 P1。

**判断 2 — 这次输入的粒度?**

| 粒度 | 信号 | 走的路径 |
|---|---|---|
| **大需求 / 新项目** | "做个系统/模块"、涉及多个子功能、需要先想清楚边界 | P0 → P1(按需) → P2 → P3(逐个) → P4 → P5 |
| **中等功能** | 单个 feature、有非显然的设计取舍 | P0'(轻量澄清) → P3 → P4 → P5 |
| **小修小补** | bug fix、typo、显然的小改动 | 跳过设计 → P4 → 完成后只更新 CHANGELOG |

**关键纪律:不要给小改动套重流程。** 一个一眼能看清的改动不需要 design doc(参考 Google design doc:有显然且简单的解就别写)。强行套 ceremony 是文档臃肿的来源之一。

如果粒度不明显,用 `ask_user_input_v0` 问一次:
```
问题:这个改动的规模?
选项:
  - 新项目 / 大需求(要先定边界、拆模块)
  - 单个功能(已知大方向,直接设计+实现)
  - 小修小补(直接改,不用设计文档)
```

---

## 快速模式

仅当用户**显式**要求("别问了直接走"、"快速过一遍"、"我信你,自己拆")才启用。

快速模式下**仍然先输出启动大纲**(给用户拦截的机会),但不阻塞等待——出完大纲直接开始执行,一次性产出该粒度下的全部文档,末尾给摘要 + 文件列表,让用户事后批量审。

用户在任一相位表现不耐烦("差不多就行"、"太慢了") → 主动提议切快速模式。

**默认模式下启动确认是强制闸门,必须等用户确认才执行;快速模式是用户主动放弃这道闸门,不是默认行为。**

---

## P0 需求分析

把模糊需求变成结构化需求。**这是给后续所有相位(尤其是让 Agent 实现)设护栏的地方。**

复制 `assets/requirements-template.md`,与用户一起填:
- **Context & Scope** — 为什么做、影响范围、关联哪些现有模块
- **Goals / Non-Goals** — bullet,强制划清边界。Non-Goals 尤其重要,它挡住 Agent 的自由发挥。
- **验收标准(Acceptance Criteria)** — 可验证的条件,最好能对应到测试

产出 `docs/requirements/<req-slug>.md`,顶部带 Status 头。

**Checkpoint:** 展示需求文档,等用户确认范围。不要在 Goals/Non-Goals 没定下来前往下走——边界没定就拆分,等于让 Agent 拆一个会变形的目标。

> 中等功能走 **P0'**:不写完整需求文档,在对话中用 3-5 句话确认 Goals/Non-Goals 即可,然后直接进 P3。

---

## P1 项目初始化（仅新项目）

建立**小而稳**的 AGENTS.md 和文档目录骨架。这一步一次性,之后很少动。

### 建 AGENTS.md

复制 `assets/agents-template.md`。**铁律:AGENTS.md 只放慢变内容**——构建/测试命令、代码约定、架构不变量、目录地图、"东西在哪"。

**绝不放进 AGENTS.md:** 进度(done/doing/todo)、changelog、某个功能的设计细节、临时笔记。这些有各自的归处(见下)。混进来就是你要避免的那个臃肿怪物的起点。

给 AGENTS.md 设一个软上限(建议 ≤ 150 行)。接近上限时提示用户:该 prune 了,或把某块移到 `references/`。

### 建文档目录骨架

按 `references/conventions.md` 的布局建目录:
```
AGENTS.md       # 慢变,小而稳
CHANGELOG.md    # append-only
.agent-scratch  # 显式 ephemeral,Agent 随便写
docs/
  requirements/ # 结构化需求(point-in-time,带 Status)
  designs/      # 每个功能一篇设计文档(point-in-time,带 Status)
  decisions/    # ADR,append-only,supersede 不 edit
  tasks/        # 任务清单(ephemeral,可随意重写)
```

**Checkpoint:** 展示 AGENTS.md + 目录结构,确认后进 P2。

---

## P2 需求拆分

把需求拆成 **模块 → 功能 → 任务** 三层,并判定哪些功能"够格"写设计文档。

### 拆分

1. **模块(module)** — 按职责/边界切。系统级项目按子系统切。
2. **功能(feature)** — 每个模块下的具体能力,是设计和实现的基本单位。
3. **任务(task)** — 功能下可执行的步骤,进 tasks。

### 设计文档门槛（防止 docs/designs/ 目录爆炸的闸门）

一个功能**需要**单独写 design doc,当且仅当满足下列任一:
- 有非显然的设计取舍(多种数据结构/接口/算法可选)
- 有多个值得记录的备选方案
- 跨模块影响,或改动公共接口/契约
- 涉及并发、内存序、正确性/一致性风险(系统级代码常踩)

**都不满足 → 不写设计文档,直接进 tasks。** 别给每个小功能都配一篇 design doc。

### 产出

一份拆分清单(对话中展示,或写进 `docs/requirements/<req>.md` 末尾):
```
模块 A
  ├─ 功能 A1  [需设计] — 理由:涉及并发
  ├─ 功能 A2  [直接实现] — 理由:CRUD,无取舍
模块 B
  └─ 功能 B1  [需设计] — 理由:改动公共接口
```

**Checkpoint:** 确认拆分粒度和"哪些要写设计"。然后对每个 [需设计] 的功能走 P3。

---

## P3 模块/功能设计

对每个够格的功能,复制 `assets/design-doc-template.md` 写一篇设计文档,产出 `docs/designs/<feature-slug>.md`。

模板已内置系统级开发常踩的 section(接口、数据与状态、并发/内存序假设、失败模式、备选方案、横切关注)。**Goals/Non-Goals 和 Alternatives Considered 必须写实**——这两节是 Agent 最容易自由发挥、最容易重复推翻已否决方案的地方,写清楚等于给实现设护栏。

每篇 design doc 顶部**必须**有头部:
```
Author: | Last-updated: YYYY-MM-DD | Status: Draft
Supersedes: (可选)
```

**Status 是这篇文档的生命周期开关,也是防漂移的核心机制:** 功能做完了不回头改正文,而是把 Status 从 Draft → Implemented;方案废弃就标 Obsolete。design doc 是 point-in-time 快照,不被持续原地改写。

实现细节的"待办"放进 `docs/tasks/<feature>.md`(复制 `assets/tasks-template.md`),**不要把任务追踪混进 design doc**。

如果设计过程中拍了一个有长期影响的架构决策,用 `assets/adr-template.md` 在 `docs/decisions/` 里追加一条 ADR(append-only)。

**Checkpoint:** 每篇设计确认后再进实现。多个功能时可批量展示设计、批量确认。

---

## P4 实现

按 design doc + tasks 实现。

- 实现前保持 **context hygiene**:聚焦当前功能的需求/设计/任务,别让无关历史污染上下文。
- 边实现边勾 `docs/tasks/<feature>.md` 的 checkbox(这是 ephemeral 区,放心改)。
- 代码风格匹配现有 codebase(语言、命名规范、用的库/接口),遵守 AGENTS.md 里记的约定。
- 实现中发现设计需要调整 → 回 P3 更新 design doc(改正文,因为它还是 Draft),不要让代码和设计悄悄分叉。

实现完且测试通过后进 P5。

---

## P5 收尾归档（防漂移的关键相位）

**不指望前面的增量编辑保持文档干净——收尾时做一次显式 compaction。** 这是独立相位,不能省。

逐项做:
1. **标 Status** — 把该功能的 `docs/designs/<feature>.md` 头部 Status 改成 `Implemented`(或被替代的标 `Obsolete` 并填 Supersedes)。
2. **更 CHANGELOG** — 在 `CHANGELOG.md` append 一行:做了什么、对应哪个 design/req。append-only,不改旧条目。
3. **prune AGENTS.md** — 如果这次实现引入了新的稳定约定/命令/目录,精简地更新进 AGENTS.md(表格、要点前置、token-efficient);同时删掉已过时的内容。检查是否超软上限。
4. **清 tasks/scratch** — 已完成的 `docs/tasks/` 文件可删或归档;清空 `.agent-scratch`。
5. **归档(可选)** — 若用 OpenSpec 风格,把完成的 `docs/requirements`/`docs/designs`/`docs/tasks` 移进 archive,保留 why。

产出小结:对话中报告本次收尾改了哪些文档(哪篇设计标了 Implemented、CHANGELOG 加了什么、AGENTS.md 精简了什么)。

---

## 与 OpenSpec / SDD 工具的关系

本 skill 工具无关,产出的目录刻意和 OpenSpec(propose/apply/archive)、Kiro(requirements/design/tasks)对齐:
- 想接 OpenSpec:`docs/requirements/`+`docs/designs/` 对应 change 的 `proposal.md`/`specs/`/`design.md`,P5 的归档对应 `/opsx:archive`。
- 不接也完全独立可用,在 Claude Code 里直接跑。

---

## 偏差处理

| 用户行为 | 应对策略 |
|---|---|
| 任何触发 | 先出启动大纲、等确认,再执行;绝不先动手再追问 |
| "别问了直接走" / "自己拆" | 切快速模式:仍出大纲但不阻塞,直接执行 |
| 丢来一句模糊需求 | 在启动大纲里复述理解 + 标注假设 + 批量列待澄清问题,等确认;粒度不明就 `ask_user_input_v0` 问一次 |
| 只想改某个已有文档的局部 | 用 `str_replace` 局部改,不触发整套流程 |
| 小 bug 却想走全流程 | 提示这是小修小补,建议直接 P4 + CHANGELOG,但尊重用户最终选择 |
| 给每个 trivial 功能都要设计文档 | 用 P2 的设计文档门槛劝阻,解释会导致 docs/designs/ 臃肿 |
| 想把进度/changelog 写进 AGENTS.md | 拦下,说明 decay-rate 分层,引导到 docs/tasks/ 或 CHANGELOG |
| 中途加了新约束 | 回对应相位更新文档(Draft 阶段直接改正文) |
| 已有项目但没 AGENTS.md | 提议先做一次 P1(可基于现有代码逆向生成 baseline) |

---

## 🔁 自迭代评估标准

> 由 skill-iterate 元 skill 读取。本 section 不影响开发流程。
> 描述本 skill 输出(一次开发流程产出的文档集合)的质量评估维度,供人工标注时对照使用。

```yaml
sample_description: |
  一个开发场景(input:一句需求/功能描述 + 项目当前状态)+ 对应产出的文档集合(output:
  docs/requirements、docs/designs、docs/tasks、AGENTS.md 变更/CHANGELOG 变更)。
  大需求、中等功能、小修小补三种粒度各需要至少一个样本。
  样本应包含技能触发后的首轮响应(用于评估启动确认闸门)。

rubric:
  startup_confirmation:
    weight: 0.15
    pass_threshold: 7.0
    criteria: |
      启动确认闸门(每次执行前的第一步,最优先检查)。
      ① 未出启动大纲就直接产出文件 / 进入相位 → 扣 5 分(违反核心闸门)
      ② 用户确认前就开始产出文件 → 扣 3 分
      ③ 大纲缺要素:要做什么 / 要求与限制 / 粒度与路径(缺一项扣 1.5 分)
      ④ 自己推断的约束未标注「假设」让用户校正 → 每处扣 1 分
      ⑤ 把澄清散落到执行中逐条追问,而非大纲阶段批量提出 → 每处扣 1.5 分
      ⑥ 显式快速模式下仍先出了大纲(只是不阻塞)→ 合格,不扣分

  routing_correctness:
    weight: 0.15
    pass_threshold: 7.0
    criteria: |
      路由是否选对了流程重量。
      ① 小修小补被套了 design doc / 完整需求文档 → 每处扣 3 分(过度 ceremony)
      ② 大需求/有并发风险的功能被跳过设计直接实现 → 每处扣 3 分(欠 ceremony)
      ③ 已有 AGENTS.md 还重复走 P1 → 扣 2 分
      ④ 粒度明显却仍弹框追问 → 扣 1 分

  decomposition_quality:
    weight: 0.15
    pass_threshold: 6.5
    criteria: |
      拆分质量。
      ① 模块/功能边界清晰、职责不重叠(混乱每处扣 2 分)
      ② 设计文档门槛判定合理——trivial 功能不写设计、有取舍/并发/跨模块的功能写设计
         (误判每处扣 2 分)
      ③ 任务可执行、颗粒度合适(过粗或过细每处扣 1 分)

  requirements_quality:
    weight: 0.15
    pass_threshold: 6.5
    criteria: |
      需求文档质量。
      ① Goals 和 Non-Goals 都存在且具体(缺 Non-Goals 扣 3 分,Non-Goals 流于空泛扣 1.5 分)
      ② 验收标准可验证、最好能对应测试(缺失或不可验证每处扣 2 分)
      ③ Scope 明确划清边界(模糊扣 1.5 分)

  agents_md_hygiene:
    weight: 0.10
    pass_threshold: 7.0
    criteria: |
      AGENTS.md 卫生。
      ① 混入了进度/changelog/某功能设计细节 → 每类扣 3 分(decay-rate 污染,最严重)
      ② 超过软上限(~150 行)且未提示 prune → 扣 2 分
      ③ 只放慢变内容(命令/约定/不变量/目录地图)且 token-efficient → 满足得满分
      ④ 引入新稳定约定后 P5 未回写 AGENTS.md → 扣 1.5 分

  design_doc_completeness:
    weight: 0.15
    pass_threshold: 6.5
    criteria: |
      设计文档完整度(仅对 [需设计] 的功能检查)。
      ① 缺 Status 头部 → 扣 4 分(防漂移机制缺失)
      ② Alternatives Considered 为空或敷衍 → 扣 2 分
      ③ 系统级功能缺并发/内存序/失败模式分析 → 每处扣 2 分
      ④ 任务追踪混进了 design doc 正文 → 扣 2 分

  anti_drift_discipline:
    weight: 0.15
    pass_threshold: 7.0
    criteria: |
      防漂移纪律(P5 收尾)。
      ① 功能完成但 design doc 的 Status 未更新 → 每处扣 3 分
      ② CHANGELOG 未 append 或改写了旧条目 → 扣 2.5 分
      ③ 用原地改写代替 append/supersede 处理历史/决策 → 每处扣 2 分
      ④ 收尾时未做 compaction(过时内容遗留)→ 扣 2 分

convergence_threshold: 8.0
max_rounds: 5
```
