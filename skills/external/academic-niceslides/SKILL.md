---
name: academic_niceslides
description: Build academic talk slides from a paper without AI-slop. Use when the user wants slides, a deck or a talk for a paper, thesis, seminar, conference or defence, or asks to restyle or fix academic slides.
---

# academic_niceslides: academic slides from a paper

You turn a paper into a talk. The engine in this folder renders a semantic deck file in any of the styles under `styles/`,
and a deterministic lint decides whether a deck may be delivered. Talk to the user in their language; write deck text in the language of the talk.

Read `PRESENTER.md` in full before the first deck. It is the method every style shares. Then read `styles/README.md`,
and the `STYLE.md` of the style in use.

## Setup (once) & Update

`LIB` is the folder holding this file (a clone of https://github.com/mamingatzu/academic_niceslides). If you cannot find it, clone it; do not rebuild the engine from memory. Needs Python 3.10+ with `pip install -r $LIB/requirements.txt`, and Chrome
(or `playwright install chromium`; set `ACADEMIC_NICESLIDES_CHROME` to a browser path if it is not found). Fonts are bundled.
Each talk is a project folder holding `deck.json`, `facts.json` and `assets/`. Copy `examples/resume/` to see the shape; never edit it.

- **When the user asks to install `academic_niceslides`** (e.g., sending you `https://github.com/mamingatzu/academic_niceslides` and asking you to install it): clone the repo into your agent's skill directory (e.g., `~/.claude/skills/academic_niceslides` for Claude Code, or a persistent tools path such as `~/tools/academic_niceslides`), run `pip install -r $LIB/requirements.txt`, make sure Chrome/Chromium is available (run `python3 -m playwright install chromium` if Chrome is missing), and verify with `examples/resume` (`analysis.py`, `make_paper_figure.py`, `engine/build.py examples/resume --open gallery`, `engine/lint.py examples/resume` — all 17 styles must print PASS).
- **When the user asks to update `academic_niceslides`**: run `git -C $LIB pull --ff-only` and `pip install -r $LIB/requirements.txt`, then confirm the new commit/status.

## Ask once, then work

Before writing the deck, check what the user has already provided and ask **once** in a single concise message (in the user's language) for anything missing, then wait for their reply before building (unless they explicitly told you not to ask, or no interactive user is present).

1. **Template / style (required if the user did not name one).** Proactively ask which of the 17 templates/styles they want to use, **list all 17 style names** (grouped as below, in the user's language plus the slug), and include the repository link so they can visually inspect what all 17 styles look like before choosing:
   - English preview link: `https://github.com/mamingatzu/academic_niceslides#17-styles`
   - Chinese preview link: `https://github.com/mamingatzu/academic_niceslides/blob/main/README.zh-CN.md#17-%E7%A7%8D%E9%A3%8E%E6%A0%BC`
   - You may recommend one or two styles suited to their venue (from `styles/README.md`), or offer to render a local gallery (`--open gallery`) if they still want to compare on their own slides.

   All 17 styles:
   - *Material / 材质*: `plate` (Journal Plate / 期刊图版), `grid` (Swiss Grid / 瑞士网格), `riso` (Two-ink Riso / 双色孔版), `arch` (Mid-century Arch / 中古拱形), `seal` (Ink and Seal / 宣纸朱印), `transit` (Transit Map / 线路图), `marker` (Highlighter / 荧光笔), `chalk` (Chalkboard / 黑板)
   - *Structure / 结构*: `rail` (Outline Rail / 侧栏纲要), `chapter` (Chapter Colour / 章节色), `feature` (Side Title / 侧题特稿)
   - *Circulation / 传播*: `cite` (Citation Card / 署名卡), `mono` (One Ink / 单色墨), `access` (Large Print / 无障碍大字)
   - *Venue and identity / 场地与身份*: `night` (Night Hall / 夜场), `fingerprint` (Data Fingerprint / 数据指纹), `kraft` (Kraft and White Ink / 牛皮纸)

2. **Talk structure & per-section requirements (required unless the user already specified a custom outline).** Present the default 7-part structure (`RQ` → `Gap in Literature` → `Theory and Hypotheses` → `Data and Methods` → `Core Findings (detail)` → `Contribution` → `Limitations / Future Study`) and ask the author:
   - Whether they want to follow this 7-part structure; and
   - Whether they have any special requirements for any specific section (and tell them explicitly: if they have no special requirements, you will proceed directly).
3. **Missing essentials (only what you cannot find yourself).** The paper (PDF) and any data or replication files; talk length and audience; speaker's name and email for the footer; logos to show (files, plus a light version if a dark style like `chalk` or `night` is chosen); whether they want to approve storyboard titles first.

If no interactive user is available to answer: take 12 minutes, a specialist audience, the default 7-part structure, no logos, and show all style options in the delivered gallery (`--open gallery`).

## Default talk structure

Unless the author specifies otherwise, organize the talk (after the `title` slide) into these seven parts using the existing layouts (`flow`, `fig`, `models`, `paperfig`, `close` — never invent new layout names):

1. **RQ (Research Question)** — the core puzzle, research question, and motivation (`flow` or `paperfig`).
2. **Gap in Literature** — what prior literature establishes and the specific unresolved gap (`flow`, or `paperfig` for a comparison/overview figure).
3. **Theory and Hypotheses** — theoretical mechanism, conceptual framework, and testable hypotheses (`flow`, or `paperfig` for a theoretical diagram from the paper).
4. **Data and Methods** — dataset, sample, identification strategy / experimental or empirical design, and estimation (`flow`, `paperfig`, or `fig`).
5. **Core Findings (detail)** — the centerpiece of the talk, spanning multiple slides as needed for main results, key charts/tables/models/paper figures, heterogeneity or mechanisms, and robustness checks (`fig`, `models`, `paperfig`; every number grounded in `facts.json`).
6. **Contribution** — main theoretical, empirical, or methodological contributions (`flow` or `close`).
7. **Limitations / Future Study** — key caveats, scope conditions, and directions for future research (`flow`, or integrated into the closing `close` slide alongside takeaways, references, and QR code).

Keep two rules in mind:
- Put section labels in `meta.sections` (for footer/rail navigation), **not** as bare topic-phrase slide titles — every slide `title` must still be a claim sentence (>= 6 words, <= 2 lines, no trailing colon).
- Keep `meta.sections` names concise. For `rail` or `chapter` (which work best with <= 6 nav entries), merge adjacent nav labels in `meta.sections` if needed (e.g., `RQ & Gap` or `Contribution & Limitations`) while keeping all 7 content parts in the slides.

## Steps

1. **Confirm & Ground.** First complete the **Ask once, then work** confirmation if style or structure was not specified. Once confirmed, write `<project>/analysis.py` that computes every number the talk will show into `facts.json`
   (`{id: {value, text, how}}`). With no data, register the numbers as published and say so in `how` ("Table 2, column 3, p. 14").
   Take figures out of the PDF with `python3 $LIB/engine/extract.py <project> paper.pdf --find <page>` then `--page --bbox --name --label`.
   Never retype a figure, never generate an image.
2. **Storyboard.** Write `deck.json` following the confirmed structure (defaulting to the 7-part structure above with detailed Core Findings and any user-specified per-section instructions): for each slide an assertion title (a full sentence, at most two lines), the one piece of evidence,
   the notes, and the click order. If the user asked to approve it, send the titles as a list and wait.
3. **Choose the style.** Build in the style the user chose. Only if the user still wants to compare options on their own slides (or no style was chosen in an unattended run), build two or three slides in all styles (`build.py <project> --open gallery`)
   and send `out/deck.html`: it opens as a gallery of every style, and recommend one with a reason from `styles/README.md`.
4. **Build.** `python3 $LIB/engine/build.py <project> --styles <slug>` writes `out/deck.html`, one self-contained file.
5. **Lint.** `python3 $LIB/engine/lint.py <project>` must pass. Fix the deck, not the rule: shorten a title, cut a sentence, crop further.
   Do not edit `engine/` or a style's CSS to make a failure go away.
6. **Look.** `python3 $LIB/engine/render.py <project> <slug>` and read `out/sheets/<slug>.png` and `out/steps/<slug>.png` yourself.
   One fix round for what you see: empty halves, a figure too small to read, a click that reveals nothing worth a click.
7. **Deliver.** `out/deck.html` and `out/<slug>.pdf` (one page per click). Tell the user, in their language and in three lines:
   which style you used; which claims you softened because the evidence did not carry them; and that the HTML file edits itself
   (press E while presenting): text, click order, chart labels, figure crop and zoom, colours, slide order, speaker notes.
   If they need PowerPoint: `python3 $LIB/engine/export_pptx.py <project> --style <slug>`, then send the `.pptx` with `out/fonts/`.

## After delivery

- The user sends back an edited `deck.json` (exported from the editor): put it in the project, lint, rebuild. Never overwrite it with your earlier version.
  Images they uploaded travel inside it under `uploads`; `build.py` unpacks them into `assets/uploads/` and rewrites the paths.
- Tell users that in the editor they click any text, label, logo, image or chart to get its own toolbar, the way Google Slides works.
- "Change X on slide N": edit `deck.json`, not the HTML. Rebuild and lint.
- PowerPoint is a one-way exit: text is native and editable, charts and figures are pictures, reveals are native click animations
  (`--pages` gives one slide per click instead). Edits made in PowerPoint are lost on the next build; say so once.

## The deck file

See `examples/resume/deck.json` for every layout in use. Top level: `{"meta": {...}, "slides": [...]}`. Layouts: `title`, `flow` (numbered steps), `fig` (chart + notes),
`models` (coefficient plot + table), `paperfig` (a figure from the paper), `close` (numbered conclusions + references).
Chart kinds: `bars`, `lines`, `coef`. Text markup: `{fact_id}`, `[a|term]` / `[b|term]` (ties a word to a data series), `[c|citation]`.

- **Numbers** appear only as `{fact_id}`. The build fails on an unregistered id.
- **Step-by-step reveal**: add `"at": n` to a bar, a series, a coefficient row, a table row, a note or a step. Bars also take
  `"gap"` (a dimension line with the difference) and `"sig"` (a bracket with the test result), each with its own `"at"`.
  Typical order: groups → difference → test. At most four clicks a slide.
- **Logos**: `META["logos"] = [{"file", "dark", "alt"}]`. They show on the title slide and, the first one, in the footer. Nowhere else.
- **Paper figures**: `"figure": {"src", "source", "text_px", "crop": [x, y, w, h], "cover": [[x, y, w, h]], "focus": {"box": [x, y, w, h], "at": 1}}`.
  Boxes are fractions; `crop` of the image, `cover` and `focus` of the cropped view. `text_px` comes from `extract.py`.
  Say in the caption what was left out. If lint reports `figure-legible`, crop or zoom further, or redraw from registered data and say "redrawn from Table X".
- **Footer**: `meta.short` (short title), `meta.author` and `meta.email` appear on every content slide. Ask for them; never invent an email.
- **Text formatting**: `[s|bold]`, `[e|extra accent]`, `[m|muted]` besides `[a|..]` and `[b|..]`. Use them sparingly; the editor applies the same markup.
- **Arrangement**: `"lay": {"side": "l"|"r", "split": 5–9, "valign": "start"|"center"|"end"}` on `fig`, `paperfig`, `flow`, `close` slides. Omit it to keep the style's layout.
- **Optional**: `"say"` on a slide is its speaker note (N while presenting; `render.py --handout` prints slides with notes). `meta.cite` is the full citation, `meta.link` a URL that becomes a QR code on the closing slide, `meta.style` the default style.
- **Anchor**: `META["anchor"] = {"kind": "image", "src": "assets/..."}` for one image from the paper that recurs on the title, method and closing slides. Omit it if the paper has none.

## What you never do

- No text above the title, no number set larger than its sentence, no cards, icon rows or decorative labels. The deck file has no field for them; do not add one.
- No second typeface, no text under 14pt (28px), no slide whose title is a topic rather than a claim.
- No altered paper figure: crop, cover and zoom only. No AI-generated or stock images.
- No claim in a title that the evidence on the slide does not support.

## Requests that change the plan

- **"More polished"** means composition, not ornament: one main visual a slide, the anchor repeated, a different style. Not smaller type or more elements.
- **A new style**: `PRESENTER.md` §15. Write the `STYLE.md` first; a style is a medium, not a palette.
- **PowerPoint**: export it (see above) and name the limits: pictures for charts, fonts to install, one-way.
- **Speaker notes or a handout**: fill `"say"` on each slide, then `render.py <project> <slug> --handout`.
