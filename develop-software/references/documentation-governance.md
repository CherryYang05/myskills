# Documentation governance

## 1. 按 decay rate 分层

| 文档类型 | 变化速度 | 内容 | 写语义 |
|---|---|---|---|
| Repository instructions | 慢 | 命令、项目不变量、风险规则 | 直接修正 + 定期 prune |
| System Design / operations | 慢 | 当前架构和运行事实 | 原地同步 current state + `last_verified` |
| Feature Spec | 阶段性 | 一个行为契约 | 状态机 + successor |
| ADR | 历史 | 高代价决定及理由 | proposed 可改；accepted 后 supersede |
| Active Plan / issue | 快 | 当前 slices、阻塞和 evidence | living state，随执行更新 |
| Generated reference | 与代码相同 | schema、CLI/API、配置 | 从代码生成，CI 检测 drift |
| Release notes | 历史 | 已发布用户可见变化 | 按 release policy append |
| Scratch / spike notes | 极快 | 临时探索 | 可重写；关闭时删除或压缩 |

把进度写入 AGENTS.md、把函数签名手抄到多份设计、把 future roadmap 写成 current capability，都会制造 drift。

## 2. 五种操作

- **Update**：当前事实变化时原地更新 System Design、runbook、用户文档或 AGENTS.md。
- **Append**：release history、audit log 等真正的时间序列追加新记录。
- **Supersede**：已接受 Spec/ADR 的语义被新 Artifact 替代，保留旧文件和双向链接。
- **Archive**：只有 active 目录被历史噪音淹没且链接可稳定迁移时才使用；不默认移动文件。
- **Compact**：关闭时删除临时笔记、合并重复说明、修复索引和失效状态，不抹除决策历史。

Git 已经保存文件历史。不要仅因为“完成了”就搬到 archive，也不要创建 `design-old.md`、`design-new.md`、`final-plan-v2.md`。

## 3. Documentation impact

每次关闭只同步受影响的事实：

- 用户行为变化：用户/CLI/API 文档；
- 架构边界变化：System Design + accepted ADR；
- schema/config/protocol 变化：migration、generated reference、兼容说明；
- 运维行为变化：deployment/runbook/observability；
- 已发布变化：按项目 policy 更新 release notes/CHANGELOG；
- 纯内部机械变化：可以明确 `No documentation impact`。

通用 SOP 不要求每个 Feature 固定更新三类站点，也不要求每个小修写 CHANGELOG。Repository overlay 可以增加项目特有要求。

## 4. Current、accepted、planned 必须分离

公开文档和架构文档应清楚标注：

- **Current**：代码和测试已证明的当前能力；
- **Accepted**：已批准但尚未完成的行为/决定；
- **Planned**：roadmap 候选，可能变化。

ADR accepted 不得被写成 Feature current。Feature implemented 不得被写成 released，除非发布事实存在。

## 5. 生成优先

容易随代码变化的事实尽量生成：

- CLI `--help`、OpenAPI、JSON schema、config reference；
- Feature/ADR 索引和 milestone 状态表；
- module dependency graph；
- docs internal links 与 frontmatter index。

生成流程应可重复，并在 CI 中重新生成后检查 diff。手写文档保留为什么、边界、失败语义、安全、迁移和用户流程。

## 6. Closure-time compaction

任务关闭时至少检查：

1. Plan/issue 是否真实反映剩余工作；
2. Spec、ADR、System Design 与代码是否存在冲突；
3. 是否出现新的重复 source of truth；
4. 临时文档、失效 TODO、debug 指令是否应删除；
5. AGENTS.md 是否混入进度或 Feature 细节；
6. 索引、链接、`superseded_by` 和 `last_verified` 是否正确；
7. 未完成项是否回到 roadmap/issue，而不是被状态变化掩盖。

Compaction 应缩短未来 Agent 建立上下文的路径，而不是把所有历史重写成一篇大文档。

## 7. 长期 drift 检查

在 milestone、release 或定期维护时，从代码反向检查：模块边界、公共 schema、可用命令和当前能力。只修复事实差异；不要借“文档同步”扩张产品范围。
