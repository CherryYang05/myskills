# Instructions for coding agents (Codex and others)

This repository is a skill: a method plus an engine for turning a research paper into an academic talk.

When the user asks for slides, a deck or a talk for a paper, thesis, seminar, conference or defence,
or asks to restyle or fix academic slides, follow `SKILL.md` exactly. It is written for any agent, not only Claude.

- `LIB` in `SKILL.md` is the root of this repository.
- When asked to **install**, clone `https://github.com/mamingatzu/academic_niceslides` into your skill/tools directory, run `pip install -r requirements.txt`, ensure Chrome/Chromium (or Playwright Chromium) is available, and verify with `examples/resume`. When asked to **update**, run `git -C $LIB pull --ff-only` and `pip install -r $LIB/requirements.txt`.
- Before building a deck, follow the **Ask once, then work** section in `SKILL.md`: if the user did not specify a style, proactively ask which one they want, list all 17 style names with the repo preview link, and confirm whether to use the default 7-part structure (`RQ` → `Gap in Literature` → `Theory and Hypotheses` → `Data and Methods` → `Core Findings (detail)` → `Contribution` → `Limitations / Future Study`) and whether any section has special requirements.
- Read `PRESENTER.md` before the first deck, then `styles/README.md` and the `STYLE.md` of the style in use.
- Never edit `engine/` or a style's CSS to make `engine/lint.py` pass. Fix the deck instead.
- Each talk lives in its own project folder outside this repository (copy the shape of `examples/resume/`).
- To check your setup: run the commands under "Try the example" in `README.md`; all 17 styles must print PASS.
