# Workflow composition and task routing

## Contents

1. 组合原则
2. 项目画像
3. 模块选择
4. 校准示例
5. 固化日常任务路由
6. 既有项目迁移
7. 重新校准与反模式

## 1. 组合原则

`develop-software` 不把同一套 CodeSpec 式流程安装到所有仓库。先识别项目需要，再从 Artifact、验证、架构和文档治理模块中组合最小充分集合。

遵守三条约束：

1. **仓库自包含**：初始化结束后，普通开发依赖 repository instructions、代码、测试和项目文档，而不是依赖再次调用 Skill。
2. **风险局部升级**：某个高风险变化只升级相关决策、计划和验证，不自动把整个项目升级为最重流程。
3. **机械规则下沉**：能由工具确定的规则进入 test、lint、CI 或 validator；Agent 指令负责上下文与判断边界。

## 2. 项目画像

从仓库证据和用户目标判断：

| 维度 | 轻量信号 | 增强治理信号 |
|---|---|---|
| 生命周期 | spike、课程项目、短期脚本 | 长期产品、基础设施、公共开源项目 |
| 协作 | 单人、单 session | 多人、多 Agent、跨团队或跨 session |
| 行为契约 | 内部使用、可随时改 | public API、协议、文件格式、兼容承诺 |
| 状态 | 无持久化、易重建 | schema、migration、数据保留、恢复 |
| 副作用 | 本地且可回滚 | 外部写入、收费 API、部署、不可逆操作 |
| 架构 | 单模块、边界显然 | 多模块、依赖方向、部署/信任边界 |
| 交付 | 一次完成 | milestone、多个 outcome、rollout 窗口 |
| 审计 | 无正式审批 | 合规、决策 owner、证据留存 |

不要机械打分。画像只用于解释为什么选择或省略某个模块。

## 3. 模块选择

### 始终保留的项目基线

- 权威 repository instructions；
- 可复制运行的 build/test/static-check 命令；
- 项目地图、source of truth 和修改边界；
- 保存用户已有改动、只报告实际验证结果等基本执行规则；
- 与当前风险匹配的 Definition of Done。

### 条件模块

| 模块 | 启用信号 | 不启用时的替代 |
|---|---|---|
| Project Brief | 新的长期项目、大型 Epic、总体边界易漂移 | README 中的简短目标/非目标 |
| System Design | 多组件、状态所有权、依赖或部署边界 | AGENTS/README 中的短项目地图 |
| Roadmap | 多个 outcome、依赖或 milestone | issue list 或当前任务清单 |
| Feature Spec | 行为契约需稳定引用和跨 session 保持 | issue/PR 中写 AC |
| Stable Feature ID | Feature 多、会跨 milestone 或需长期链接 | issue number 或普通文件名 |
| ADR | 高代价、跨模块、难逆转的决定 | Spec/PR 中记录局部取舍 |
| Implementation Plan | 多个可验证切片、迁移、并行或长周期 | Spec/issue 中的短实现清单 |
| Artifact validator | 已采用严格命名、状态和关系 | docs lint 或人工 review |
| Architecture guard | 违规可机械判断且代价不低 | 明确 review Gate |
| Release/migration control | 多版本、数据或部署风险 | 普通测试与发布说明 |

模板是素材，不是表格税。选择模块后仍要删除与项目无关的字段。

## 4. 校准示例

以下只是校准点，不是固定 profile：

### 轻量

个人博客主题、小型脚本或短期原型通常只需要：

- 简洁 `AGENTS.md`；
- 真实 build/test/preview 命令；
- 目录地图和少量架构约束；
- issue 或对话级 AC；
- 最小 CI。

默认不创建 `F-NNNN`、ADR、Plan 目录。出现安全、发布或 migration 风险时只增加对应控制。

### 中等

长期维护的 Agent runtime、开发工具或开源基础设施通常需要：

- `AGENTS.md`、Project Brief、current System Design 和 Roadmap；
- 非平凡行为使用稳定 Feature Spec；
- 高代价决定使用 ADR；
- 只有多切片或高风险 Feature 才使用独立 Plan；
- build/test/lint/architecture checks 进入 CI；
- Artifact 数量增加后再启用 validator。

### 严格

多团队、强审计、关键数据或发布代价高的系统可以采用完整 CodeSpec 式治理：

- 全量稳定 ID、状态机、审批 owner 与关系校验；
- 每个非平凡 Feature 的 Spec 和证据映射；
- 架构/数据/安全决策 ADR；
- migration、rollout、recovery Plan；
- CI validator、兼容测试与独立 review Gate。

严格不是成熟度的同义词。超过风险和协作需要的流程会制造空文档、状态漂移和虚假 Gate。

## 5. 固化日常任务路由

把适合项目的路由写进 repository instructions，而不是要求每次调用 Skill。可从以下通用形态裁剪：

| 变化 | 默认处理 | 升级信号 |
|---|---|---|
| Mechanical | 不新建 Artifact；做最小改动和 targeted verification | 实际改变行为、契约或风险边界 |
| Behavior | 在项目选定的 Spec/issue 中明确 AC；按需制定切片 | 跨 session、多个调用方、失败语义复杂 |
| Architecture / high risk | 先处理边界和决定，再实现；增加风险测试与 rollback | security、data、external write、compatibility、concurrency |

即使项目未启用 Feature Spec，以下变化也不能按普通小修处理：

- 权限、secrets、不可信输入或 trust boundary；
- schema、migration、数据丢失或 recovery；
- 外部副作用、重试、幂等或不可逆操作；
- public API、protocol、file format 或 backward compatibility；
- concurrency、consistency、资源上限或 production dependency。

Repository instructions 应明确这些变化使用什么实际载体：Feature Spec、RFC、issue、ADR、Plan、测试或审批，而不是引用一个抽象 lane 名称后把判断留给聊天。

## 6. 既有项目迁移

按以下顺序最小迁移：

1. 识别已有权威文件和重复规则；
2. 保留现有 RFC、issue、ADR、目录和编号体系；
3. 先修正 repository instructions 和真实验证命令；
4. 只补当前已存在的架构、数据和发布风险；
5. 用一项真实工作验证路由是否够用；
6. 出现第二次真实需求后，再决定是否引入统一模板或 validator；
7. 删除被替代的重复 SOP，避免两个权威来源。

不要先批量生成历史 Spec，不要给远期 backlog 建空 Plan，也不要仅为了目录一致性迁移稳定链接。

## 7. 重新校准与反模式

需要重新校准的信号：

- 项目从原型转为长期维护或正式发布；
- 协作者、执行器、仓库或部署边界增加；
- 数据、安全、兼容、合规或恢复要求发生结构性变化；
- 文档和实现持续漂移，或现有流程明显妨碍交付；
- 多份 Agent/Contributor 指令互相冲突。

常见反模式：

- 在 Global instructions 中要求所有软件任务调用 `develop-software`；
- 用 Skill 本身保存项目状态；
- 新项目第一天就生成完整 Spec/ADR/Plan 树；
- 为了“流程完整”保留没有决策作用的 Gate；
- 把不能机械验证的口号伪装成 CI 规则；
- 只因 diff 小就忽略 migration、安全、协议或外部副作用。
