# Impeccable 本地同步记录

上游来源：https://github.com/pbakaus/impeccable/tree/c3bb418ee38ee49a6b999b7752c1368f3123a2bd/.agents/skills/impeccable

- **Skill 版本**：4.8.0；**本地参考的上游快照**：`c3bb418ee38ee49a6b999b7752c1368f3123a2bd`（2026-11-05 的该技能目录最新提交）。
- **引擎版本**：`scripts/VERSION` 固定为 `0.1.18`，校验清单与上游目录一致。仓库其他引擎 Release 不代表本技能已升级引擎。
- **本次同步**：同步 `reference/hooks.md`、`reference/init.md`、`reference/live.md`、`scripts/live-browser.js`；技能主体、其余参考与脚本经 Git Blob SHA 对比保持一致。
- **本地保留**：`LICENSE`、`NOTICE.md` 及本记录文件；`scripts/impeccable.cmd` 与上游仅 CRLF/LF 换行不同，保留本地 Windows 换行格式。启动器权限保持现状。
- **安装边界**：最初封装用于个人 Codex Skill，不通过同步注册自动 hooks、启动 Live Edit、修改审批策略或重新安装任何 ChatGPT 插件。Live Edit 与 Hooks 必须由使用方明确启用。
- **验证边界**：以上是上游内容同步与静态对比记录，不等同于在 Windows、Live 浏览器会话或所有 Agent 环境中完成端到端运行测试。
