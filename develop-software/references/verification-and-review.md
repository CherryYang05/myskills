# Verification and review

## 1. Evidence model

Acceptance Criteria 与 evidence 是多对多关系：

| Evidence | 适合证明 |
|---|---|
| Unit test | 局部规则、边界条件、纯状态转换 |
| Contract test | adapter、provider、协议或公共接口的一致性 |
| Integration test | 数据库、文件、网络或多个真实组件的协作 |
| End-to-end / smoke | 从真实入口观察用户场景 |
| Recovery / fault injection | crash window、retry、幂等、恢复和 partial failure |
| Security test | 权限绕过、不可信输入、路径/命令注入、secret exposure |
| Static / architecture check | 类型、依赖方向、禁止模式、schema 形态 |
| Benchmark / profile | latency、throughput、memory、resource budget |
| Manual / visual | 暂时难自动化的 UX、视觉或硬件行为 |
| Operational evidence | staged rollout、metric、log、audit 或 restore drill |

不要强迫 `AC-1 = test_1`。建立 `AC → Evidence` 表，允许一个场景覆盖多条 AC，也允许一条 AC 需要多个证据层。

## 2. Test-first 的适用边界

默认先建立会失败的自动化测试或 characterization，再实现最小改动。以下情况可以先调查：

- 旧系统行为尚不明确，需要 characterization；
- API/算法可行性未知，需要限时 spike；
- 视觉、硬件、生成物或第三方环境难以先写稳定测试；
- 纯机械变换已经由编译器、formatter 或等价检查完整覆盖。

例外不取消验证责任。关闭前仍要补齐回归证据，或明确 manual evidence、未自动化原因和剩余风险。

## 3. 风险驱动验证

| 变化 | 最低附加检查 |
|---|---|
| bug fix | 失败前能复现、修复后通过的 regression evidence |
| public contract | contract + backward compatibility |
| persistence/migration | 空库/旧版本升级、失败回滚、数据保留 |
| retry/external write | 重复请求、timeout、partial success、idempotency |
| concurrency | race/order/atomicity/failure interleaving |
| security/trust | negative tests、权限边界、secret redaction、resource limits |
| performance claim | 固定环境与基线、可重复 benchmark、退化阈值 |
| UI/visual | interaction/E2E、截图或明确人工验收步骤 |

项目风险规则可以提高门槛，不能用本表降低已有要求。

## 4. 验证顺序

1. Targeted test：当前 slice/bug 的最小证据；
2. Static checks：format、lint、type、compile；
3. Boundary checks：contract、architecture、schema/migration；
4. Integration/E2E：受影响关键路径；
5. Full suite / clean environment：按项目 Gate 和风险决定；
6. Artifact/doc checks：链接、生成物、状态关系和 docs impact。

记录实际命令、退出状态和可观察结果。不要只写“CI 应该会过”。测试失败时保留最相关输出，先判断是产品缺陷、测试缺陷还是环境限制。

## 5. Review 清单

Review 要以找问题为目标，不继续扩展功能：

- **Scope**：是否满足 Goals，是否越过 Non-goals，是否混入无关重构；
- **Correctness**：状态、不变量、边界和错误路径是否完整；
- **Architecture**：依赖方向、职责、公共类型和 adapter 边界是否符合设计；
- **Failure**：timeout、retry、cancel、recovery、partial success 是否与 Spec 一致；
- **Security/privacy**：不可信输入、权限、secrets、资源上限和日志；
- **Data/compatibility**：migration、旧数据、协议/配置兼容和 rollback；
- **Tests**：是否验证真实边界，是否只验证 mock，是否遗漏负路径；
- **Observability**：失败能否定位，metric/log 是否泄漏或制造高基数；
- **Docs**：是否把 future 写成 current，是否复制了易漂移实现细节。

高风险或大 diff 推荐独立 review pass；可使用另一个 Agent，但不是强制。无论由谁 review，结论必须回到 diff、tests 或 Artifact，而不是只留在聊天。

## 6. Definition of Done

Feature 只有在以下条件都满足时才能 `implemented`：

- 所有必须 AC 有足够 evidence；
- 从真实入口可以观察核心场景；
- 相关 unit/contract/integration/recovery/security/benchmark 已按风险运行；
- architecture guard、lint/type/build 和项目 CI Gate 通过；
- Spec/ADR/System Design/generated reference 与实现没有已知矛盾；
- docs、migration、rollout/rollback 和 release impact 已处理或明确 N/A；
- active Plan 的 slice 与剩余工作真实；
- 没有 secrets、临时调试、未授权依赖或无消费者抽象；
- 实际验证命令、observable result、known limitations 已报告。

如果关键测试因环境无法运行，不要标记为通过。根据风险保持 Feature 为 `accepted`、Plan 为 `active`，或经项目所有者明确接受限制后记录人工证据和风险。
