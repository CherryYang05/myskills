# Executor portability

## 1. 通用层与项目 overlay

推荐四层职责：

```text
Global agent instructions
  -> 声明软件任务使用 develop-software
Skill
  -> 定义通用生命周期、Artifact、验证和文档治理
Repository instructions
  -> 只定义项目命令、架构不变量、风险和额外 Gate
CI / lint / tests / hooks
  -> 机械强制确定性规则
```

不要把完整 SOP 复制到每个 repository。复制会使修订无法同步，并让 Agent 同时接收多个相互矛盾版本。

## 2. 最小 Global AGENTS.md

```markdown
# Global software engineering workflow

- For software projects and code changes, use the `develop-software` skill.
- Let the skill route architecture work, non-trivial features, and small changes differently.
- Treat repository files, code, tests, and generated references as authoritative project evidence; chat history is not a source of truth.
- Use repository instructions for project-specific commands, invariants, risks, and verification requirements.
- Prefer tests, lint, CI, and hooks for rules that can be checked mechanically.
- Do not claim completion without actual verification, observable results, remaining work, and known limitations.
```

## 3. Repository AGENTS.md

Repository 文件只保留：

- 最常用且可复制执行的 build/test/lint/architecture commands；
- 该项目特有的模块边界、依赖方向、术语和禁止模式；
- 数据、安全、部署、文档或发布的额外风险 Gate；
- 目录地图和 authoritative docs 指针；
- 与通用规则不同的明确 overlay。

不要放：当前 Feature 进度、通用 Phase 说明、完整 DoD 复本、聊天式背景或未来 roadmap。使用 [agents-template.md](../assets/agents-template.md)。

## 4. Claude Code wrapper

如果执行器默认读取 `CLAUDE.md` 而不是 `AGENTS.md`，使用极薄 wrapper：

```markdown
@AGENTS.md

Use the `develop-software` skill for software changes.
```

不要维护第二份项目规范。若执行器不支持 `@AGENTS.md` import，则只复制最小指针，并以 AGENTS.md 为权威。模板见 [claude-wrapper-template.md](../assets/claude-wrapper-template.md)。

## 5. Skill 可移植性

- 核心 Front Matter 只依赖 `name` 和 `description`。
- References、assets、scripts 使用相对路径。
- 核心流程不要求某个专有 tool、subagent API、Plan Mode、worktree 或浏览器。
- 执行器专属配置可以放在 `agents/` 或 wrapper 中，但不能改变 Artifact 语义。
- Artifact 存在于 repository，避免把 project state 锁在某个聊天产品中。

## 6. 多 Agent

多 Agent 是调度优化，不是流程阶段。只在边界明确、写集合不冲突、接口已接受且验证可独立运行时并行。

每个 Agent 必须从相同 repository truth 开始，并把结果落到代码、tests、Plan evidence 或 review comments。主 Agent 合并前重新验证共享边界。不要用“子 Agent 说完成了”替代 diff 和命令结果。

## 7. Mechanical enforcement

Repository instructions 应描述**要遵守什么**和**如何运行检查**；CI/test 配置负责让违规失败。Hooks 可以早反馈，但不能成为只在某个开发者机器上存在的唯一 Gate。

若某条规则无法机械化，明确 review owner、evidence 和失败处理，而不是伪装成 lintable requirement。

## 8. 接入已有执行器

1. 安装或暴露 `develop-software` Skill；
2. Global instructions 只加一条使用 Skill 的指针；
3. 清理 Repository instructions 中重复的通用 SOP；
4. 保留项目专属不变量和命令；
5. 将强制规则迁入 CI/lint/tests/hooks；
6. 用一个 Small fix 和一个真实 Feature 验证 routing，再扩大采用范围。
