/* academic_niceslides renderer: deck JSON + facts -> slide HTML. The only renderer; the editor, lint, PDF and PPTX all read its output. */
const LX = {D: null, F: null, IMG: null, STY: null, missing: new Set()};
const M = '−';
const SLOTS = {fig: [1109, 600], coef: [1680, 250], paperfig: [1109, 620], glyph_title: [520, 430], glyph_flow: [480, 400], glyph_close: [330, 280]};
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const step = at => at ? ` data-step="${at}"` : '';
const sp = p => ` data-sp="${p}"`;
const ed = p => ` data-path="${p}"`;
const it = x => typeof x === 'string' ? [x, 0] : [x.t, x.at || 0];
const V = k => { const f = LX.F[k]; if (!f) { LX.missing.add(k); return 0; } return f.value; };
function fact(k, tag) {
  const f = LX.F[k];
  if (!f) { LX.missing.add(k); return `<${tag} class="nofact">{${esc(k)}}</${tag}>`; }
  return `<${tag} data-fact="${k}"${tag === 'span' ? ` title="${esc(f.how)}"` : ''}>${esc(f.text).replace(/-/g, M)}</${tag}>`;
}
function rich(s) {
  return esc(s).replace(/\{(\w+)\}/g, (_, k) => fact(k, 'span'))
    .replace(/\[s\|([^\]]+)\]/g, '<strong class="k s">$1</strong>').replace(/\[([abem])\|([^\]]+)\]/g, '<span class="k $1">$2</span>').replace(/\[c\|([^\]]+)\]/g, '<span class="cite">$1</span>');
}
const tx = s => esc(s).replace(/\{(\w+)\}/g, (_, k) => fact(k, 'tspan'));
const T = (x, y, s, cls = '', anchor = 'start', raw = false, lp = '') => `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" class="${cls}" text-anchor="${anchor}"${lp ? ` data-lpath="${lp}"` : ''}>${raw ? s : esc(s)}</text>`;
const L = (x1, y1, x2, y2, cls) => `<line x1="${x1.toFixed(1)}" y1="${y1.toFixed(1)}" x2="${x2.toFixed(1)}" y2="${y2.toFixed(1)}" class="${cls}"/>`;
const svg = (w, h, body, label) => `<svg class="chart" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${label}">${body}</svg>`;
const whisker = (x, ylo, yhi, cls, cap = 14) => L(x, ylo, x, yhi, 'ci ' + cls) + L(x - cap, ylo, x + cap, ylo, 'ci ' + cls) + L(x - cap, yhi, x + cap, yhi, 'ci ' + cls);
function patternSheet(slug) {
  return `<svg class="defs" width="0" height="0" style="position:absolute" aria-hidden="true"><defs>` +
    `<pattern id="ht-${slug}" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="6" cy="6" r="3.6" class="ht-dot"/></pattern>` +
    `<pattern id="hx-${slug}" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="14" class="hx-line"/></pattern>` +
    `<linearGradient id="wash-${slug}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" class="wash-0"/><stop offset="1" class="wash-1"/></linearGradient>` +
    `<filter id="rough-${slug}" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="n"/>` +
    `<feDisplacementMap in="SourceGraphic" in2="n" scale="5"/></filter></defs></svg>`;
}
function axisY(o, c, ml, mt, pw, ph) {
  for (const t of c.ticks) { const y = mt + ph * (1 - t / c.ymax); o.push(L(ml, y, ml + pw, y, t ? 'grid' : 'axis'), T(ml - 18, y + 10, t + (c.unit || ''), 'tick', 'end')); }
}
const CH = {
  bars(c, w, h, P) {
    const sig = c.sig, gap = c.gap, ml = 110, mr = gap ? 330 : 40, mt = sig ? 112 : 64, mb = 118;
    const pw = w - ml - mr, ph = h - mt - mb, n = c.bars.length, slot = pw / n, bw = slot * 0.54, Y = v => mt + ph * (1 - v / c.ymax), o = [], xs = [];
    axisY(o, c, ml, mt, pw, ph);
    c.bars.forEach((b, i) => { const x = ml + slot * (i + .5), s = b.s, g = []; xs.push(x); let top = Y(V(b.v));
      g.push(`<rect x="${(x - bw / 2).toFixed(1)}" y="${top.toFixed(1)}" width="${bw.toFixed(1)}" height="${(Y(0) - top).toFixed(1)}" class="bar ${s}"/>`);
      if (b.lo) { g.push(whisker(x, Y(V(b.lo)), Y(V(b.hi)), s)); top = Y(V(b.hi)); }
      g.push(T(x, top - 18, tx(`{${b.v}}`), 'val ' + s, 'middle', true));
      (b.label || []).forEach((t, j) => g.push(T(x, Y(0) + 46 + j * 40, t, 'cat', 'middle', false, `${P}.bars.${i}.label`)));
      o.push(`<g${step(b.at)}${sp(`${P}.bars.${i}`)}>${g.join('')}</g>`); });
    const [i, j] = (gap || sig || {}).between || [0, n - 1];
    if (gap) { const ya = Y(V(c.bars[i].v)), yb = Y(V(c.bars[j].v)), xd = ml + pw + 56;
      const g = [L(xs[i] + bw / 2, ya, xd + 14, ya, 'guide'), L(xs[j] + bw / 2, yb, xd + 14, yb, 'guide'), L(xd, ya, xd, yb, 'dim'), L(xd - 10, ya, xd + 10, ya, 'dim'), L(xd - 10, yb, xd + 10, yb, 'dim')];
      gap.text.forEach((t, k) => g.push(T(xd + 26, (ya + yb) / 2 - 8 + k * 40, tx(t), 'dimlab', 'start', true, `${P}.gap.text`)));
      o.push(`<g${step(gap.at)}${sp(`${P}.gap`)}>${g.join('')}</g>`); }
    if (sig) { const tops = c.bars.map(b => Y(V(b.hi || b.v))), yb = Math.min(tops[i], tops[j]) - 64;
      o.push(`<g${step(sig.at)}${sp(`${P}.sig`)} class="sig">` + L(xs[i], yb, xs[j], yb, 'dim') + L(xs[i], yb, xs[i], yb + 14, 'dim') + L(xs[j], yb, xs[j], yb + 14, 'dim') +
        T((xs[i] + xs[j]) / 2, yb - 16, tx(sig.text), 'siglab', 'middle', true, `${P}.sig.text`) + '</g>'); }
    return svg(w, h, o.join(''), 'Bar chart');
  },
  lines(c, w, h, P) {
    const ml = 110, mr = 150, mt = 40, mb = 96, pw = w - ml - mr, ph = h - mt - mb, n = c.x.length;
    const Y = v => mt + ph * (1 - v / c.ymax), inset = Math.max(pw * 0.13, 150), X = i => ml + inset + (pw - 2 * inset) * i / (n - 1), o = [];
    axisY(o, c, ml, mt, pw, ph);
    c.x.forEach((s, i) => o.push(T(X(i), Y(0) + 52, s, 'cat', 'middle', false, `${P}.x.${i}`)));
    c.series.forEach((sr, si) => { const s = sr.s, off = (si - (c.series.length - 1) / 2) * 18, Pt = sr.pts, g = [];
      for (let i = 0; i < n - 1; i++) { const a = [X(i) + off, Y(V(Pt[i].v)), X(i + 1) + off, Y(V(Pt[i + 1].v))]; g.push(L(...a, 'under ' + s), L(...a, 'line ' + s)); }
      Pt.forEach((p, i) => { const x = X(i) + off;
        if (p.lo) g.push(whisker(x, Y(V(p.lo)), Y(V(p.hi)), s, 10));
        g.push(`<circle cx="${x.toFixed(1)}" cy="${Y(V(p.v)).toFixed(1)}" r="11" class="pt ${s}"/>`);
        if (i === 0 || i === n - 1) { const side = i === 0 ? -1 : 1; g.push(T(x + side * 34, Y(V(p.v)) + 11, tx(`{${p.v}}`), 'val ' + s, side < 0 ? 'end' : 'start', true)); } });
      const ym = (Y(V(Pt[0].v)) + Y(V(Pt[n - 1].v))) / 2;
      const above = (sr.pos || 'above') === 'above', tight = sr.label.length * 17 + 60 > X(n - 1) - X(0);  // label wider than the gap between whiskers: move it clear of the intervals
      const ly = tight ? (above ? Math.min(...Pt.map(p => Y(V(p.hi || p.v)))) - 22 : Math.max(...Pt.map(p => Y(V(p.lo || p.v)))) + 46) : ym + (above ? -26 : 62);
      g.push(T((X(0) + X(n - 1)) / 2, ly, sr.label, 'serlab ' + s, 'middle', false, `${P}.series.${si}.label`));
      o.push(`<g${step(sr.at)}${sp(`${P}.series.${si}`)}>${g.join('')}</g>`); });
    return svg(w, h, o.join(''), 'Line chart');
  },
  coef(c, w, h, P) {
    const ml = Math.max(Math.round(w / 3), 500), mr = 250, mt = 14, mb = 96, pw = w - ml - mr, ph = h - mt - mb, lim = c.lim, X = v => ml + pw * (v + lim) / (2 * lim), rh = ph / c.rows.length, o = [];
    for (const t of c.ticks) o.push(L(X(t), mt, X(t), mt + ph, t === 0 ? 'zero' : 'grid'), T(X(t), mt + ph + 38, (t > 0 ? '+' : '') + String(t).replace('-', M), 'tick', 'middle'));
    o.push(T(ml + pw / 2, mt + ph + 82, c.axis, 'axlab', 'middle', false, `${P}.axis`));
    c.rows.forEach((r, i) => { const y = mt + rh * (i + .5), s = r.focal ? 'b' : 'n';
      o.push(`<g${step(r.at)}${sp(`${P}.rows.${i}`)}>` + T(0, y + 10, r.label, 'rowlab ' + s, 'start', false, `${P}.rows.${i}.label`) + L(X(V(r.lo)), y, X(V(r.hi)), y, 'under ' + s) + L(X(V(r.lo)), y, X(V(r.hi)), y, 'ci thick ' + s) +
        `<circle cx="${X(V(r.b)).toFixed(1)}" cy="${y.toFixed(1)}" r="12" class="pt ${s}"/>` + T(w, y + 10, tx(`{${r.b}} ({${r.se}})`), 'val ' + s, 'end', true) + '</g>'); });
    return svg(w, h, o.join(''), 'Coefficient plot');
  }
};
function glyphPair(w, h) {
  const sw = w * 0.56, sh = h * 0.86, o = [];
  for (const [c, x, y] of [['a', 0, 0], ['b', w - sw, h - sh]]) { const px = sw * 0.12, top = y + sh * 0.11;
    o.push(`<g class="sheet ${c}"><rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${sw.toFixed(1)}" height="${sh.toFixed(1)}" class="paper"/>`,
      `<rect x="${(x + px).toFixed(1)}" y="${top.toFixed(1)}" width="${(sw * 0.52).toFixed(1)}" height="${(sh * 0.075).toFixed(1)}" class="name"/>`);
    for (let i = 0; i < 6; i++) o.push(`<rect x="${(x + px).toFixed(1)}" y="${(top + sh * 0.2 + i * sh * 0.105).toFixed(1)}" width="${(sw * (i % 3 !== 2 ? 0.76 : 0.5)).toFixed(1)}" height="${(sh * 0.028).toFixed(1)}" class="row"/>`);
    o.push('</g>'); }
  return `<svg class="glyph" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" aria-hidden="true">${o.join('')}</svg>`;
}
function table(t, P, w) {
  const cell = c => c == null ? '–' : fact(c[0], 'span') + (c.length > 1 ? ` (${fact(c[1], 'span')})` : '');
  return `<table style="--lab:${Math.max(Math.round(w / 3), 500)}px">` + '<thead><tr><th></th>' + t.cols.map((c, k) => `<th class="idx" data-lpath="${P}.cols.${k}">${esc(c)}</th>`).join('') + '</tr></thead><tbody>' +
    t.rows.map((r, i) => `<tr class="${['focal', 'rule'].filter(k => r[k]).join(' ')}"${step(r.at)}${sp(`${P}.rows.${i}`)}><td data-lpath="${P}.rows.${i}.label">${esc(r.label)}</td>` +
      (r.text ? r.text.map(esc) : r.cells.map(cell)).map(c => `<td>${c}</td>`).join('') + '</tr>').join('') + '</tbody></table>';
}
function paperfig(fg, st, k = 8) {
  const [W0, H] = st.slots.paperfig, W = cols(W0, k), im = LX.IMG[fg.src]; if (!im) return `<div class="pf" style="width:${W}px;height:${H}px"></div>`;
  const [cx, cy, cw, ch] = fg.crop || [0, 0, 1, 1], CW = cw * im.w, CH_ = ch * im.h, s0 = Math.min(W / CW, H / CH_), w0 = CW * s0, h0 = CH_ * s0, ox = (W - w0) / 2, oy = (H - h0) / 2;
  let style = `left:${ox.toFixed(1)}px;top:${oy.toFixed(1)}px;width:${w0.toFixed(1)}px;height:${h0.toFixed(1)}px;background-image:var(${im.v});background-size:${(im.w * s0).toFixed(1)}px ${(im.h * s0).toFixed(1)}px;background-position:${(-cx * im.w * s0).toFixed(1)}px ${(-cy * im.h * s0).toFixed(1)}px;`;
  const box = b => `left:${(b[0] * 100).toFixed(2)}%;top:${(b[1] * 100).toFixed(2)}%;width:${(b[2] * 100).toFixed(2)}%;height:${(b[3] * 100).toFixed(2)}%`;
  let kids = (fg.cover || []).map(b => `<div class="cover" style="${box(b)}"></div>`).join(''), zoom = '', scale = s0;
  if (fg.focus) { const [fx, fy, fw, fh] = fg.focus.box, z = Math.min(W / (fw * w0), H / (fh * h0)); scale = s0 * z;
    style += `--zs:${z.toFixed(4)};--zx:${((W - fw * w0 * z) / 2 - ox - fx * w0 * z).toFixed(1)}px;--zy:${((H - fh * h0 * z) / 2 - oy - fy * h0 * z).toFixed(1)}px;--clip:inset(${(fy * 100).toFixed(2)}% ${((1 - fx - fw) * 100).toFixed(2)}% ${((1 - fy - fh) * 100).toFixed(2)}% ${(fx * 100).toFixed(2)}%)`;
    zoom = ` data-zoom="${fg.focus.at || 1}"${sp('figure.focus')}`; kids += `<div class="mark" style="${box(fg.focus.box)}"></div>`; }
  return `<div class="pf" data-asset="figure" style="width:${W}px;height:${H}px" data-source="${esc(fg.source || '')}" data-textpx="${fg.text_px || 0}" data-scale="${scale.toFixed(4)}"><div class="pf-img"${zoom} style="${style}">${kids}</div></div>`;
}
/* A band of bars computed from the deck's own registered numbers: the same talk always gets the same band,
   a different talk a different one. It is an identity mark, not a chart; styles may show it and use it as progress. */
