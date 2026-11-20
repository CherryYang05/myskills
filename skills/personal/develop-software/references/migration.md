# Existing repository migration

## 1. 原则

- 迁移职责，不迁移外观。已有 RFC、decision log、issue 和目录能承担目标职责时继续使用。
- 先确定 Source of Truth，再补模板。不要让新旧两套文档同时权威。
- 只迁移当前和近期真实工作。不要批量伪造历史 Spec、ADR 或 Plan。
- 不改变稳定 ID、外部链接和已接受决定，除非用户明确批准迁移方案。
- 先更新根 `AGENTS.md`，让后续任务立即获得一致路由。

## 2. 审计映射

| 目标职责 | 常见既有载体 |
|---|---|
| Project Brief | README、PRD、charter、product brief |
| Current Architecture | architecture overview、C4、design doc |
| Feature behavior | RFC、issue、requirements、OpenSpec specs |
| Architecture decision | ADR、decision log、accepted RFC |
| Implementation state | issue checklist、execution plan、tasks.md |
| Roadmap | milestone、project board、release plan |
| Agent rules | AGENTS.md、CLAUDE.md、contributor guide |

一个载体可以映射一个职责，但不要让同一字段同时表达 current behavior、future intent 和 implementation progress。

## 3. Simple → Medium

1. 从 `docs/project.md` 提取稳定产品边界到 Project Brief。
2. 将当前架构草图扩展为 current Architecture。
3. 为正在实施的非平凡行为分配首个 `F-NNNN`，把需求、设计和切片迁入 Feature Spec。
4. 仅当已有长期决定需要保留理由时创建 ADR。
5. 更新 `AGENTS.md`，停止在 living spec 中保存 Feature 进度。

## 4. Medium → Complex

1. 保留 `F-NNNN` 和 ADR ID。
2. 从 Medium Feature Spec 中拆出行为契约和 delivery slices；前者留在 Spec，后者进入 `PLAN-F-NNNN`。
3. 将多个 milestone 和 Feature 依赖移到 Roadmap。
4. 将已经实施的架构事实同步到 Architecture；历史理由保留在 ADR。
5. 创建索引并运行 validator，修复关系后再启用 CI Gate。

## 5. 降档

不要删除或合并已经接受的历史 Artifact。选择目标档的新写入规则，保留旧索引为历史入口，并明确哪些文件不再创建。Git 历史不能替代仍被外部链接引用的已接受决定。

## 6. 执行器入口

以 `AGENTS.md` 为项目权威指令。其他执行器只能维护薄 wrapper 或指针；不要复制第二份 SOP。确定性规则进入项目自己的 tests、lint、CI 或 scripts，不引用 Skill 安装路径。
