# Executor portability

## 1. 初始化与日常执行分离

推荐职责链：

```text
Explicit project initialization / recalibration
  -> develop-software 组合工作流
  -> Repository instructions + project docs + mechanical checks
  -> Codex / Claude Code / other agents 按仓库规则处理日常任务
```

`develop-software` 只负责生成或重新校准项目工作流。普通 Feature、bug fix、refactor、test 和 review 不应再次进入本 Skill。

## 2. Global instructions

Global instructions 最多声明：

```markdown
- When explicitly asked to initialize or recalibrate a repository's software-development workflow, use `develop-software`.
- For ordinary repository work, follow the repository's own instructions and authoritative project files.
```

不要写“所有软件任务都使用 develop-software”。这会把一次性初始化器变成固定重型 SOP，并覆盖项目自己的裁剪结果。

## 3. Repository instructions

Repository instructions 是日常 Agent 的权威入口，必须自包含：

- build/test/lint/type/architecture 的真实命令；
- 项目地图、术语、模块边界与禁止依赖；
- 数据、安全、兼容、部署和副作用风险；
- 该项目实际启用的 Spec/ADR/Plan 触发条件与位置；
- Definition of Done、文档同步面和授权边界；
- architecture、roadmap 和 Artifact 索引。

不要只写“遵循 develop-software”。初始化结束后，项目规则应独立于 Skill 版本和安装位置。

## 4. 执行器 wrapper

若执行器默认读取 `CLAUDE.md` 而不是 `AGENTS.md`，使用极薄 wrapper：

```markdown
@AGENTS.md
```

若不支持 import，只复制一个指向权威文件的最小说明；不要维护第二份 SOP。模板见 [claude-wrapper-template.md](../assets/claude-wrapper-template.md)。

其他执行器也使用相同原则：配置入口可以不同，但项目规则、状态与证据只保留一份。

## 5. 机械强制层

Repository instructions 描述要遵守什么、去哪里找权威事实以及如何运行检查；CI、lint、tests、schema checks 和 validators 负责让确定性违规失败。

若初始化选择 Artifact validator：

1. 将脚本复制或改写到项目自己的 `tools/`、`scripts/` 或既有工具目录；
2. 在 repository instructions 中写入稳定命令；
3. 在共享 CI 中执行；
4. 不引用某台机器上的 Skill 安装路径。

Hooks 可用于快速反馈，但不能成为唯一共享 Gate。

## 6. 项目状态与聊天

Project Brief、System Design、roadmap、Spec、ADR、Plan、code、tests 和 generated references 保存项目事实。聊天只表达本次意图，不是长期 source of truth。

多 Agent 协作时，每个 Agent 从同一仓库事实开始，并把决定、进度和 evidence 写回选定载体。不要用“另一个 Agent 说完成了”替代 diff、测试或状态迁移。

## 7. 接入已有执行器

1. 找到当前每个执行器实际读取的指令文件；
2. 选择一个 repository instructions 作为权威；
3. 将项目专属规则、命令和路由合并到权威文件；
4. 将其他入口缩减为 import 或指针；
5. 删除要求日常任务反复调用 Skill 的全局/仓库规则；
6. 把确定性规则迁入共享 test/lint/CI；
7. 用一个 mechanical change 和一个真实 behavior change 验证上下文与路由。

## 8. 重新调用 Skill

只有新项目初始化、治理级别迁移、执行器拓扑变化或风险边界发生结构性变化时，才显式调用 `develop-software`。日常任务由 repository instructions 直接驱动。
