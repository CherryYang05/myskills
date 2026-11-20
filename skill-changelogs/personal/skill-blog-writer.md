# blog-writer 修订记录

- 2026-11-10 — 建立当前仓库版本的修订基线。[8561edd6e7c8](https://github.com/CherryYang05/myskills/commit/8561edd6e7c86a9e2289fad0c316741bc33e3834) · 重写 blog-writer，以读者目标和证据组织博客 (#30)
- 2026-11-10 — 增加 Halo/ByteMD 原始 HTML block 约束、公式标题规范、Markdown 结构预检与 Blog MCP 写入后回读验证。
- 2026-11-10 — 修复 ByteMD 清理内联样式后配图布局丢失的问题：默认使用不依赖 CSS 的 HTML 行列和步骤结构，增加分组、耗时示例及真实清理器回归检查。
- 2026-11-10 — 按用户要求原样使用 Intelligent UI 生成的 HTML，撤回强制表格与去样式要求；仅处理 Markdown 嵌入格式并核对源码和实际呈现。