function fingerprint(p) {
  const vals = Object.keys(LX.F).sort().map(k => Math.abs(LX.F[k].value)); if (!vals.length) return '';
  let x = 0, i = 0, o = '';
  while (x < 1920) { const v = vals[i % vals.length], f = (v * 7.31 + i * 0.618) % 1, w = 4 + Math.round(f * 22);
    o += `<rect x="${x}" y="0" width="${w}" height="100" class="fpb${Math.floor(v * 10 + i) % 5 === 0 ? ' on' : ''}${x < p * 1920 ? ' done' : ''}"/>`; x += w + 5 + Math.round(((v * 3.7) % 1) * 9); i++; }
  return `<svg class="fp" viewBox="0 0 1920 100" preserveAspectRatio="none" aria-hidden="true">${o}</svg>`;
}
/* width of a block spanning k of the 12 columns, given the style's 8-column slot width */
const cols = (w8, k) => Math.round((w8 + 32) * k / 8 - 32);
/* per-slide arrangement chosen in the editor: which side the evidence sits, how many columns it takes, where the text sits */
function lay(s, st) {
  const L = s.lay; if (!L || st.fixed_layout) return {k: 8, attr: ''};
  const k = Math.max(5, Math.min(9, L.split || 8)), side = L.side || st.fig_side || 'l', v = [];
  if (s.layout === 'fig' || s.layout === 'paperfig') v.push(side === 'l' ? `--fc:1 / span ${k};--nc:${k + 1} / 13` : `--fc:${13 - k} / 13;--nc:1 / ${13 - k}`);
  if (s.layout === 'flow' || s.layout === 'close') { const a = s.layout === 'flow' ? 4 : 3, r = s.layout === 'flow' ? 8 : 8;
    v.push(side === 'r' ? `--rc:1 / span ${r};--ac:${13 - a} / 13;--aj:end` : `--ac:1 / span ${a};--rc:${13 - r} / 13;--aj:start`); }
  if (L.valign) v.push(`--nv:${L.valign}`);
  return {k: s.layout === 'fig' || s.layout === 'paperfig' ? k : 8, attr: ` style="${v.join(';')}"`, cls: ' lay'};
}
function anchor(st, slot) {
  const a = LX.D.meta.anchor, [w, h] = st.slots[slot]; if (!a) return '';
  if (a.kind === 'pair') return `<div class="asset" data-asset="anchor">${glyphPair(w, h)}</div>`;
  const im = LX.IMG[a.src]; return im ? `<div class="asset" data-asset="anchor"><img class="anchor-img" src="${im.uri}" alt="" style="max-width:${w}px;max-height:${h}px"></div>` : '';
}
function logos(st, n) {
  return (LX.D.meta.logos || []).slice(0, n).map((l, k) => { const im = LX.IMG[st.ground === 'dark' && l.dark ? l.dark : l.file]; return im ? `<img class="logo" data-asset="logo.${k}" src="${im.uri}" alt="${esc(l.alt || '')}">` : ''; }).join('');
}
const el = (tag, x, path, cls) => { const [t, at] = it(x); return `<${tag}${step(at)}${sp(path)}${ed(path)}${cls ? ` class="${cls}"` : ''}>${rich(t)}</${tag}>`; };
const li = (x, path) => { const [t, at] = it(x); return `<li${step(at)}${sp(path)}><span${ed(path)}>${rich(t)}</span></li>`; };
function slide(s, i, n, st) {
  const Lr = s.layout, meta = LX.D.meta, say = s.say ? ` data-say="${esc(s.say)}"` : '';
  if (Lr === 'title') { const lg = logos(st);
    return `<section class="slide L-title" data-i="${i}" data-id="${esc(s.id)}" data-steps="0"${say}><div class="art">${anchor(st, 'glyph_title')}</div><div class="words"><h1${ed('title')}>${rich(s.title)}</h1>` +
      `<p class="sub"${ed('sub')}>${rich(s.sub || '')}</p><p class="by"${ed('by')}>${rich(s.by || '')}</p>${lg ? `<div class="logos">${lg}</div>` : ''}</div>${fingerprint(1)}</section>`; }
  const secs = meta.sections || [], nav = `<nav class="secnav">${secs.map((x, k) => `<span class="${k === s.section ? 'cur' : k < s.section ? 'done' : ''}">${esc(x)}</span>`).join('')}</nav>`;
  const head = `<header>${nav}<h2${ed('title')}>${rich(s.title)}</h2></header>`; let main = '';
  const notes = () => `<div class="notes">${(s.notes || []).map((p, k) => el('p', p, `notes.${k}`)).join('')}`;
  const LY = lay(s, st);
  if (Lr === 'fig') { const c = s.chart, [w0, h] = st.slots[c.kind === 'coef' ? 'coef' : 'fig'], w = cols(w0, LY.k);
    main = `<figure>${CH[c.kind](c, w, h, 'chart')}<figcaption${ed('caption')}>${rich(s.caption || '')}</figcaption></figure>${notes()}</div>`; }
  else if (Lr === 'flow') main = `<div class="anchor">${anchor(st, 'glyph_flow')}</div><div class="right"><ol>${s.steps.map((p, k) => li(p, `steps.${k}`)).join('')}</ol>${s.note ? el('p', s.note, 'note', 'note') : ''}</div>`;
  else if (Lr === 'models') { const [w, h] = st.slots.coef; main = `<figure>${CH.coef(s.chart, w, h, 'chart')}</figure>${table(s.table, 'table', w)}<p class="caption"${ed('caption')}>${rich(s.caption || '')}</p>`; }
  else if (Lr === 'paperfig') main = `<figure>${paperfig(s.figure, st, LY.k)}</figure>${notes()}<p class="caption"><span${ed('caption')}>${rich(s.caption || '')}</span> <span class="credit">Source: ${esc(s.figure.source || '')}.</span></p></div>`;
  else if (Lr === 'close') { const qr = meta.link && LX.IMG.__qr;
    main = `<ol>${s.points.map((p, k) => li(p, `points.${k}`)).join('')}</ol><div class="anchor">${anchor(st, 'glyph_close')}</div><div class="foot"><p class="refs"${ed('refs')}>${rich(s.refs || '')}</p>` +
      (qr ? `<div class="qrbox"><p class="qrnote">${esc(meta.link_note || 'Scan the code to open the paper.')}</p><img class="qr" src="${qr.uri}" alt="QR code: ${esc(meta.link)}"></div>` : '') + '</div>'; }
  else main = `<p>Unknown layout ${esc(Lr)}</p>`;
  const stations = Array.from({length: n}, (_, k) => `<b class="${k < i ? 'done' : k === i ? 'cur' : ''}"></b>`).join('');
  const foot = `<footer><span class="who">${logos(st, 1)}<span class="short"${ed('@meta.short')}>${esc(meta.short || '')}</span></span><span class="citeline">${esc(meta.cite || meta.short || '')}</span>${meta.author || meta.email ? `<span class="byline">${meta.author ? `<span${ed('@meta.author')}>${esc(meta.author)}</span>` : ''}${meta.author && meta.email ? '<span class="sep">\u00a0·\u00a0</span>' : ''}${meta.email ? `<span${ed('@meta.email')}>${esc(meta.email)}</span>` : ''}</span>` : ''}<span class="sec">${esc(secs[s.section] || '')}</span><span class="pg">${i + 1} / ${n}</span></footer><i class="prog" style="--p:${((i + 1) / n).toFixed(4)};--n:${n}">${stations}</i>`;
  const body = `${head}<div class="main">${main}</div>${foot}${fingerprint((i + 1) / n)}`;
  const steps = Math.max(0, ...[...body.matchAll(/data-(?:step|zoom)="(\d+)"/g)].map(m => +m[1]));
  return `<section class="slide L-${Lr}${LY.cls || ''}" data-i="${i}" data-sec="${s.section ?? ''}" data-id="${esc(s.id)}" data-steps="${steps}"${say}${LY.attr}>${body}</section>`;
}
function deckHTML(slug) {
  const st = {...LX.STY[slug]}; st.slots = {...SLOTS, ...(st.slots || {})}; const n = LX.D.slides.length; LX.missing.clear();
  const tok = Object.entries(LX.D.meta.tokens || {}).map(([k, v]) => `${k}:${v}`).join(';');
  return `<div class="deck s-${slug}" data-style="${slug}" style="${esc(tok)}">${patternSheet(slug)}${LX.D.slides.map((s, i) => slide(s, i, n, st)).join('')}</div>`;
}
function applyStep(sl, at) {
  sl.dataset.at = at;
  sl.querySelectorAll('[data-step]').forEach(e => e.classList.toggle('off', +e.dataset.step > at));
  sl.querySelectorAll('[data-zoom]').forEach(e => e.classList.toggle('zoomed', at >= +e.dataset.zoom));
}
