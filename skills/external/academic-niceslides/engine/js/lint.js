/* Deterministic lint over rendered slides (final state, 1:1 scale). Same function for the CLI and the editor. */
function LINT(root) { const out = []; const MIN = 28, FIGMIN = 24;
const lum = c => { const m = c.match(/[\d.]+/g).map(Number); const f = v => { v/=255; return v<=.03928? v/12.92 : Math.pow((v+.055)/1.055,2.4) }; return .2126*f(m[0])+.7152*f(m[1])+.0722*f(m[2]) };
root.querySelectorAll('.slide').forEach((sl, si) => { const id = sl.dataset.id; const R0 = sl.getBoundingClientRect();
  const fail = (rule, msg) => out.push({slide: si+1, id, rule, msg});
  const paper = getComputedStyle(sl).backgroundColor; const fams = new Set(); const isTitle = sl.classList.contains('L-title');
  const h2 = sl.querySelector('h2'); const h2size = h2 ? parseFloat(getComputedStyle(h2).fontSize) : Infinity; const h2top = h2 ? h2.getBoundingClientRect().top : -1; const h2r = h2 ? h2.getBoundingClientRect() : null; const maxLines = (LX.STY[(sl.closest('.deck') || {dataset: {}}).dataset.style] || {}).title_lines || 2;
  const w = document.createTreeWalker(sl, NodeFilter.SHOW_TEXT); let n;
  while (n = w.nextNode()) { const t = n.textContent.trim(); if (!t) continue; const el = n.parentElement; const cs = getComputedStyle(el);
    if (cs.display === 'none' || el.closest('.secnav') && getComputedStyle(el.closest('.secnav')).display === 'none') continue;
    const r = document.createRange(); r.selectNodeContents(n); const b = r.getBoundingClientRect(); if (!b.width) continue;
    let fs = parseFloat(cs.fontSize); const svg = el.closest('svg'); if (svg) fs *= svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
    fams.add(cs.fontFamily.split(',')[0].replace(/"/g,'').trim());
    if (el.closest('.nofact')) { fail('provenance', `unregistered fact ${t}`); continue; }
    if (fs < MIN - .01) fail('min-size', `${fs.toFixed(1)}px < ${MIN}px (14pt): "${t.slice(0,40)}"`);
    if (!isTitle && fs > h2size + .01) fail('giant', `text larger than the title (${fs}px): "${t.slice(0,40)}"`);
    if (b.left < R0.left-1 || b.right > R0.right+1 || b.top < R0.top-1 || b.bottom > R0.bottom+1) fail('overflow', `outside the slide: "${t.slice(0,40)}"`);
    if (h2 && !h2.contains(el) && b.bottom <= h2top + 2 && Math.min(b.right, h2r.right) - Math.max(b.left, h2r.left) > 0) fail('eyebrow', `text above the title: "${t.slice(0,40)}"`);
    if (/\d/.test(t) && !el.closest('[data-fact],.cite,.idx,.tick,.pg,.credit,.citeline,.byline')) fail('provenance', `number without a registered fact: "${t.slice(0,50)}"`);
    const fact = el.closest('[data-fact]'); if (fact && !svg) { const blk = fact.closest('p,li,h1,h2,td,figcaption'); if (blk && fs > parseFloat(getComputedStyle(blk).fontSize)+.01) fail('stat-callout', `number set larger than its sentence: "${t}"`); }
    const col = svg ? cs.fill : cs.color; if (/rgb/.test(col)) { let bgEl = svg ? sl : el, bg = paper; while (bgEl && bgEl !== sl) { const c = getComputedStyle(bgEl).backgroundColor; if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) { bg = c; break; } bgEl = bgEl.parentElement; } const on = cs.getPropertyValue('--on').trim(); if (on) bg = on; const a = lum(col), p = lum(bg); const cr = (Math.max(a,p)+.05)/(Math.min(a,p)+.05); const need = (fs >= 36 || (fs >= 28 && parseInt(cs.fontWeight) >= 600)) ? 3 : 4.5; if (cr < need) fail('contrast', `${cr.toFixed(2)}:1 < ${need}:1 "${t.slice(0,30)}"`); }
  }
  if (fams.size > 1) fail('one-family', `families in use: ${[...fams].join(', ')}`);
  if (h2) { const lines = Math.round(h2.getBoundingClientRect().height / parseFloat(getComputedStyle(h2).lineHeight)); const words = h2.textContent.trim().split(/\s+/).length;
    if (lines > maxLines) fail('title-lines', `title runs to ${lines} lines`); if (words < 6) fail('assertion', `title is not a sentence (${words} words)`); if (/[:：]$/.test(h2.textContent.trim())) fail('assertion', 'title ends in a colon'); }
  sl.querySelectorAll('p,li,figcaption').forEach(e => { if (e.closest('footer')) return; const k = e.textContent.trim().split(/\s+/).length; if (e.textContent.trim() && k < 5) fail('fragment', `block of ${k} words: "${e.textContent.trim()}"`); });
  const blocks = [...sl.querySelectorAll('h1,h2,p,li,figcaption,table,svg,footer,.pf,.logos,.qr')].filter(e => !e.parentElement.closest('p,li,figcaption,table,svg,footer') && e.getBoundingClientRect().width);
  for (let i = 0; i < blocks.length; i++) for (let j = i+1; j < blocks.length; j++) { const a = blocks[i].getBoundingClientRect(), b = blocks[j].getBoundingClientRect();
    const ox = Math.min(a.right,b.right)-Math.max(a.left,b.left), oy = Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
    if (ox > 4 && oy > 4) fail('overlap', `<${blocks[i].tagName.toLowerCase()}> overlaps <${blocks[j].tagName.toLowerCase()}> by ${oy.toFixed(0)}px`); }
  blocks.forEach(e => { const b = e.getBoundingClientRect(); if (b.bottom > R0.bottom+1 || b.right > R0.right+1) fail('overflow', `<${e.tagName.toLowerCase()}> leaves the slide`); });
  sl.querySelectorAll('svg.chart text').forEach((a, i, all) => { const A = a.getBoundingClientRect(); for (let j = i+1; j < all.length; j++) { const B = all[j].getBoundingClientRect();
    if (Math.min(A.right,B.right)-Math.max(A.left,B.left) > 2 && Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top) > 6) fail('label-collision', `"${a.textContent}" × "${all[j].textContent}"`); } });
  const st = new Set([...sl.querySelectorAll('[data-step],[data-zoom]')].map(e => +(e.dataset.step || e.dataset.zoom)));
  for (let k = 1; k <= +sl.dataset.steps; k++) if (!st.has(k)) fail('step-gap', `no element appears on click ${k}`);
  if (+sl.dataset.steps > 4) fail('too-many-clicks', `${sl.dataset.steps} clicks on one slide; split it`);
  sl.querySelectorAll('img.logo').forEach(im => { const b = im.getBoundingClientRect(); const inFoot = !!im.closest('footer');
    if (!inFoot && !im.closest('.logos')) fail('logo-place', 'logo outside the title block and footer');
    if (b.height > (inFoot ? 48 : 96) + .5) fail('logo-size', `logo ${b.height.toFixed(0)}px tall`);
    if (im.naturalWidth && Math.abs(b.width/b.height - im.naturalWidth/im.naturalHeight) > .02*im.naturalWidth/im.naturalHeight) fail('logo-stretch', 'logo aspect ratio changed'); });
  sl.querySelectorAll('.pf').forEach(pf => { if (!pf.dataset.source) fail('figure-credit', 'paper figure without a source');
    const px = +pf.dataset.textpx * +pf.dataset.scale; if (!+pf.dataset.textpx) fail('figure-legible', 'text_px not declared for the figure');
    else if (px < FIGMIN - .01) fail('figure-legible', `smallest figure text renders at ${px.toFixed(1)}px < ${FIGMIN}px (12pt): crop or zoom further`); });
}); return out; }
