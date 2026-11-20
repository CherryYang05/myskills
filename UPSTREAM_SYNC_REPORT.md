# 外部 Skill 同步与修正报告

检查周期（北京时间）：2026-W47

覆盖 registry 中全部外部 Skill；自研 Skill 不在自动替换范围内。
该文件由 GitHub Actions 生成，只有候选通过 CI 并合并到 master 才视为同步成功。

| Skill | 结果 | 上次同步 commit | 本次同步 commit | 变更文件 |
|---|---|---|---|---:|
| academic-niceslides | 已同步 | b77c608a993e | b77c608a993e | 177 |
| caveman | 无变化 | 3dc497a7f858 | 3dc497a7f858 | 0 |
| deep-research | 已同步 | 6d9388674de1 | bd57330f63f4 | 1 |
| design-taste-frontend | 无变化 | f6b76575f949 | f6b76575f949 | 0 |
| frontend-design | 无变化 | ca45fc496a34 | ca45fc496a34 | 0 |
| gsap-core | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-frameworks | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-performance | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-plugins | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-react | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-scrolltrigger | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-timeline | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| gsap-utils | 无变化 | aed9cfd32777 | aed9cfd32777 | 0 |
| humanizer | 无变化 | b48c832f0f80 | b48c832f0f80 | 0 |
| impeccable | 已同步 | c4cd1924c389 | b49177d32788 | 28 |
| lieflat-charts | 无变化 | 4b4e75bde11c | 4b4e75bde11c | 0 |
| mermaid-diagrams | 无变化 | 3027f20f3181 | 3027f20f3181 | 0 |
| playwright | 无变化 | 49f948faa925 | 49f948faa925 | 0 |
| shadcn | 无变化 | 42f3bb63b46a | 42f3bb63b46a | 0 |
| skill-creator | 无变化 | b9e19e6f4477 | b9e19e6f4477 | 0 |
| web-design-guidelines | 无变化 | 1a2c79d4e6c4 | 1a2c79d4e6c4 | 0 |

## 文件变更

### academic-niceslides

