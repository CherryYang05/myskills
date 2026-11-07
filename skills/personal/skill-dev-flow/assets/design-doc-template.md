<!--
  设计文档模板 — P3 功能设计产出
  用法:复制到 docs/designs/<feature-slug>.md,删掉本注释,填充。
  仅对【够格】的功能写(有设计取舍/多备选方案/跨模块影响/并发或正确性风险)。
  trivial 功能不写,直接进 tasks。
  原则:point-in-time 快照,靠 Status 头表达生命周期,功能完成后改 Status 而非回头改正文。
-->

# <功能名称>

Author: <你> | Last-updated: <YYYY-MM-DD> | Status: Draft
<!-- Status:Draft | Implemented | Obsolete。Implemented 后不再改正文。 -->
<!-- Supersedes: <被本设计替代的旧设计,可选> -->
<!-- 关联需求:docs/requirements/<req>.md -->

## Context & Scope

<!-- 这个功能在解决什么、属于哪个模块、和谁交互。读者不靠对话也能看懂。 -->

## Goals / Non-Goals

**Goals**
- 

**Non-Goals**
<!-- 给实现设护栏,挡住 Agent 自由发挥。 -->
- 

## Design

### Interfaces / APIs
<!-- 对外接口、函数签名、协议。契约层面先定清楚。 -->

### Data & State
<!-- 数据结构、状态、生命周期、所有权(谁分配谁释放)。 -->

### Concurrency / Memory Ordering
<!-- 系统级功能必填:线程模型、共享状态、锁/原子、内存序(acquire/release)假设。 -->
<!-- 无并发则写"单线程,无共享状态"一句话即可,不要留空。 -->

### Failure Modes
<!-- 会怎么失败、如何检测、如何恢复/回滚。错误码、超时、重入、资源耗尽。 -->

## Alternatives Considered

<!-- 必填,不能敷衍。每个备选:做法 + 为什么没选(空间/时间权衡、复杂度、与现有架构冲突)。 -->
<!-- 这一节防止 Agent 和后人重复推翻已否决的方案。 -->
- **方案 A:** ... — 没选原因:...
- **方案 B(选中):** ... — 选中原因:...

## Cross-cutting

<!-- 兼容性、可观测性(日志/指标)、测试策略、回滚方案、对其他模块的影响。 -->

## Open Questions

<!-- known unknowns,显式留白。 -->
- 

<!--
  实现的"待办清单"不写在这里——放 docs/tasks/<feature>.md。
  有长期架构影响的决策另起一条 ADR 进 docs/decisions/。
-->
