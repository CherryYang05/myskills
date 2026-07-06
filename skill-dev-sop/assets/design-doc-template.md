<!--
  功能设计文档模板 — P4 功能设计阶段产出
  用法：复制到 docs/designs/<feature-slug>.md，删掉本注释，填充。
  仅对【够格】的功能写（有设计取舍/多备选方案/跨模块影响/并发或正确性风险）。
  trivial 功能不写，直接进任务清单。
  原则：point-in-time 快照，靠 Status 头表达生命周期，完成后改 Status 而非回头改正文。
-->

# <功能名称>

Author: <你> | Last-updated: <YYYY-MM-DD> | Status: Draft
<!-- Status: Draft | Implemented | Obsolete。Implemented 后不再改正文。 -->
<!-- Supersedes: <被本设计替代的旧设计，可选> -->
<!-- 关联需求：docs/requirements/<req>.md -->
<!-- 关联系统设计：docs/architecture/system-design.md -->

## Context & Scope

<!-- 这个功能在解决什么、属于哪个模块、和谁交互。读者不靠对话也能看懂。 -->

## Goals / Non-Goals

**Goals**
-

**Non-Goals**
<!-- 给实现设护栏，挡住自由发挥。 -->
-

## Design

### Interfaces / APIs
<!-- 对外接口、函数签名、协议。契约层面先定清楚。 -->

### Data & State
<!-- 数据结构、状态、生命周期、所有权（谁分配谁释放）。 -->

### Concurrency / Memory Ordering
<!-- 系统级功能必填：线程模型、共享状态、锁/原子、内存序假设。 -->
<!-- 无并发则写"单线程，无共享状态"一句话即可，不要留空。 -->

### Failure Modes
<!-- 会怎么失败、如何检测、如何恢复/回滚。错误码、超时、重入、资源耗尽。 -->
<!-- 这一节是 P6 单元测试"边界/失败路径"用例的直接依据。 -->

## 耦合评估

<!-- 新增小节：耦合问题几乎都在设计阶段悄悄引入，这里是前置闸门，必须回答。 -->
- 本功能新增/修改了哪些对外接口？
- 依赖了哪些模块？是否引入了系统设计里依赖方向规则之外的新依赖？
- 会不会导致循环依赖？如果会，怎么解决（拆接口 / 引入事件回调 / 提取共享模块）？
- 本功能的代码将放在哪个目录？是否符合项目的文件分类规范（feature-based / layer-based）？

## Alternatives Considered

<!-- 必填，不能敷衍。每个备选：做法 + 为什么没选（空间/时间权衡、复杂度、与现有架构冲突）。 -->
<!-- 这一节防止重复推翻已否决的方案。 -->
- **方案 A：** ... — 没选原因：...
- **方案 B（选中）：** ... — 选中原因：...

## Cross-cutting

<!-- 兼容性、可观测性（日志/指标）、测试策略（对应 P6 单元/集成测试计划）、回滚方案、对其他模块的影响。 -->

## Open Questions

<!-- known unknowns，显式留白。 -->
-

<!--
  实现的"待办清单"不写在这里——放 docs/tasks/<feature>.md。
  有长期架构影响的决策另起一条 ADR 进 docs/decisions/。
-->
