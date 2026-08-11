# Architecture and coupling

## 1. System Design 的职责

System Design 描述当前系统，而不是保存每个历史版本。应回答：

- 顶层组件、职责和 owned data；
- 对外接口与隐藏实现；
- dependency direction 和禁止边；
- 关键跨组件流程；
- deployment/runtime 边界；
- 影响系统形态的质量属性与资源约束；
- 哪些不变量由什么机械检查保护。

重大变化先用 ADR 保存理由和取舍，再把 accepted 结果同步到 current-state System Design。使用 `last_verified` 暴露长期未核对的文档。

## 2. Coupling governance 链路

```text
System Design
  -> dependency direction
  -> architecture invariant
  -> machine-enforceable guard
  -> Feature coupling assessment
  -> implementation check
  -> review
```

每个 Feature 至少回答：新增/修改哪些接口，依赖哪些模块，是否改变允许边，是否产生循环依赖，代码归属是否符合模块职责。

不要用延迟 import、service locator、全局单例或复制类型掩盖循环依赖。常见修复顺序：缩小接口、反转依赖、提取稳定契约、引入事件边界、重新划分职责。

## 3. 何时写 ADR

满足任一条件时通常需要 ADR：

- 改变稳定模块边界或 dependency direction；
- 改变 public contract、持久化 schema 策略或兼容策略；
- 改变 security/trust boundary、权限模型或外部副作用语义；
- 引入新的 production dependency、runtime、storage 或 deployment topology；
- 方案难以回滚、跨多个 Feature，且未来维护者需要知道为什么。

普通内部重构、沿用已有模式、局部实现选择通常不需要 ADR。把这些说明留在 Spec/Plan/diff。

## 4. Cross-cutting concern 筛选

每项不是都要长篇填写，但必须判断并在不适用时写 `N/A + 简短理由`：

| Concern | 关键问题 |
|---|---|
| Failure semantics | 失败如何暴露？partial success 如何处理？ |
| Retry / timeout / cancellation | 谁控制 deadline？哪些操作可安全重试？ |
| Recovery | 崩溃或重启后从哪里恢复？是否会重复副作用？ |
| Security / trust | 哪些输入不可信？谁能授权？边界在哪里？ |
| Privacy / secrets | 哪些数据不得持久化、输出或记录？ |
| Observability | 哪些日志、metric、trace、audit 能解释行为？ |
| Resource limits | 时间、内存、并发、输出、配额上限是什么？ |
| Persistence / migration | schema 如何演进、验证和回退？ |
| Backward compatibility | 多版本如何共存？调用方如何迁移？ |
| Rollout / rollback | 如何逐步启用、停用和恢复旧版本？ |
| Concurrency / consistency | 共享状态、原子边界、顺序和一致性模型是什么？ |

## 5. 机械化层级

优先把确定性规则交给工具：

| 规则 | 适合的强制层 |
|---|---|
| 格式、类型、静态错误 | formatter、linter、type checker |
| dependency direction / cycle | architecture test、dependency lint |
| schema / protocol 兼容 | snapshot、compatibility、migration test |
| secrets / known vulnerable dependency | secret scan、dependency scan |
| 生成文档漂移 | generator + `diff --exit-code` |
| 链接、Front Matter、Artifact 状态 | docs lint、Artifact validator |
| 风险语义和设计取舍 | 人/Agent review + failure tests |

工具示例仅用于选择，不是技术栈要求：Python `import-linter`，TypeScript `dependency-cruiser`，Java `ArchUnit`，Go `depguard`，C/C++ `clang-tidy` 或 include-layer checks，Rust workspace metadata/custom checks。

Hooks 提供快速反馈，CI 是共享权威 Gate。不要把必须执行的规则只写在 prompt 或 AGENTS.md 中。

## 6. 新项目最小架构基线

新项目先建立最少可工作的控制面：

1. 可复现 build/test 命令；
2. formatter/lint/type check 中适合该栈的部分；
3. 模块边界和一条可运行的 architecture guard；
4. CI 执行相同权威命令；
5. Repository `AGENTS.md` 只记录项目命令、风险和不变量；
6. 第一条端到端 smoke path。

不要在第一天预建所有未来目录、抽象和部署系统。让真实 Feature 验证边界。
