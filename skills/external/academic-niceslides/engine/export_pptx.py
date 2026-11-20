"""PowerPoint export.  python3 engine/export_pptx.py <project> [--style slug] [--pages]
Every piece of text becomes a native, editable text box in the deck's own font; charts, shapes and paper figures become
pictures placed underneath. Step-by-step reveals become native "Appear on click" animations (--pages: one slide per click instead).
Also writes out/fonts/*.ttf: install them before opening the file, or PowerPoint substitutes another typeface.
One-way: edits made in PowerPoint do not flow back into deck.json. For changes that should survive a rebuild, use the built-in editor."""
import sys, io, json, copy, pathlib, asyncio, base64
from playwright.async_api import async_playwright
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.oxml.ns import qn
from lxml import etree
E = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(E)); import chrome
P = pathlib.Path(sys.argv[1]).resolve(); arg = lambda k, d=None: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
PAGES = "--pages" in sys.argv; PX = 6350  # EMU per CSS px on a 13.333in slide
COLLECT = r"""
(sl) => { const R = sl.getBoundingClientRect(), out = [], n = +sl.dataset.steps; applyStep(sl, n);
  const rgb = c => (c.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
  const sel = 'h1,h2,p,li>span,figcaption,td,th,footer .who>span,footer .byline,footer .sec,footer .pg,footer .citeline,.secnav span,svg.chart text';
  for (const el of sl.querySelectorAll(sel)) { if (!el.getClientRects().length) continue; const cs = getComputedStyle(el), svg = !!el.closest('svg');
    const runs = [], w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let nd;
    const hard = !svg && (el.matches('h1,h2') || !!el.querySelector('.k')), lh0 = cs.lineHeight === 'normal' ? parseFloat(cs.fontSize) * 1.2 : parseFloat(cs.lineHeight); let lastTop = null;
    while (nd = w.nextNode()) { const p = nd.parentElement, s = getComputedStyle(p); if (s.display === 'none') continue; let t = nd.textContent.replace(/\s+/g, ' '); if (!t) continue;
      if (hard) { const raw = nd.textContent, parts = []; let m, re = /\S+/g, first = true;   // keep the designed line breaks: titles are balanced and highlights are painted underneath
        re = /[^\s-]*-|[^\s-]+/g; let prevEnd = 0;   // split at spaces and after hyphens: browsers break "African-American" at the hyphen
        while (m = re.exec(raw)) { const r = document.createRange(); r.setStart(nd, m.index); r.setEnd(nd, m.index + m[0].length); const top = r.getBoundingClientRect().top;
          const nl = lastTop !== null && top > lastTop + lh0 * .5; lastTop = top; const gap = /\s/.test(raw.slice(prevEnd, m.index)) ? ' ' : '';
          parts.push((nl ? '\n' : gap) + m[0]); prevEnd = m.index + m[0].length; first = false; }
        t = parts.join('') + (/\s$/.test(raw) ? ' ' : ''); if (!t.trim()) continue; }
      const ul = /underline/.test(s.textDecorationLine) || !!p.closest('.k') && /underline/.test(getComputedStyle(p.closest('.k')).textDecorationLine);
      runs.push({t, c: rgb(svg ? s.fill : s.color), b: parseInt(s.fontWeight) >= 600, i: s.fontStyle === 'italic', u: ul}); }
    if (!runs.length || !runs.map(r => r.t).join('').trim()) continue;
    runs[0].t = runs[0].t.replace(/^\s+/, ''); runs[runs.length - 1].t = runs[runs.length - 1].t.replace(/\s+$/, '');
    let b = el.getBoundingClientRect(), x = b.left, y = b.top, bw = b.width, bh = b.height;
    if (!svg) { const pl = parseFloat(cs.paddingLeft) + parseFloat(cs.borderLeftWidth), pr = parseFloat(cs.paddingRight) + parseFloat(cs.borderRightWidth), pt = parseFloat(cs.paddingTop) + parseFloat(cs.borderTopWidth), pb = parseFloat(cs.paddingBottom) + parseFloat(cs.borderBottomWidth);
      x += pl; y += pt; bw -= pl + pr; bh -= pt + pb;
      if (cs.display.startsWith('inline')) { const r = document.createRange(); r.selectNodeContents(el); const q = r.getBoundingClientRect(); x = q.left; y = q.top; bw = q.width; bh = q.height; } }
    const fs = parseFloat(cs.fontSize), lh = cs.lineHeight === 'normal' ? fs * 1.2 : parseFloat(cs.lineHeight);
    const al = svg ? ({middle: 'c', end: 'r'}[el.getAttribute('text-anchor')] || 'l') : ({right: 'r', end: 'r', center: 'c'}[cs.textAlign] || 'l');
    out.push({x: x - R.left, y: y - R.top, w: bw, h: bh, fs, lh, al, svg, lines: Math.max(1, Math.round(bh / lh)), fam: cs.fontFamily.split(',')[0].replace(/"/g, '').trim(),
      hard, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing), step: +((el.closest('[data-step]') || {dataset: {}}).dataset.step || 0), runs});
    el.style.setProperty('-webkit-text-fill-color', 'transparent', 'important'); el.style.setProperty('text-decoration-color', 'transparent', 'important');
    el.querySelectorAll('*').forEach(k => { k.style.setProperty('-webkit-text-fill-color', 'transparent', 'important'); k.style.setProperty('text-decoration-color', 'transparent', 'important'); if (svg) k.style.fillOpacity = 0; });
    if (svg) el.style.fillOpacity = 0; }
  const boxes = {};
  for (let k = 1; k <= n; k++) { const els = [...sl.querySelectorAll(`[data-step="${k}"]`), ...[...sl.querySelectorAll(`[data-zoom="${k}"]`)].map(e => e.closest('.pf'))]; let a = [1e9, 1e9, -1e9, -1e9];
    for (const e of els) { const b = e.getBoundingClientRect(); a = [Math.min(a[0], b.left - R.left), Math.min(a[1], b.top - R.top), Math.max(a[2], b.right - R.left), Math.max(a[3], b.bottom - R.top)]; }
    const pad = 16; boxes[k] = [Math.max(0, Math.floor(a[0] - pad)), Math.max(0, Math.floor(a[1] - pad)), Math.min(1920, Math.ceil(a[2] + pad)), Math.min(1080, Math.ceil(a[3] + pad))]; }
  const assets = [...sl.querySelectorAll('img.logo,[data-asset="anchor"]>*')].filter(e => e.getClientRects().length).map((e, k) => { const b = e.getBoundingClientRect();
    e.dataset.ppt = k; return {k, x: b.left - R.left, y: b.top - R.top, w: b.width, h: b.height, name: e.classList.contains('logo') ? 'Logo ' + (+e.dataset.asset.split('.')[1] + 1) : 'Anchor image',
      uri: e.tagName === 'IMG' ? e.src : '', step: +((e.closest('[data-step]') || {dataset: {}}).dataset.step || 0)}; });
  return {texts: out, steps: n, boxes, assets, say: sl.dataset.say || ''}; }
"""
def timing(groups):
    """groups: [[shape ids appearing on click 1], [click 2], ...] -> <p:timing> with Appear effects."""
    ns = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'; n = [2]
    def nid(): n[0] += 1; return n[0]
    clicks = ""
    for ids in groups:
        fx = ""
        for j, sid in enumerate(ids):
            fx += (f'<p:par><p:cTn id="{nid()}" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" nodeType="{"clickEffect" if j == 0 else "withEffect"}">'
                   f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
                   f'<p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par>')
        clicks += (f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>'
                   f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{fx}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
    return etree.fromstring(f'<p:timing {ns}><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{clicks}</p:childTnLst></p:cTn>'
        f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
def textbox(sl, t):
    slack = 0 if t["svg"] else t["w"]*0.025
    x, w = t["x"], t["w"] + slack
    one = t["svg"] or t["lines"] == 1 or t["hard"]
    if t["hard"] and t["lines"] > 1: w = t["w"] + 300
    elif one:   # single line: never wrap; keep the anchor edge fixed so edits grow the right way
        grow = 400; w = t["w"] + grow
        x = t["x"] - (grow/2 if t["al"] == "c" else grow if t["al"] == "r" else 0)
    tb = sl.shapes.add_textbox(Emu(int(x*PX)), Emu(int(t["y"]*PX)), Emu(int(w*PX)), Emu(int(t["h"]*PX))); tf = tb.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.word_wrap = not one
    tf.auto_size = MSO_AUTO_SIZE.NONE; tf.vertical_anchor = MSO_ANCHOR.TOP if t["lines"] > 1 else MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[t["al"]]
    if t["lines"] > 1: p.line_spacing = round(t["lh"]/(t["fs"]*1.2), 3)
    segs = []
    for r in t["runs"]:
        for j, seg in enumerate(r["t"].split("\n")):
            if j: segs.append(None)
            if seg: segs.append({**r, "t": seg})
    for r in segs:
        if r is None: p.add_line_break(); continue
        run = p.add_run(); run.text = r["t"]; f = run.font; f.name = t["fam"]; f.size = Pt(round(t["fs"]/2, 1)); f.bold = r["b"]; f.italic = r["i"]; f.underline = True if r["u"] else None
        f.color.rgb = RGBColor(*[int(v) for v in r["c"]]); rPr = run._r.get_or_add_rPr()
        if t["ls"]: rPr.set("spc", str(int(round(t["ls"]*50))))
        for tag in ("a:ea", "a:cs"): e = etree.SubElement(rPr, qn(tag)); e.set("typeface", t["fam"])
    return tb
async def main():
    async with async_playwright() as pw:
        b = await chrome.launch(pw); ctx = await b.new_context(viewport={"width": 1920, "height": 1080}, device_scale_factor=2); pg = await ctx.new_page()
        await pg.goto(f"file://{P}/out/deck.html#flat"); style = arg("--style") or await pg.evaluate("ST.style")
        await pg.evaluate("s => { ST.style = s; staticMode('flat'); return document.fonts.ready }", style)
        prs = Presentation(); prs.slide_width = Emu(1920*PX); prs.slide_height = Emu(1080*PX); blank = prs.slide_layouts[6]; fams = set()
        for el in await pg.query_selector_all("#stage .slide"):
            info = await el.evaluate(COLLECT); await el.scroll_into_view_if_needed(); n = info["steps"]; pics = {}; apics = {}
            r0 = await el.bounding_box()
            for a in info["assets"]:      # raster files go in as they are; SVG logos are rasterised at 2x
                u = a["uri"]
                if u.startswith(("data:image/png", "data:image/jpeg")): apics[a["k"]] = base64.b64decode(u.split(",", 1)[1])
                else: apics[a["k"]] = await pg.screenshot(clip={"x": r0["x"]+a["x"], "y": r0["y"]+a["y"], "width": a["w"], "height": a["h"]})
            await el.evaluate("sl => sl.querySelectorAll('[data-ppt]').forEach(e => e.style.visibility = 'hidden')")
            for k in range(n+1):
                await el.evaluate("(sl, k) => applyStep(sl, k)", k); r = await el.bounding_box()
                box = [0, 0, 1920, 1080] if k == 0 else info["boxes"][str(k)]
                png = await pg.screenshot(clip={"x": r["x"]+box[0], "y": r["y"]+box[1], "width": box[2]-box[0], "height": box[3]-box[1]}); pics[k] = (box, png)
            for last in (range(n+1) if PAGES else [n]):          # --pages: one slide per click state
                sl = prs.slides.add_slide(blank); groups = {}
                for k in range(last+1):
                    box, png = pics[k]; pic = sl.shapes.add_picture(io.BytesIO(png), Emu(box[0]*PX), Emu(box[1]*PX), Emu((box[2]-box[0])*PX), Emu((box[3]-box[1])*PX))
                    if k: groups.setdefault(k, []).append(pic.shape_id)
                for a in info["assets"]:
                    if a["step"] > last: continue
                    pic = sl.shapes.add_picture(io.BytesIO(apics[a["k"]]), Emu(int(a["x"]*PX)), Emu(int(a["y"]*PX)), Emu(int(a["w"]*PX)), Emu(int(a["h"]*PX))); pic.name = a["name"]
                for t in info["texts"]:
                    if t["step"] > last: continue
                    fams.add(t["fam"]); tb = textbox(sl, t)
                    if t["step"]: groups.setdefault(t["step"], []).append(tb.shape_id)
                if groups and not PAGES: sl._element.append(timing([groups[k] for k in sorted(groups)]))
                if info["say"]: sl.notes_slide.notes_text_frame.text = info["say"]
        out = P / f"out/{style}{'-pages' if PAGES else ''}.pptx"; prs.save(out); await b.close()
    # fonts for PowerPoint: woff2 -> ttf
    from fontTools.ttLib import TTFont
    (P / "out/fonts").mkdir(exist_ok=True); st = json.load(open(E.parent / "styles" / style / "style.json"))
    for f in st["fonts"]:
        t = TTFont(E.parent / "styles" / style / "fonts" / f["file"]); t.flavor = None; t.save(P / "out/fonts" / f["file"].replace(".woff2", ".ttf"))
    print(f"{out.name}: {len(prs.slides)} slides · fonts in out/fonts ({', '.join(sorted(fams))}) must be installed before opening")
asyncio.run(main())