上游提交：[b77c608a993e65ee44120a6eceeb708a2d8d39ed](https://github.com/kingofwinter1994/academic_niceslides/commit/b77c608a993e65ee44120a6eceeb708a2d8d39ed)

| 文件路径 | 变化 |
|---|---|
| .gitignore | added |
| AGENTS.md | added |
| LICENSE | added |
| NOTICE.md | added |
| PRESENTER.md | added |
| README.md | added |
| README.zh-CN.md | added |
| SKILL.md | added |
| TASKS.md | added |
| docs/editor.jpg | added |
| docs/reveal.gif | added |
| docs/steps.jpg | added |
| docs/styles.jpg | added |
| docs/styles/access-all.jpg | added |
| docs/styles/access.gif | added |
| docs/styles/arch-all.jpg | added |
| docs/styles/arch.gif | added |
| docs/styles/chalk-all.jpg | added |
| docs/styles/chalk.gif | added |
| docs/styles/chapter-all.jpg | added |
| docs/styles/chapter.gif | added |
| docs/styles/cite-all.jpg | added |
| docs/styles/cite.gif | added |
| docs/styles/feature-all.jpg | added |
| docs/styles/feature.gif | added |
| docs/styles/fingerprint-all.jpg | added |
| docs/styles/fingerprint.gif | added |
| docs/styles/grid-all.jpg | added |
| docs/styles/grid.gif | added |
| docs/styles/kraft-all.jpg | added |
| docs/styles/kraft.gif | added |
| docs/styles/marker-all.jpg | added |
| docs/styles/marker.gif | added |
| docs/styles/mono-all.jpg | added |
| docs/styles/mono.gif | added |
| docs/styles/night-all.jpg | added |
| docs/styles/night.gif | added |
| docs/styles/plate-all.jpg | added |
| docs/styles/plate.gif | added |
| docs/styles/rail-all.jpg | added |
| docs/styles/rail.gif | added |
| docs/styles/riso-all.jpg | added |
| docs/styles/riso.gif | added |
| docs/styles/seal-all.jpg | added |
| docs/styles/seal.gif | added |
| docs/styles/transit-all.jpg | added |
| docs/styles/transit.gif | added |
| engine/app.css | added |
| engine/base.css | added |
| engine/build.py | added |
| engine/chrome.py | added |
| engine/export_pptx.py | added |
| engine/extract.py | added |
| engine/js/app.js | added |
| engine/js/editor.js | added |
| engine/js/lint.js | added |
| engine/js/render.js | added |
| engine/lint.py | added |
| engine/render.py | added |
| examples/resume/analysis.py | added |
| examples/resume/assets/logo-institute-light.svg | added |
| examples/resume/assets/logo-institute.svg | added |
| examples/resume/assets/logo-project-light.svg | added |
| examples/resume/assets/logo-project.svg | added |
| examples/resume/assets/paper_fig2.png | added |
| examples/resume/data/ResumeNames.csv | added |
| examples/resume/deck.json | added |
| examples/resume/facts.json | added |
| examples/resume/make_paper_figure.py | added |
| requirements.txt | added |
| styles/README.md | added |
| styles/_template/STYLE.md | added |
| styles/access/STYLE.md | added |
| styles/access/fonts/LICENSE.txt | added |
| styles/access/fonts/lexend-latin-400-normal.woff2 | added |
| styles/access/fonts/lexend-latin-700-normal.woff2 | added |
| styles/access/style.css | added |
| styles/access/style.json | added |
| styles/arch/STYLE.md | added |
| styles/arch/fonts/LICENSE.txt | added |
| styles/arch/fonts/outfit-latin-400-normal.woff2 | added |
| styles/arch/fonts/outfit-latin-700-normal.woff2 | added |
| styles/arch/style.css | added |
| styles/arch/style.json | added |
| styles/chalk/STYLE.md | added |
| styles/chalk/fonts/LICENSE.txt | added |
| styles/chalk/fonts/atkinson-hyperlegible-latin-400-normal.woff2 | added |
| styles/chalk/fonts/atkinson-hyperlegible-latin-700-normal.woff2 | added |
| styles/chalk/style.css | added |
| styles/chalk/style.json | added |
| styles/chapter/STYLE.md | added |
| styles/chapter/fonts/LICENSE.txt | added |
| styles/chapter/fonts/figtree-latin-400-normal.woff2 | added |
| styles/chapter/fonts/figtree-latin-700-normal.woff2 | added |
| styles/chapter/style.css | added |
| styles/chapter/style.json | added |
| styles/cite/STYLE.md | added |
| styles/cite/fonts/LICENSE.txt | added |
| styles/cite/fonts/libre-franklin-latin-400-normal.woff2 | added |
| styles/cite/fonts/libre-franklin-latin-700-normal.woff2 | added |
| styles/cite/style.css | added |
| styles/cite/style.json | added |
| styles/feature/STYLE.md | added |
| styles/feature/fonts/LICENSE.txt | added |
| styles/feature/fonts/fraunces-latin-400-italic.woff2 | added |
| styles/feature/fonts/fraunces-latin-400-normal.woff2 | added |
| styles/feature/fonts/fraunces-latin-600-normal.woff2 | added |
| styles/feature/style.css | added |
| styles/feature/style.json | added |
| styles/fingerprint/STYLE.md | added |
| styles/fingerprint/fonts/LICENSE.txt | added |
| styles/fingerprint/fonts/schibsted-grotesk-latin-400-normal.woff2 | added |
| styles/fingerprint/fonts/schibsted-grotesk-latin-700-normal.woff2 | added |
| styles/fingerprint/style.css | added |
| styles/fingerprint/style.json | added |
| styles/grid/STYLE.md | added |
| styles/grid/fonts/LICENSE.txt | added |
| styles/grid/fonts/archivo-latin-400-normal.woff2 | added |
| styles/grid/fonts/archivo-latin-700-normal.woff2 | added |
| styles/grid/style.css | added |
| styles/grid/style.json | added |
| styles/kraft/STYLE.md | added |
| styles/kraft/fonts/LICENSE.txt | added |
| styles/kraft/fonts/zilla-slab-latin-400-normal.woff2 | added |
| styles/kraft/fonts/zilla-slab-latin-700-normal.woff2 | added |
| styles/kraft/style.css | added |
| styles/kraft/style.json | added |
| styles/marker/STYLE.md | added |
| styles/marker/fonts/LICENSE.txt | added |
| styles/marker/fonts/public-sans-latin-400-normal.woff2 | added |
| styles/marker/fonts/public-sans-latin-700-normal.woff2 | added |
| styles/marker/style.css | added |
| styles/marker/style.json | added |
| styles/mono/STYLE.md | added |
| styles/mono/fonts/LICENSE.txt | added |
| styles/mono/fonts/bitter-latin-400-normal.woff2 | added |
| styles/mono/fonts/bitter-latin-700-normal.woff2 | added |
| styles/mono/style.css | added |
| styles/mono/style.json | added |
| styles/night/STYLE.md | added |
| styles/night/fonts/LICENSE.txt | added |
| styles/night/fonts/red-hat-display-latin-400-normal.woff2 | added |
| styles/night/fonts/red-hat-display-latin-700-normal.woff2 | added |
| styles/night/style.css | added |
| styles/night/style.json | added |
| styles/plate/STYLE.md | added |
| styles/plate/fonts/LICENSE.txt | added |
| styles/plate/fonts/source-serif-4-latin-400-italic.woff2 | added |
| styles/plate/fonts/source-serif-4-latin-400-normal.woff2 | added |
| styles/plate/fonts/source-serif-4-latin-600-normal.woff2 | added |
| styles/plate/style.css | added |
| styles/plate/style.json | added |
| styles/rail/STYLE.md | added |
| styles/rail/fonts/LICENSE.txt | added |
| styles/rail/fonts/ibm-plex-sans-latin-400-normal.woff2 | added |
| styles/rail/fonts/ibm-plex-sans-latin-600-normal.woff2 | added |
| styles/rail/style.css | added |
| styles/rail/style.json | added |
| styles/riso/STYLE.md | added |
| styles/riso/fonts/LICENSE.txt | added |
| styles/riso/fonts/bricolage-grotesque-latin-400-normal.woff2 | added |
| styles/riso/fonts/bricolage-grotesque-latin-700-normal.woff2 | added |
| styles/riso/style.css | added |
| styles/riso/style.json | added |
| styles/seal/STYLE.md | added |
| styles/seal/fonts/LICENSE.txt | added |
| styles/seal/fonts/literata-latin-400-italic.woff2 | added |
| styles/seal/fonts/literata-latin-400-normal.woff2 | added |
| styles/seal/fonts/literata-latin-600-normal.woff2 | added |
| styles/seal/style.css | added |
| styles/seal/style.json | added |
| styles/transit/STYLE.md | added |
| styles/transit/fonts/LICENSE.txt | added |
| styles/transit/fonts/overpass-latin-400-normal.woff2 | added |
| styles/transit/fonts/overpass-latin-700-normal.woff2 | added |
| styles/transit/style.css | added |
| styles/transit/style.json | added |

### deep-research

上游提交：[bd57330f63f4b089dde8fdef9bf5f009ecc89f0c](https://github.com/Imbad0202/academic-research-skills/commit/bd57330f63f4b089dde8fdef9bf5f009ecc89f0c)

| 文件路径 | 变化 |
|---|---|
| agents/timeline_extraction_agent.md | modified |

### impeccable

上游提交：[b49177d32788f2dc585c42831d845dacf1ebed2c](https://github.com/pbakaus/impeccable/commit/b49177d32788f2dc585c42831d845dacf1ebed2c)

| 文件路径 | 变化 |
|---|---|
| SKILL.md | modified |
| agents/impeccable_documenter.toml | modified |
| agents/impeccable_finish_reviewer.toml | modified |
| agents/impeccable_motion_reviewer.toml | added |
| reference/adapt.md | modified |
| reference/animate.md | modified |
| reference/audit.md | modified |
| reference/audit.native.md | modified |
| reference/craft-floor.md | modified |
| reference/critique-rubric.md | added |
| reference/critique.md | modified |
| reference/degraded/documenter.md | modified |
| reference/degraded/finish-reviewer.md | modified |
| reference/degraded/motion-reviewer.md | added |
| reference/doctor.md | modified |
| reference/document.md | modified |
| reference/foundations.md | added |
| reference/hooks.md | modified |
| reference/init.md | modified |
| reference/live.md | modified |
| reference/new-work-comp.md | added |
| reference/new-work-world.md | added |
| reference/new-work.md | modified |
| reference/polish.md | modified |
| reference/typeset.md | modified |
| scripts/VERSION | modified |
| scripts/engine-checksums.txt | modified |
| scripts/live-browser.js | modified |
