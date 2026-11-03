# Impeccable

来源：pbakaus/impeccable 的 Codex 分发目录 .agents/skills/impeccable。完整提交：9fadc41729c38fd47d7ae622b501558653f9d2e9。技能版本 4.8.0，引擎版本 0.1.18，Apache-2.0。

本包与本机已安装版本一致，保留全部指令、参考文档、字体数据、脚本、LICENSE 与 NOTICE。引擎二进制不入库；启动器按 scripts/engine-checksums.txt 验证固定版本下载。

安装本包不会自行注册自动 hooks、启动 Live Edit、修改审批设置或创建定时同步任务。本机现有安装未启用自动 hooks 和 Live Edit。上游采用 review 模式，避免自动覆盖执行相关内容。

上游 Live Edit 的 fallback 执行路径可能使用关闭审批/沙箱的运行参数。安装并不等于授权该路径，使用时仍遵循用户现有权限和审批约束。常用入口：$impeccable critique <目标>、$impeccable polish <目标>。
