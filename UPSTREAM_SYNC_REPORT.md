# 外部 Skill 同步与修正报告

检查周期（北京时间）：2026-W48

覆盖 registry 中全部外部 Skill；自研 Skill 不在自动替换范围内。
该文件由 GitHub Actions 生成，只有候选通过 CI 并合并到 master 才视为同步成功。

| Skill | 结果 | 上次同步 commit | 本次同步 commit | 变更文件 |
|---|---|---|---|---:|
| academic-niceslides | 无变化 | b77c608a993e | b77c608a993e | 0 |
| archify | 已同步 | 62f3a995eb26 | d6b0f71f25a3 | 49 |
| ask-matt | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| caveman | 无变化 | 3dc497a7f858 | 3dc497a7f858 | 0 |
| code-review | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| codebase-design | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| deep-research | 已同步 | d120dfd598a0 | 62f5c2a0e66d | 5 |
| design-taste-frontend | 无变化 | f6b76575f949 | f6b76575f949 | 0 |
| diagnosing-bugs | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| domain-modeling | 已同步 | abeeaf95660b | bbadaa631c37 | 1 |
| frontend-design | 无变化 | ca45fc496a34 | ca45fc496a34 | 0 |
| grill-me | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| grill-with-docs | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| grilling | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| gsap-core | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-frameworks | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-performance | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-plugins | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-react | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-scrolltrigger | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-timeline | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-utils | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| handoff | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| humanizer | 无变化 | b48c832f0f80 | b48c832f0f80 | 0 |
| impeccable | 已同步 | b49177d32788 | 2fc5e1459efb | 13 |
| implement | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| implement-spec | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| improve-codebase-architecture | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| lieflat-charts | 无变化 | 4b4e75bde11c | 4b4e75bde11c | 0 |
| mermaid-diagrams | 无变化 | 3027f20f3181 | 3027f20f3181 | 0 |
| playwright | 无变化 | 49f948faa925 | 49f948faa925 | 0 |
| pr | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| prototype | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| research | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| retro | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| setup-matt-pocock-skills | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| shadcn | 无变化 | 42f3bb63b46a | 42f3bb63b46a | 0 |
| skill-creator | 无变化 | b9e19e6f4477 | b9e19e6f4477 | 0 |
| tdd | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| teach | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| to-questionnaire | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| to-spec | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| to-tickets | 已同步 | abeeaf95660b | bbadaa631c37 | 1 |
| triage | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| wait-what | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| wayfinder | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| web-design-guidelines | 无变化 | 5a37a6329fba | 5a37a6329fba | 0 |
| wizard | 无变化 | abeeaf95660b | abeeaf95660b | 0 |
| writing-for-agents | 无变化 | abeeaf95660b | abeeaf95660b | 0 |

## 文件变更

### archify

上游提交：[d6b0f71f25a3337ed2fcd09c973cacf67be7baba](https://github.com/tt-a1i/archify/commit/d6b0f71f25a3337ed2fcd09c973cacf67be7baba)

| 文件路径 | 变化 |
|---|---|
| assets/template.html | modified |
| bin/archify.mjs | modified |
| bin/delivery-update.mjs | modified |
| bin/finalize.mjs | modified |
| bin/update-notice.mjs | added |
| bin/visual-check.mjs | modified |
| explainer/browser-check.mjs | modified |
| explainer/reader.js | modified |
| modules/code-analysis/bin/prepare.mjs | modified |
| modules/code-analysis/bin/serve.mjs | modified |
| modules/code-analysis/docs/USAGE.md | modified |
| modules/code-analysis/lib/architecture-drift.mjs | modified |
| modules/code-analysis/lib/git-sources.mjs | modified |
| modules/code-analysis/lib/pull-request.mjs | modified |
| modules/code-analysis/lib/task-command.mjs | modified |
| modules/code-analysis/overlay/client/atlas.js | modified |
| modules/code-analysis/overlay/client/overlay.css | modified |
| modules/code-analysis/overlay/client/overlay.js | modified |
| modules/code-analysis/overlay/i18n.mjs | modified |
| modules/code-analysis/overlay/inject.mjs | modified |
| modules/code-analysis/overlay/page.mjs | modified |
| modules/code-analysis/overlay/pull-request-markdown.mjs | added |
| modules/code-analysis/overlay/pull-request.mjs | modified |
| modules/code-analysis/overlay/source-changes.mjs | modified |
| modules/code-analysis/overlay/standalone.mjs | modified |
| modules/code-analysis/test/pull-request.test.mjs | modified |
| package-lock.json | modified |
| package.json | modified |
| references/delivery-contract.md | modified |
| references/pr-review.md | modified |
| references/update-awareness.md | modified |
| renderers/architecture/render-architecture.mjs | modified |
| renderers/class/render-class.mjs | modified |
| renderers/dataflow/dataflow-compiler.mjs | modified |
| renderers/erd/render-erd.mjs | modified |
| renderers/lifecycle/render-lifecycle.mjs | modified |
| renderers/sequence/render-sequence.mjs | modified |
| renderers/shared/change-marks.mjs | modified |
| renderers/shared/generated-validators.mjs | modified |
| renderers/timeline/render-timeline.mjs | modified |
| renderers/tree/render-tree.mjs | modified |
| renderers/waterfall/render-waterfall.mjs | modified |
| renderers/workflow/workflow-compiler.mjs | modified |
| schemas/lifecycle.schema.json | modified |
| scripts/check-update.mjs | modified |
| scripts/delivery-update-child.mjs | modified |
| skill-release.json | modified |
| story/native-motion.js | modified |
| story/story-stage-html.mjs | modified |

### deep-research

上游提交：[62f5c2a0e66d2f38324d9dbc7313f0d006637fec](https://github.com/Imbad0202/academic-research-skills/commit/62f5c2a0e66d2f38324d9dbc7313f0d006637fec)

| 文件路径 | 变化 |
|---|---|
| agents/source_verification_agent.md | modified |
| references/arxiv_api_protocol.md | modified |
| references/crossref_api_protocol.md | modified |
| references/openalex_api_protocol.md | modified |
| references/semantic_scholar_api_protocol.md | modified |

### domain-modeling

上游提交：[bbadaa631c37af594e5a05c9cefacd9956136b18](https://github.com/mattpocock/skills/commit/bbadaa631c37af594e5a05c9cefacd9956136b18)

| 文件路径 | 变化 |
|---|---|
| GLOSSARY-FORMAT.md | modified |

### impeccable

上游提交：[2fc5e1459efbbf06d92c7306517c286bf12490cf](https://github.com/pbakaus/impeccable/commit/2fc5e1459efbbf06d92c7306517c286bf12490cf)

| 文件路径 | 变化 |
|---|---|
| SKILL.md | modified |
| reference/audit.md | modified |
| reference/critique.md | modified |
| reference/generate.md | modified |
| reference/init.md | modified |
| reference/live.md | modified |
| reference/new-work-comp.md | modified |
| reference/new-work-world.md | modified |
| scripts/VERSION | modified |
| scripts/engine-checksums.txt | modified |
| scripts/impeccable | modified |
| scripts/impeccable.cmd | modified |
| scripts/live-browser.js | modified |

### to-tickets

上游提交：[bbadaa631c37af594e5a05c9cefacd9956136b18](https://github.com/mattpocock/skills/commit/bbadaa631c37af594e5a05c9cefacd9956136b18)

| 文件路径 | 变化 |
|---|---|
| SKILL.md | modified |
