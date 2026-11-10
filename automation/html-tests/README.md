# Blog Writer HTML regression checks

Run with Node 22:

```bash
cd automation/html-tests
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

The tests pass the canonical Skill's HTML examples through ByteMD 1.22.0's actual Markdown parser and default sanitizer. They check preserved table relationships, phase totals, and the paragraph following each figure. They also strip presentation attributes and verify that inline layout and active content remain filtered. No sanitizer permissions are relaxed.

These tests cover portable HTML structure. Narrow-screen browser checks and a particular Halo editor/theme still need their own rendering verification.
