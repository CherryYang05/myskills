# Lifecycle and routing

## Contents

1. Discovery before process
2. Lane 判定
3. 风险覆盖规则
4. Phase 进入与退出
5. 何时需要用户 Gate
6. 既有项目接入
7. 常见误路由

## 1. Discovery before process

先建立 repository truth，再决定流程。最小 discovery 顺序：

1. 当前目录生效的 Agent/Contributor 指令；
2. `git status`、当前 diff、分支和用户已有改动；
3. Roadmap、System Design、相关 Spec/ADR/Plan；
4. 当前代码、测试、schema、CLI/API 生成物和 CI；
5. 必要时才读取历史提交、issue 或外部资料。

输出应区分：已验证事实、合理推断、待确认问题。聊天历史不能覆盖仓库事实。

## 2. Lane 判定

### Small / Mechanical

只有同时满足以下条件才使用轻量 lane：

- 目标与解法明确；
- 影响局部、容易回滚；
- 不改变稳定公共契约、架构边界或持久状态；
- 不引入高风险 cross-cutting concern；
- 可以用现有测试或一个小型回归证据验证。

典型例子：typo、格式、无行为变化的 rename、局部空指针修复、已有模式下的小配置修正。

### Feature

满足任一信号时创建或更新 Feature Spec：

- 新增或改变用户/调用方可观察行为；
- 存在非显然取舍或失败语义；
- 跨多个文件、组件或接口；
- 需要独立 Acceptance Criteria 才能判断完成；
- Small lane 在调查中暴露出更大范围。

### Architecture / New Project

满足任一信号时进入完整 lane：

- 从零建立项目或大型子系统；
- 改变模块职责、dependency direction、trust boundary 或 deployment topology；
- 引入高代价、跨模块、难逆转的技术决定；
- 需要重塑多个 Feature 的顺序或公共基线。

代码量不是可靠信号。一个五行 schema 变化可能是 Architecture risk；一个批量格式化可以仍是 Mechanical。

## 3. 风险覆盖规则

从以下维度选择最高风险 lane：

| 维度 | 低风险 | 升级信号 |
|---|---|---|
| 行为 | 内部等价变换 | 新用户场景、公共输出变化 |
| 数据 | 无持久化 | schema、migration、兼容或数据丢失 |
| 安全 | 无边界变化 | 权限、secrets、不可信输入、外部写入 |
| 执行 | 同步且局部 | retry、timeout、cancel、concurrency、recovery |
| 架构 | 遵循现有模式 | 新依赖方向、公共 abstraction、production dependency |
| 发布 | 易回滚 | 不可逆 rollout、多版本共存、协议兼容 |

若多个 lane 信号冲突，采用最高风险 lane；在证据显示风险更低后可以降级，并记录理由。

## 4. Phase 进入与退出

- **R0 Route & Discover**：得到当前行为证据、受影响范围、lane 和未知项。
- **P0 Frame**：得到可判断的 Goals、Non-goals、AC。新项目使用 Project Brief；Feature 使用 Spec；Small 可留在 issue/对话。
- **P1 Architect**：得到 current-state System Design、依赖方向和必要 ADR。普通 Feature 不重写全局架构。
- **P2 Bootstrap Controls**：得到可运行的 build/test/lint/CI/architecture checks。既有项目只补当前风险需要的缺口。
- **P3 Shape Work**：把大型范围切成稳定 Feature；确定依赖和交付顺序，不把 milestone 编进 ID。远期 backlog 只登记 ID/outcome/dependency，不预建空 Spec/Plan。
- **P4 Specify, Decide & Plan**：Spec accepted；相关 ADR accepted；必要 Plan active 前没有实现性开放问题。
- **P5 Execute Slices**：每次只推进一个可验证 slice；失败时保留可诊断证据。
- **P6 Verify & Review**：完成 AC evidence、风险测试、架构检查和范围 review。
- **P7 Close & Compact**：迁移状态，同步变化的事实，删除/合并临时状态，准确记录限制。

允许回退：实现中发现行为契约缺口时回 P4；发现系统边界错误时回 P1；发现工程基线不足时按需进入 P2。Phase 不是单向瀑布。

## 5. 何时需要用户 Gate

暂停并请求决定，仅限：

- 两种方案会产生显著不同的用户行为、长期成本或风险；
- Acceptance Criteria、Non-goals 或兼容边界不明确；
- 需要接受 Spec/ADR，但当前请求没有授权代表项目所有者作决定；
- 需要不可逆变更、外部副作用、新权限或额外资源；
- 证据与用户描述冲突且无法安全判断。

其余情况继续安全、可逆的工作，并在更新中显式写明假设。

## 6. 既有项目接入

不要先生成整套空文档。按实际任务渐进接入：

1. 保留现有 issue/RFC/ADR 体系，先映射而不是迁移；
2. 为当前非平凡 Feature 分配下一个稳定 `F-NNNN`；
3. 只补与当前风险相关的 System Design 段落和机械护栏；
4. 关闭任务时清理重复 source of truth；
5. 等出现第二次真实需求后，再决定是否需要统一目录和 validator。

## 7. 常见误路由

- “只改几行”不等于 Small；迁移、安全和协议变更必须升级。
- “新项目”不等于立即写十份文档；先 Project Brief、System Design 和第一批 Feature。
- “有 Spec”不等于必须有独立 Plan；单切片且低风险时可以省略。
- “没有自动化测试”不等于可以无证据关闭；可用 characterization、manual、benchmark 或 operational evidence，但要说明限制。
