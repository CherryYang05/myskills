# 仓库结构与维护约定

本仓库保留 **扁平的 Skill 包布局**：每个根目录下有 `SKILL.md` 的目录都是可安装 Skill，不把这些包移动进统一的 `skills/` 子目录，以免破坏 `npx skills` 现有路径与 Marketplace 引用。

```text
myskills/
├── <skill-name>/SKILL.md              # 可安装技能包，含自研与外部来源
├── skill-sync/
│   ├── SKILL.md                       # 自研的安装、更新、同步指导
│   ├── upstreams.json                 # 外部来源唯一登记表
│   ├── scripts/                      # 发现/同步、报告、目录、校验及自动合并
│   ├── tests/                        # 回归测试
│   └── hooks/pre-commit              # 本地生成 README 和 Marketplace
├── .github/workflows/
│   ├── sync-upstream.yml             # 每周五检查并自动合并通过校验的更新
│   └── validate-skills.yml           # PR 与 master 的质量门禁
├── .agents/plugins/marketplace.json  # ChatGPT 工作区插件清单（生成物）
├── docs/
│   ├── marketplace.md                # GitHub → ChatGPT 工作区同步方式
│   ├── upstream-sync.md              # 外部上游 → 本仓库同步策略
│   ├── repository-structure.md       # 本文
│   └── upstream-reports/             # 单个 Skill 的变更明细及健康记录
├── README.md                         # 安装说明与来源版本目录（生成物）
└── UPSTREAM_SYNC_REPORT.md           # 根目录外部 Skill 修正报告（生成物）
```

## 来源认定

- `skill-sync/upstreams.json` 是唯一的外部来源登记表。每个键是根目录下实际存在、含 `SKILL.md` 的技能目录名；所有登记项均参与每周同步。**不在登记表中的 Skill 不会被自动覆盖**。
- 默认未登记 Skill 在 README 中显示“自研”。**这是一项维护约定，不是自动鉴定作者身份**。引入新的第三方 Skill 时，必须在同一个变更中登记来源、上游仓库/路径、跟踪 ref 和同步基线；否则它会被漏检且被错误展示为自研。
- `sync.repository`、`sync.path`、`sync.ref` 定义真实上游；`sync.synced_commit` 记录已落地的完整 SHA；`version` 为 README 展示用的可追溯版本；`url` 为可读的来源链接；`sync.last_reported` 只用于避免重复报告。部分字段可理论上派生，但目前被不同脚本和测试显式使用，暂时保留以避免静默破坏同步链路。
- 已登记的外部技能采用 `replace` 策略，必须完整同步其管理目录。上游自带的 README、示例、插件配置、许可证和脚本可能是技能运行所需或其来源组成部分；不能因为看起来“多余”就在仓库里单独删除，否则下次上游同步会重新加入。
- 本仓库自研 Skill 只接受正常人工维护及质量检查。GitHub Action 不会遍历并覆盖这些目录。

## 生成物与依赖

| 文件 | 唯一维护入口 | 说明 |
| --- | --- | --- |
| `README.md` | `skill-sync/scripts/gen_readme.py` | 含各 Skill 版本、来源与说明；不要直接编辑生成后的文件 |
| `.agents/plugins/marketplace.json` | `skill-sync/scripts/gen_marketplace.py` | 由根目录所有 Skill 的 `SKILL.md` 生成，既含外部 Skill 也含自研 Skill |
| `UPSTREAM_SYNC_REPORT.md` | `skill-sync/scripts/sync_upstream.py --apply` | 候选报告；只有合并到 master 才代表落地 |
| `docs/upstream-reports/*` | 同步脚本 | 变更详情与月度健康记录，不要手工修改版本状态 |

手动开发前，运行 `python3 -m pip install pyyaml`。在源码 Git 工作树启用 `git config core.hooksPath skill-sync/hooks` 后，每次提交会生成 README 和 Marketplace；任何生成失败都会阻断本地提交。CI 还会阻止提交 Python bytecode、`__pycache__`、`.pytest_cache` 和 `node_modules` 等运行时缓存。

## 清理原则

2026-11-08 的维护删除了已被 Git 跟踪的 Python `.pyc` 缓存，以及三份未被引用、内容与现行同步策略或版本不一致的一次性说明（旧的 Impeccable / UI 设计来源 / Web Skill 来源核对）。历史内容依然可从 Git 提交记录恢复。

暂不移动现有 Skill 包，也不清除外部 Skill 目录里的配置、参考资料及大文件。重构 `upstreams.json` 字段或搬动 `skill-sync` 自动化脚本需要同步修改源码、工作流和测试，宜作为单独 PR 并跑完整同步与安装验证。
