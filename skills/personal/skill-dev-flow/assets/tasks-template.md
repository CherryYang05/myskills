<!--
  任务清单模板 — P3/P4 使用
  用法:复制到 docs/tasks/<feature-slug>.md,删掉本注释。
  这是 ephemeral 区:放心勾选、增删、重写,不用心疼。完成后可删或归档。
  作用是把"进度"从 design doc 和 AGENTS.md 里隔离出来,避免污染慢变文档。
-->

# Tasks — <功能名称>

关联设计:docs/designs/<feature-slug>.md

## 待办

<!-- 颗粒度:每条是一个可独立完成、可验证的步骤。太粗拆开,太细合并。 -->
- [ ] 
- [ ] 
- [ ] 

## 测试

- [ ] 单元测试覆盖 <核心路径>
- [ ] 边界/失败路径测试(对应 design 的 Failure Modes)
- [ ] 

## 收尾(P5,完成后逐项做)

- [ ] design doc Status → Implemented
- [ ] CHANGELOG.md append 一行(做了什么 + 关联 design/req)
- [ ] 若引入新稳定约定/命令/目录,精简更新 AGENTS.md
- [ ] 清理本 tasks 文件 / 清空 .agent-scratch
