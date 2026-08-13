# SDD design basis

三档模板吸收主流 SDD 的稳定部分，但不绑定外部 CLI：

- [GitHub Spec Kit](https://github.com/github/spec-kit)：采用项目治理原则、`Specify -> Plan -> Tasks -> Implement`、可独立验收的 user story 和跨 Artifact 一致性检查；不复制其完整脚本和重型 feature 目录。
- [OpenSpec](https://github.com/Fission-AI/OpenSpec)：采用 `why -> what -> how -> steps` 的职责分离、current truth 与 proposed change 不混写、完成后同步事实；不要求安装 OpenSpec。
- [Kiro Specs](https://kiro.dev/docs/specs/feature-specs/)：采用 requirements、design、tasks 的渐进细化和可测试 EARS 风格；Medium 将三者合并进一个 Feature 文件，Complex 再拆开。
- [MADR](https://github.com/adr/madr)：ADR 只记录架构意义显著的决定，并保留 context、options、decision outcome、consequences 和 confirmation；不把 ADR 当开发日记。
- [BearAgent](https://github.com/CherryYang05/BearAgent)：Complex 采用稳定 `F-NNNN`、Spec/ADR/Plan 状态分离、Vertical Slice、Roadmap、current Architecture、Source of Truth 和 DoD；移除 Agent Runtime 专属术语和固定技术栈。

共同原则：

1. 先确认可观察行为，再决定实现。
2. 项目事实必须进入版本库，聊天不是 Source of Truth。
3. What、Why、How、Progress 和 Current state 不放在同一个权威字段中。
4. 验收标准必须可判断，证据必须来自实际运行的检查。
5. 文档成本随维护、协作和失败风险增加，不随代码行数机械增加。
6. 能由 test、lint、schema check 或 CI 判断的规则，不只写成自然语言。
7. 允许在实现中回到早期 Artifact 修正认识，但语义变化必须重新确认。
