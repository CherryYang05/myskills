# Conventions — 目录布局 / 拆分启发式 / 反漂移原则

> 本文件供 skill-dev-flow 按需加载。SKILL.md 是流程编排,本文件是细则。

## 目录布局

```
项目根/
├── AGENTS.md                # 慢变。命令/约定/不变量/目录地图。小而稳,≤~150 行。
├── CHANGELOG.md             # 历史。append-only,新条目置顶或置底但绝不改旧条目。
├── .agent-scratch           # 显式临时区。Agent 随便写,定期清空。
└── docs/
    ├── requirements/        # 结构化需求。point-in-time,带 Status 头。
    │   └── <req-slug>.md
    ├── designs/             # 每个够格的功能一篇设计文档。point-in-time,带 Status 头。
    │   └── <feature-slug>.md
    ├── decisions/           # ADR。append-only,supersede 不 edit。
    │   └── NNNN-<title>.md
    └── tasks/               # 任务清单。ephemeral,随便勾改删。
        └── <feature-slug>.md
```

每个目录对应一种 decay rate,这是整套布局的核心:**不同变化速率的内容物理隔离,各用各的写操作语义。**

| 目录 | decay rate | 写操作语义 |
|---|---|---|
| AGENTS.md | 慢变 | 谨慎编辑 + 定期 prune |
| docs/requirements、docs/designs | 阶段性(快照) | 写一次,靠 Status 标生命周期,不回头改正文 |
| docs/decisions(ADR) | 历史 | append + supersede,绝不 edit |
| CHANGELOG | 历史 | append-only |
| docs/tasks、scratch | ephemeral | 随意重写 |

---

## 拆分启发式（P2 用）

### 三层拆分
1. **模块(module)** — 按职责和边界切;系统级项目按子系统切(如存储引擎 / 网络 / 共识)。
2. **功能(feature)** — 模块下的具体能力,是设计与实现的基本单位。
3. **任务(task)** — 功能下可执行、可验证的步骤。

### 设计文档门槛
功能**需要**单独写 design doc,当且仅当满足任一:
- 有非显然的设计取舍(多种数据结构 / 接口 / 算法可选)
- 有多个值得记录的备选方案
- 跨模块影响,或改动公共接口 / 契约
- 涉及并发、内存序、正确性 / 一致性风险

都不满足 → 不写设计文档,直接进 tasks。

> 反例(不该写设计文档):给已有结构体加一个字段、修一个空指针、改一处日志格式、CRUD 包装。
> 正例(该写):新的并发数据结构、改动 RPC 契约、引入新的状态机、有多种实现路径的算法。

### 任务颗粒度
- 每条 task 能独立完成且可验证(有明确的"做完了"判据)。
- 太粗(如"实现整个功能")→ 拆开。
- 太细(如"加一个分号")→ 合并进相邻 task。

---

## 反漂移原则（贯穿全流程,P5 集中体现）

文档臃肿/漂移的根因:**把不同 decay rate 的内容塞进同一文件,再用原地增删去维护它。** 四条原则对症:

1. **按 decay rate 物理拆分** — 一个文件只承担一种生命周期(见目录布局)。

2. **历史和决策 append + supersede,不 edit** — ADR 一旦写下不可变;要改写新条目标 supersedes。CHANGELOG 同理。永不臃肿,因为从不重写旧的。

3. **状态尽量派生,不维护第二份真相** — "哪些做完了"的权威来源是 tasks / issue / PR / 测试 / 代码本身,不要手工同步进多个 markdown。维护两份真相 = 必然 drift。

4. **设计/需求文档是快照,靠 Status 标生命周期** — 不持续原地改写正文。Draft 阶段可改;一旦 Implemented 就冻结,后续变化写新文档并 supersede。

### P5 收尾时的 compaction checklist
- `docs/designs/` design doc Status → Implemented(被替代的 → Obsolete + Supersedes)
- CHANGELOG append 一行(做了什么 + 关联 design/req),不改旧条目
- 引入新稳定约定/命令/目录 → 精简更新 AGENTS.md(表格、要点前置),同时删过时内容,检查软上限
- 已完成 `docs/tasks/` 删/归档,清空 .agent-scratch

### AGENTS.md 卫生红线
绝不写进 AGENTS.md:进度(done/doing/todo)、changelog、某个功能的设计细节、临时笔记。
这些各有归处(docs/tasks / CHANGELOG / docs/designs / scratch)。混进来就是臃肿的起点。
