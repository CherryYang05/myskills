/* Editor. Every edit is a patch to the deck JSON followed by a re-render; the page is never the source. */
const ED = {undo: [], redo: [], prev: 99, last: null, timer: 0};
const getP = (o, p) => p.split('.').reduce((a, k) => a == null ? a : a[k], o);
const setP = (o, p, v) => { const ks = p.split('.'), k = ks.pop(); ks.reduce((a, x) => a[x], o)[k] = v; };
const target = p => p.startsWith('@meta.') ? [LX.D.meta, p.slice(6)] : [LX.D.slides[ST.i], p];
const getText = p => { const [o, q] = target(p), v = getP(o, q); return v == null ? '' : typeof v === 'string' ? v : v.t; };
const setText = (p, t) => { const [o, q] = target(p), v = getP(o, q); if (v && typeof v === 'object') v.t = t; else setP(o, q, t); };
const getAt = p => { const v = getP(LX.D.slides[ST.i], p); return v && typeof v === 'object' ? (v.at || 0) : 0; };
const setAt = (p, n) => { const s = LX.D.slides[ST.i], v = getP(s, p); if (typeof v === 'string') setP(s, p, {t: v, at: n}); else v.at = n; };
function commit(fn) { ED.redo = []; ED.undo.push(JSON.stringify(LX.D)); if (ED.undo.length > 80) ED.undo.shift(); fn(); ED.dirty = true; redraw(); }
const plain = t => String(t || '').replace(/\{(\w+)\}/g, (_, k) => LX.F[k] ? LX.F[k].text : k).replace(/\[[abcems]\|([^\]]+)\]/g, '$1');
function describe(p) {
  const s = LX.D.slides[ST.i], v = getP(s, p), cut = t => t.length > 34 ? t.slice(0, 33) + '…' : t;
  if (p === 'chart.gap') return '差值标注（尺寸线）'; if (p === 'chart.sig') return '显著性标注'; if (p === 'figure.focus') return '放大到焦点区域';
  if (/^chart\.bars/.test(p)) return '柱 · ' + (v.label || []).join(' '); if (/^chart\.series/.test(p)) return '折线 · ' + v.label;
  if (/^chart\.rows/.test(p)) return '系数 · ' + v.label; if (/^table\.rows/.test(p)) return '表格行 · ' + v.label;
  return '文字 · ' + cut(plain(getText(p)));
}
function edit() {
  ST.mode = 'edit'; document.body.className = 'edit'; if (ED.prev == null) ED.prev = 99;
  ui.innerHTML = `<div class="e-top"><b>academic_niceslides 编辑</b><button data-a="present">放映</button><button data-a="gallery">全部风格</button><button data-a="undo">撤销</button><button data-a="redo">重做</button>
<span class="e-sp"></span><span class="e-lint"></span><button data-a="html" class="pri">保存为 HTML</button><button data-a="json">导出 deck.json</button><button data-a="copy">复制 JSON</button><button data-a="pdf">打印成 PDF</button></div>
<aside class="e-list"></aside><aside class="e-insp"></aside><div class="e-scrub"></div><div id="e-tb"></div><div id="e-gut"><i></i></div><div id="lx-lintbox"></div>`;
  $('.e-top').onclick = e => { const a = e.target.dataset.a; if (!a) return;
    if (a === 'present') present(ST.i, 0); else if (a === 'gallery') gallery();
    else if (a === 'undo') { if (ED.undo.length) { ED.redo.push(JSON.stringify(LX.D)); LX.D = JSON.parse(ED.undo.pop()); redraw(); } }
    else if (a === 'redo') { if (ED.redo.length) { ED.undo.push(JSON.stringify(LX.D)); LX.D = JSON.parse(ED.redo.pop()); redraw(); } }
    else if (a === 'html') save(LX.D.meta.short.replace(/[^\w一-鿿]+/g, '-') + '.html', fileHTML(), 'text/html');
    else if (a === 'json') save('deck.json', deckJSON(), 'application/json');
    else if (a === 'copy') navigator.clipboard.writeText(deckJSON()).then(() => toast('已复制 deck.json 的内容'), () => toast('浏览器拒绝了复制'));
    else if (a === 'pdf') { staticMode('expand'); setTimeout(() => { try { print(); } catch (_) {} edit(); }, 300); } };
  redraw();
}
function save(name, text, type) {
  try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], {type})); a.download = name; document.body.appendChild(a); a.click(); a.remove(); ED.dirty = false;
    toast('已保存 ' + name + '。如果没有开始下载，请用“复制 JSON”。'); } catch (_) { toast('这个环境不能下载文件，请用“复制 JSON”。'); }
}
function fileHTML() {
  const imgs = {}; for (const k in DATA.images) { const {uri, w, h} = DATA.images[k]; imgs[k] = {uri, w, h}; }
  const data = JSON.stringify({...DATA, deck: LX.D, images: imgs, open: 'present'}).replace(/</g, '\\u003c');
  const styles = $$('head style').filter(s => !s.dataset.rt).map(s => s.outerHTML).join('');
  const scripts = $$('script[data-keep]').map(s => `<script data-keep>${s.textContent}<\/script>`).join('');
  return `<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(LX.D.meta.short || 'Deck')}</title>${styles}</head><body><script id="lectern-data" type="application/json">${data}<\/script><div id="stage"></div><div id="ui"></div>${scripts}</body></html>`;
}
function redraw() {
  ED.editing = null; hideTB();
  const n = LX.D.slides.length; ST.i = Math.max(0, Math.min(ST.i, n - 1)); const s = LX.D.slides[ST.i];
  stage.innerHTML = deckHTML(ST.style); const S = $$('.slide', stage); S.forEach((x, k) => x.classList.toggle('cur', k === ST.i));
  const cur = S[ST.i], steps = +cur.dataset.steps, at = Math.min(ED.prev, steps); applyStep(cur, at);
  const fit = () => document.body.style.setProperty('--fit', Math.min((innerWidth - 640) / 1920, (innerHeight - 150) / 1080)); fit(); onresize = () => ST.mode === 'edit' && fit();
  // slide list
  $('.e-list').innerHTML = LX.D.slides.map((x, k) => `<div class="e-item${k === ST.i ? ' on' : ''}" data-k="${k}"><i>${k + 1}</i><span>${esc(plain(x.title))}</span>
<em><button data-m="up" title="上移">↑</button><button data-m="down" title="下移">↓</button><button data-m="dup" title="复制这一页">⧉</button><button data-m="del" title="删除这一页">✕</button></em></div>`).join('');
  $('.e-list').onclick = e => { const it = e.target.closest('.e-item'); if (!it) return; const k = +it.dataset.k, m = e.target.dataset.m, A = LX.D.slides;
    if (!m) { ST.i = k; ED.prev = 99; return redraw(); }
    commit(() => { if (m === 'up' && k > 0) { [A[k - 1], A[k]] = [A[k], A[k - 1]]; ST.i = k - 1; } else if (m === 'down' && k < A.length - 1) { [A[k + 1], A[k]] = [A[k], A[k + 1]]; ST.i = k + 1; }
      else if (m === 'dup') { const c = JSON.parse(JSON.stringify(A[k])); c.id += '-copy'; A.splice(k + 1, 0, c); ST.i = k + 1; } else if (m === 'del' && A.length > 1) { A.splice(k, 1); ST.i = Math.min(k, A.length - 1); } }); };
  // step scrubber
  $('.e-scrub').innerHTML = `<span>预览第几次点击：</span>` + Array.from({length: steps + 1}, (_, k) => `<button data-k="${k}" class="${k === at ? 'on' : ''}">${k === 0 ? '刚翻到这页' : '点击 ' + k}</button>`).join('');
  $('.e-scrub').onclick = e => { if (e.target.dataset.k != null) { ED.prev = +e.target.dataset.k; redraw(); } };
  // inspector
  const paths = [...new Set($$('[data-sp]', cur).map(e => e.dataset.sp))];
  const stepRows = paths.map(p => `<div class="e-step" data-p="${p}"><span>${esc(describe(p))}</span><button data-d="-1">−</button><b>${getAt(p) || '随页'}</b><button data-d="1">+</button></div>`).join('');
  const tk = LX.D.meta.tokens || {};
  $('.e-insp').innerHTML = `<details open><summary>出现顺序</summary><p class="e-hint">每一项在第几次点击时出现。“随页”表示翻到这页就在。把鼠标放在一行上，页面里对应的元素会被框出来。</p>${stepRows || '<p class="e-hint">这一页没有可分步的元素。</p>'}
${s.layout === 'paperfig' ? '<button class="e-fig">调整原图的裁切和放大区域</button>' : ''}${s.chart && s.chart.kind === 'bars' ? `<p class="e-row"><button class="e-gap">${s.chart.gap ? '移除' : '添加'}差值标注</button><button class="e-sig">${s.chart.sig ? '移除' : '添加'}显著性标注</button></p>` : ''}</details>
${identityPanel()}${layoutPanel(s)}<details open><summary>风格</summary><label>整套风格<select class="e-style">${ORDER.map(k => `<option value="${k}"${k === ST.style ? ' selected' : ''}>${esc(LX.STY[k].cn)} · ${esc(LX.STY[k].en)}</option>`).join('')}</select></label>
<label class="e-col">对照系列的颜色<input type="color" data-t="--a" value="${tk['--a'] || hex(cur, '--a')}"><i>${tk['--a'] ? '已自定义' : '风格默认'}</i></label>
<label class="e-col">焦点系列的颜色<input type="color" data-t="--b" value="${tk['--b'] || hex(cur, '--b')}"><i>${tk['--b'] ? '已自定义' : '风格默认'}</i></label>
<button class="e-tokreset">颜色恢复为风格默认</button><p class="e-hint">颜色改动对全稿生效，对比度不够时下面的检查会报出来。</p></details>
<details><summary>插入数字</summary><p class="e-hint">页面上的数字只能来自这张表。先点一下要改的文字，再点这里的一行。</p><input class="e-ff" placeholder="筛选，例如 rate 或 3.2"><div class="e-facts"></div></details>
<details><summary>讲稿（这一页要说的话）</summary><textarea class="e-say" rows="5">${esc(s.say || '')}</textarea></details>
<details><summary>本页全部字段</summary><p class="e-hint">图表的标签、坐标范围、刻度等都在这里。改完按 Tab 或点别处生效。</p><div class="e-form">${form(s, '')}</div></details>
<details open><summary>检查</summary><div class="e-lintlist"></div></details>`;
  const insp = $('.e-insp');
  $$('.e-step', insp).forEach(r => { const p = r.dataset.p, hl = on => $$(`[data-sp="${p}"]`, cur).forEach(e => e.classList.toggle('e-hl', on));
    r.onmouseenter = () => hl(true); r.onmouseleave = () => hl(false);
    r.onclick = e => { const d = +e.target.dataset.d; if (!d) return; const v = Math.max(0, Math.min(6, getAt(p) + d)); commit(() => { setAt(p, v); ED.prev = 99; }); }; });
  $('.e-style', insp).onchange = e => { ST.style = e.target.value; commit(() => { LX.D.meta.style = ST.style; }); };
  $$('.e-col input', insp).forEach(i => i.onchange = () => commit(() => { (LX.D.meta.tokens ||= {})[i.dataset.t] = i.value; }));
  $('.e-tokreset', insp).onclick = () => commit(() => { delete LX.D.meta.tokens; });
  $('.e-say', insp).onchange = e => commit(() => { s.say = e.target.value; });
  const ff = $('.e-ff', insp), drawFacts = () => { const q = ff.value.toLowerCase();
    $('.e-facts', insp).innerHTML = Object.entries(LX.F).filter(([k, f]) => !q || k.toLowerCase().includes(q) || f.text.includes(q)).slice(0, 60)
      .map(([k, f]) => `<button data-k="${k}" title="${esc(f.how)}"><b>${esc(f.text)}</b><code>{${k}}</code><span>${esc(f.how)}</span></button>`).join(''); };
  ff.oninput = drawFacts; drawFacts();
  $('.e-facts', insp).onmousedown = e => { const b = e.target.closest('button'); if (!b) return; e.preventDefault(); const tok = `{${b.dataset.k}}`, f = ED.last;
    if (f && document.contains(f)) { if (f.isContentEditable) document.execCommand('insertText', false, tok); else { f.setRangeText(tok, f.selectionStart, f.selectionEnd, 'end'); } }
    else navigator.clipboard.writeText(tok).then(() => toast('已复制 ' + tok), () => {}); };
  $$('.e-form [data-f]', insp).forEach(f => { f.onfocus = () => ED.last = f; f.onchange = () => commit(() => { const old = getP(s, f.dataset.f);
    setP(s, f.dataset.f, f.type === 'checkbox' ? f.checked : typeof old === 'number' ? +f.value : Array.isArray(old) ? f.value.split(',').map(x => isNaN(+x) || x.trim() === '' ? x.trim() : +x) : f.value); }); });
  const fb = $('.e-fig', insp); if (fb) fb.onclick = figureEditor;
  bindPanels(insp, s);
  const gb = $('.e-gap', insp), sb = $('.e-sig', insp), nx = () => Math.min(4, +cur.dataset.steps + 1);
  if (gb) gb.onclick = () => commit(() => { if (s.chart.gap) delete s.chart.gap; else s.chart.gap = {text: ['difference between', 'the two groups'], at: nx()}; ED.prev = 99; });
  if (sb) sb.onclick = () => commit(() => { if (s.chart.sig) delete s.chart.sig; else s.chart.sig = {text: 'test result: insert a registered number', at: nx()}; ED.prev = 99; });
  bindStage(cur, s);
  clearTimeout(ED.timer); ED.timer = setTimeout(runLint, 250);
}
function form(o, base) {
  return Object.entries(o).map(([k, v]) => { const p = base ? base + '.' + k : k;
    if (v == null) return ''; if (typeof v === 'boolean') return `<label class="e-f"><span>${k}</span><input type="checkbox" data-f="${p}"${v ? ' checked' : ''}></label>`;
    if (typeof v === 'number') return `<label class="e-f"><span>${k}</span><input type="number" step="any" data-f="${p}" value="${v}"></label>`;
    if (typeof v === 'string') return `<label class="e-f"><span>${k}</span><textarea rows="${Math.min(4, Math.ceil(v.length / 34) || 1)}" data-f="${p}">${esc(v)}</textarea></label>`;
    if (Array.isArray(v) && v.every(x => x == null || typeof x !== 'object')) return `<label class="e-f"><span>${k}</span><input data-f="${p}" value="${esc(v.join(', '))}"></label>`;
    return `<details class="e-sub"><summary>${k}</summary>${form(v, p)}</details>`; }).join('');
}
function runLint() {
  const box = $('#lx-lintbox'); if (!box) return; box.innerHTML = deckHTML(ST.style); $$('.slide', box).forEach(s => applyStep(s, +s.dataset.steps));
  document.fonts.ready.then(() => { const res = LINT(box); box.innerHTML = ''; const badge = $('.e-lint'), list = $('.e-lintlist'); if (!badge) return;
    badge.textContent = res.length ? `检查：${res.length} 项未过` : '检查：全部通过'; badge.className = 'e-lint ' + (res.length ? 'bad' : 'ok');
    list.innerHTML = res.length ? res.map(r => `<button data-k="${r.slide - 1}"><b>第 ${r.slide} 页 · ${r.rule}</b><span>${esc(r.msg)}</span></button>`).join('') : '<p class="e-hint">当前风格下没有问题。交付前换几种风格各看一眼。</p>';
    list.onclick = e => { const b = e.target.closest('button'); if (b) { ST.i = +b.dataset.k; ED.prev = 99; redraw(); } }; });
}
function figureEditor() {
  const s = LX.D.slides[ST.i], fg = s.figure, im = LX.IMG[fg.src], crop = [...(fg.crop || [0, 0, 1, 1])];
  const fo = fg.focus ? fg.focus.box : [0.25, 0.25, 0.5, 0.5], foc = [crop[0] + fo[0] * crop[2], crop[1] + fo[1] * crop[3], fo[2] * crop[2], fo[3] * crop[3]];
  const W = Math.min(innerWidth - 120, 1000, (innerHeight - 220) * im.w / im.h), H = W * im.h / im.w, m = document.createElement('div'); m.className = 'e-modal';
  m.innerHTML = `<div class="e-box"><p><b>原图的裁切和放大区域</b>　实线框是页面上显示的范围，虚线框是点击后放大到的范围。拖动框移动，拖右下角改大小。原图本身不会被改动。</p>
<div class="e-canvas" style="width:${W}px;height:${H}px;background-image:url(${im.uri})"><div class="e-rect crop"><i></i></div><div class="e-rect focus"><i></i></div></div>
<p><label><input type="checkbox" class="e-usef"${fg.focus ? ' checked' : ''}> 点击后放大到虚线框</label><span class="e-sp"></span><button data-a="cancel">取消</button><button data-a="ok" class="pri">完成</button></p></div>`;
  document.body.appendChild(m);
  const bind = (cls, b) => { const r = $('.' + cls, m), put = () => Object.assign(r.style, {left: b[0] * W + 'px', top: b[1] * H + 'px', width: b[2] * W + 'px', height: b[3] * H + 'px'}); put();
    r.onpointerdown = e => { e.preventDefault(); r.setPointerCapture(e.pointerId); const rs = e.target.tagName === 'I', x0 = e.clientX, y0 = e.clientY, b0 = [...b];
      r.onpointermove = ev => { const dx = (ev.clientX - x0) / W, dy = (ev.clientY - y0) / H;
        if (rs) { b[2] = Math.max(.05, Math.min(1 - b0[0], b0[2] + dx)); b[3] = Math.max(.05, Math.min(1 - b0[1], b0[3] + dy)); }
        else { b[0] = Math.max(0, Math.min(1 - b0[2], b0[0] + dx)); b[1] = Math.max(0, Math.min(1 - b0[3], b0[1] + dy)); } put(); };
      r.onpointerup = () => { r.onpointermove = null; }; }; };
  bind('crop', crop); bind('focus', foc);
  const uf = $('.e-usef', m), tog = () => $('.focus', m).style.display = uf.checked ? '' : 'none'; uf.onchange = tog; tog();
  m.onclick = e => { const a = e.target.dataset.a; if (!a) return; m.remove(); if (a !== 'ok') return;
    commit(() => { const r4 = v => +v.toFixed(4); fg.crop = crop.map(r4);
      if (uf.checked) { const x0 = Math.max(crop[0], foc[0]), y0 = Math.max(crop[1], foc[1]), x1 = Math.min(crop[0] + crop[2], foc[0] + foc[2]), y1 = Math.min(crop[1] + crop[3], foc[1] + foc[3]);
        fg.focus = {box: [(x0 - crop[0]) / crop[2], (y0 - crop[1]) / crop[3], Math.max(.05, (x1 - x0) / crop[2]), Math.max(.05, (y1 - y0) / crop[3])].map(r4), at: (fg.focus && fg.focus.at) || 1}; }
      else delete fg.focus; ED.prev = 99; }); };
}
addEventListener('beforeunload', e => { if (ED.dirty) { e.preventDefault(); e.returnValue = ''; } });
/* ===================== Slides-like editing on the page ===================== */
const KINDS = [['s', '加粗'], ['a', '对照系列色'], ['b', '焦点系列色'], ['e', '强调色'], ['m', '次要灰']];
const LISTP = p => { const m = /^(notes|steps|points)\.(\d+)$/.exec(p); return m && [m[1], +m[2]]; };
function hideTB() { const t = $('#e-tb'); if (t) { t.style.display = 'none'; t.innerHTML = ''; t.className = ''; } $$('.e-sel').forEach(e => e.classList.remove('e-sel')); }
function placeTB(r) { const tb = $('#e-tb'); tb.style.display = 'flex'; const w = tb.offsetWidth, h = tb.offsetHeight;
  let x = r.left + r.width / 2 - w / 2, y = r.top - h - 12; if (y < 56) y = r.bottom + 12; if (y + h > innerHeight - 50) y = Math.max(56, r.top + 8);
  tb.style.left = Math.max(236, Math.min(innerWidth - 356 - w, x)) + 'px'; tb.style.top = y + 'px'; }
const swatch = (cur, k) => { const v = k === 's' ? '' : getComputedStyle(cur.querySelector('.deck') ? cur : cur).getPropertyValue(k === 'm' ? '--mute' : k === 'e' ? '--e' : (k === 'a' ? '--a' : '--b')).trim();
  return v || getComputedStyle(cur).getPropertyValue('--ink').trim(); };
function hex(el, v) { const c = getComputedStyle(el).getPropertyValue(v).trim(); if (/^#[0-9a-f]{6}$/i.test(c)) return c;
  const m = c.match(/[\d.]+/g); return m ? '#' + m.slice(0, 3).map(x => (+x).toString(16).padStart(2, '0')).join('') : '#000000'; }
function deckJSON() { const D = JSON.parse(JSON.stringify(LX.D)), used = [...new Set(JSON.stringify(D).match(/upload\/[\w.-]+/g) || [])];
  if (used.length) D.uploads = Object.fromEntries(used.filter(k => LX.IMG[k]).map(k => [k, LX.IMG[k].uri])); return JSON.stringify(D, null, 1); }
function pickImage(cb) { const i = document.createElement('input'); i.type = 'file'; i.accept = 'image/*';
  i.onchange = () => { const f = i.files[0]; if (!f) return; const rd = new FileReader();
    rd.onload = () => { const im = new Image(); im.onload = () => { const key = 'upload/' + Date.now().toString(36) + '-' + f.name.replace(/[^\w.-]+/g, '_');
      LX.IMG[key] = {uri: rd.result, w: im.naturalWidth || 300, h: im.naturalHeight || 100, v: '--img' + Object.keys(LX.IMG).length};
      document.documentElement.style.setProperty(LX.IMG[key].v, `url(${rd.result})`); cb(key, LX.IMG[key]); }; im.src = rd.result; };
    rd.readAsDataURL(f); };
  i.click(); }
/* markup <-> page: the page shows formatted text; on leaving, the DOM is turned back into deck markup */
function ser(n) { let o = '';
  for (const c of n.childNodes) {
    if (c.nodeType === 3) { o += c.textContent.replace(/[\[\]|]/g, ''); continue; } if (c.nodeType !== 1) continue;
    if (c.dataset.fact) o += `{${c.dataset.fact}}`; else if (c.classList.contains('cite')) o += `[c|${c.textContent}]`;
    else if (c.classList.contains('k')) { const k = ['s', 'a', 'b', 'e', 'm'].find(x => c.classList.contains(x)), t = ser(c); o += t.trim() && k ? `[${k}|${t}]` : t; }
    else if (c.tagName === 'BR') o += ' '; else o += ser(c); }
  return o; }
function fmt(elm, kind) {
  const sel = getSelection(); if (!sel.rangeCount) return; const r = sel.getRangeAt(0); if (!elm.contains(r.commonAncestorContainer)) return;
  const kOf = n => { const e = (n.nodeType === 1 ? n : n.parentElement).closest('.k'); return e && elm.contains(e) && e !== elm ? e : null; };
  const ks = kOf(r.startContainer), ke = kOf(r.endContainer); if (ks) r.setStartBefore(ks); if (ke) r.setEndAfter(ke);
  if (r.collapsed) return toast('先选中要改的文字');
  const probe = r.cloneContents(); if (probe.querySelector('.cite')) return toast('文献引用保持原样，不能再加格式');
  const frag = r.extractContents(); frag.querySelectorAll('.k').forEach(x => x.replaceWith(...x.childNodes));
  let node = frag; if (kind !== 'clear') { node = document.createElement(kind === 's' ? 'strong' : 'span'); node.className = 'k ' + kind; node.appendChild(frag); }
  const last = node.nodeType === 11 ? node.lastChild : node; r.insertNode(node); sel.removeAllRanges(); const nr = document.createRange();
  if (last && last.parentNode) { nr.setStartAfter(last); nr.collapse(true); sel.addRange(nr); } ED.range = nr.cloneRange(); }
function insertFact(k) {
  const elm = ED.editing; if (!elm) return; elm.focus(); const sel = getSelection(); sel.removeAllRanges(); let r = ED.range;
  if (!r || !elm.contains(r.commonAncestorContainer)) { r = document.createRange(); r.selectNodeContents(elm); r.collapse(false); }
  sel.addRange(r); const sp = document.createElement('span'); sp.dataset.fact = k; sp.contentEditable = 'false'; sp.textContent = LX.F[k].text.replace(/-/g, M);
  r.deleteContents(); r.insertNode(sp); r.setStartAfter(sp); r.collapse(true); sel.removeAllRanges(); sel.addRange(r); ED.range = r.cloneRange(); }
function factPicker(onPick) {
  return `<div class="e-fp"><input class="e-fpq" placeholder="找数字：rate、3.2、gap…"><div class="e-fpl"></div></div>`; }
function bindFactPicker(root, onPick) { const q = $('.e-fpq', root), L = $('.e-fpl', root), draw = () => { const v = q.value.toLowerCase();
    L.innerHTML = Object.entries(LX.F).filter(([k, f]) => !v || k.toLowerCase().includes(v) || f.text.includes(v) || f.how.toLowerCase().includes(v)).slice(0, 40)
      .map(([k, f]) => `<button data-k="${k}"><b>${esc(f.text)}</b><span>${esc(f.how)}</span></button>`).join(''); };
  q.oninput = draw; draw(); L.onmousedown = e => { const b = e.target.closest('button'); if (b) { e.preventDefault(); onPick(b.dataset.k); } }; }
/* finishing an edit: any press outside the text being edited and its toolbar */
addEventListener('pointerdown', e => { if (ST.mode !== 'edit' || !ED.editing) return; if (ED.editing.contains(e.target) || e.target.closest('#e-tb')) return;
  const tp = e.target.closest('#stage [data-path]'); finishText(true);
  if (tp) { const n = $(`#stage .slide.cur [data-path="${tp.dataset.path}"]`); if (n) { e.preventDefault(); editText(n, {clientX: e.clientX, clientY: e.clientY}); } } }, true);
document.addEventListener('selectionchange', () => { const el = ED.editing, sel = getSelection(); if (el && sel.rangeCount && el.contains(sel.getRangeAt(0).commonAncestorContainer)) ED.range = sel.getRangeAt(0).cloneRange(); });
function finishText(keep, then) { const elm = ED.editing; if (!elm) return; ED.editing = null; const p = elm.dataset.path, src = getText(p);
  const t = ser(elm).replace(/\s+/g, ' ').trim();
  if (then) return commit(() => { if (keep && t !== src) setText(p, t); then(); });
  if (keep && t !== src) commit(() => setText(p, t)); else redraw(); }
function editText(elm, ev) {
  if (ED.editing === elm) return; const cur = elm.closest('.slide'), p = elm.dataset.path, lst = LISTP(p);
  hideTB(); ED.editing = elm; elm.contentEditable = 'true'; elm.classList.add('e-editing'); $$('[data-fact],.cite', elm).forEach(f => f.contentEditable = 'false');
  elm.focus(); const sel = getSelection(); let r = ev && document.caretRangeFromPoint ? document.caretRangeFromPoint(ev.clientX, ev.clientY) : null;
  if (!r || !elm.contains(r.startContainer)) { r = document.createRange(); r.selectNodeContents(elm); r.collapse(false); } sel.removeAllRanges(); sel.addRange(r); ED.range = r.cloneRange();
  const tb = $('#e-tb'); tb.className = 'txt';
  tb.innerHTML = KINDS.map(([k, n]) => `<button data-f="${k}" title="${n}" class="sw${k === 's' ? ' bold' : ''}"${k === 's' ? '' : ` style="--c:${swatch(cur, k)}"`}>${k === 's' ? 'B' : ''}</button>`).join('') +
    `<label class="e-pick" title="改强调色（全稿）"><input type="color" value="${(LX.D.meta.tokens || {})['--e'] || '#7a3cff'}"></label><button data-f="clear" title="清除格式">清除</button><i class="e-div"></i><button data-f="num">插入数字</button>` +
    (lst ? `<i class="e-div"></i><button data-f="up" title="上移">↑</button><button data-f="down" title="下移">↓</button><button data-f="add" title="在下面加一段">＋</button><button data-f="dup" title="复制这一段">⧉</button><button data-f="del" title="删除这一段">✕</button>` : '') +
    `<div class="e-tbx"></div>`;
  placeTB(elm.getBoundingClientRect());
  tb.onmousedown = e => { if (!e.target.closest('input')) e.preventDefault(); };
  $('.e-pick input', tb).onchange = e => { const v = e.target.value; finishText(true, () => { (LX.D.meta.tokens ||= {})['--e'] = v; }); };
  tb.onclick = e => { const b = e.target.closest('[data-f]'); if (!b) return; const f = b.dataset.f;
    if (KINDS.some(([k]) => k === f) || f === 'clear') return fmt(elm, f);
    if (f === 'num') { const x = $('.e-tbx', tb); if (x.innerHTML) { x.innerHTML = ''; return; } x.innerHTML = factPicker(); bindFactPicker(x, k => insertFact(k)); $('.e-fpq', x).focus(); placeTB(elm.getBoundingClientRect()); return; }
    const [arr, k] = lst, s = LX.D.slides[ST.i];
    finishText(true, () => { const A = s[arr];
      if (f === 'up' && k > 0) [A[k - 1], A[k]] = [A[k], A[k - 1]]; else if (f === 'down' && k < A.length - 1) [A[k + 1], A[k]] = [A[k], A[k + 1]];
      else if (f === 'dup') A.splice(k + 1, 0, JSON.parse(JSON.stringify(A[k]))); else if (f === 'add') A.splice(k + 1, 0, {t: 'New paragraph: write a complete sentence here.', at: (A[k] && A[k].at) || 0});
      else if (f === 'del') { if (A.length > 1 || arr === 'notes') A.splice(k, 1); else toast('至少保留一项'); } ED.prev = 99; }); };
  elm.onkeydown = k => { if (k.key === 'Enter') { k.preventDefault(); finishText(true); } else if (k.key === 'Escape') finishText(false);
    else if ((k.metaKey || k.ctrlKey) && k.key.toLowerCase() === 'b') { k.preventDefault(); fmt(elm, 's'); }
    else if ((k.metaKey || k.ctrlKey) && ['i', 'u'].includes(k.key.toLowerCase())) k.preventDefault(); };
  elm.onpaste = e => { e.preventDefault(); document.execCommand('insertText', false, (e.clipboardData.getData('text/plain') || '').replace(/\s+/g, ' ')); };
}
/* labels inside charts and tables: a small field over the label */
function editLabel(node) {
  const p = node.dataset.lpath, s = LX.D.slides[ST.i], v = getP(s, p), arr = Array.isArray(v), tb = $('#e-tb'); hideTB(); node.classList.add('e-sel');
  tb.className = 'lbl'; tb.innerHTML = `<input class="e-lin" value="${esc(arr ? v.join(' / ') : v)}"><button data-f="ok" class="pri">好</button><button data-f="num">插入数字</button>
<p class="e-hint">${arr ? '用 “ / ” 分行。' : ''}数字只能从“插入数字”里选，会写成 {名字}。</p><div class="e-tbx"></div>`;
  placeTB(node.getBoundingClientRect()); const inp = $('.e-lin', tb); inp.focus(); inp.select();
  const done = () => { const t = inp.value.trim(); if (!t) return hideTB(); commit(() => setP(s, p, arr ? t.split(/\s*\/\s*/) : t)); };
  inp.onkeydown = e => { if (e.key === 'Enter') done(); if (e.key === 'Escape') hideTB(); };
  tb.onclick = e => { const f = (e.target.closest('[data-f]') || {}).dataset?.f; if (f === 'ok') done();
    if (f === 'num') { const x = $('.e-tbx', tb); x.innerHTML = factPicker(); bindFactPicker(x, k => { inp.setRangeText(`{${k}}`, inp.selectionStart, inp.selectionEnd, 'end'); inp.focus(); }); placeTB(node.getBoundingClientRect()); } };
  tb.onmousedown = null;
}
/* images: logos, the recurring anchor, paper figures */
function assetTB(node) {
  const a = node.dataset.asset, s = LX.D.slides[ST.i], m = LX.D.meta, tb = $('#e-tb'); hideTB(); const box = node.classList.contains('asset') ? node.firstElementChild : node; box.classList.add('e-sel'); tb.className = 'img';
  if (a.startsWith('logo.')) { const k = +a.split('.')[1], l = m.logos[k];
    tb.innerHTML = `<b>Logo ${k + 1}</b><button data-f="rep">换一张图片</button><button data-f="dark">${l.dark ? '换' : '加'}深色背景用的版本</button>${k ? '<button data-f="first">放到最前</button>' : ''}<button data-f="add">再加一个 logo</button><button data-f="del">删除</button>
<p class="e-hint">页脚只放第一个 logo，扉页放全部。图片不会被拉伸或改色。</p>`;
    tb.onclick = e => { const f = (e.target.closest('[data-f]') || {}).dataset?.f; if (!f) return;
      if (f === 'rep') pickImage(key => commit(() => { l.file = key; delete l.dark; }));
      if (f === 'dark') pickImage(key => commit(() => { l.dark = key; }));
      if (f === 'add') pickImage(key => commit(() => { m.logos.push({file: key, alt: 'Logo'}); }));
      if (f === 'first') commit(() => { m.logos.unshift(m.logos.splice(k, 1)[0]); });
      if (f === 'del') commit(() => { m.logos.splice(k, 1); }); }; }
  else if (a === 'anchor') { const figs = [...new Set(LX.D.slides.filter(x => x.figure).map(x => x.figure.src))];
    tb.innerHTML = `<b>贯穿全稿的示意图</b><button data-f="rep">换成我的图片</button>${figs.map((f, i) => `<button data-f="fig" data-src="${esc(f)}">用论文图 ${i + 1}</button>`).join('')}${m.anchor && m.anchor.kind === 'pair' ? '' : '<button data-f="pair">恢复样张的示意图</button>'}<button data-f="none">不显示</button>
<p class="e-hint">它会出现在扉页、方法页和结论页。最好是论文里的一张关键图或装置示意图。</p>`;
    tb.onclick = e => { const b = e.target.closest('[data-f]'); if (!b) return; const f = b.dataset.f;
      if (f === 'rep') pickImage(key => commit(() => { m.anchor = {kind: 'image', src: key}; }));
      if (f === 'fig') commit(() => { m.anchor = {kind: 'image', src: b.dataset.src}; });
      if (f === 'pair') commit(() => { m.anchor = {kind: 'pair'}; }); if (f === 'none') commit(() => { delete m.anchor; }); }; }
  else if (a === 'figure') { const fg = s.figure;
    tb.innerHTML = `<b>论文原图</b><button data-f="crop">裁切与放大</button><button data-f="rep">换一张图片</button>
<label class="e-tpx">原图里最小的字约 <input type="number" min="4" step="1" value="${fg.text_px || ''}"> 像素高</label>${layoutButtons(s)}
<p class="e-hint">字高用来检查放映时是否看得清；用 extract.py 取图时会自动填写。</p>`;
    $('.e-tpx input', tb).onchange = e => commit(() => { fg.text_px = +e.target.value || 0; });
    tb.onclick = e => { const f = (e.target.closest('[data-f]') || {}).dataset?.f; if (!f) return;
      if (f === 'crop') { hideTB(); figureEditor(); } else if (f === 'rep') pickImage((key, im) => commit(() => { fg.src = key; fg.crop = [0, 0, 1, 1]; delete fg.focus; delete fg.cover; fg.text_px = Math.max(8, Math.round(im.h / 70)); fg.source = 'replace with the figure’s source'; }));
      else layoutAct(s, f); }; }
  placeTB(box.getBoundingClientRect());
}
/* arrangement: which side the evidence sits, how wide it is, where the text sits */
const LAYOUTS = ['fig', 'paperfig', 'flow', 'close'];
const layOK = s => LAYOUTS.includes(s.layout) && !LX.STY[ST.style].fixed_layout;
function layoutButtons(s) { if (!layOK(s)) return LAYOUTS.includes(s.layout) ? '<i class="e-div"></i><span class="e-note">这种风格的版式是固定的</span>' : '';
  const w = s.layout === 'fig' || s.layout === 'paperfig';
  return `<i class="e-div"></i><button data-f="swap" title="图和文字左右对调">⇄ 对调</button>${w ? '<button data-f="narrow" title="图窄一栏">图 −</button><button data-f="wide" title="图宽一栏">图 ＋</button>' : ''}` +
    (w ? '<button data-f="vtop" title="文字靠上">文字↑</button><button data-f="vmid" title="文字居中">文字·</button><button data-f="vend" title="文字靠下">文字↓</button>' : '') + (s.lay ? '<button data-f="reset">恢复风格默认</button>' : ''); }
function layoutAct(s, f) { const st = LX.STY[ST.style], L = s.lay || {}, side = L.side || st.fig_side || 'l', k = L.split || 8;
  const set = o => commit(() => { s.lay = {...L, ...o}; });
  if (f === 'swap') set({side: side === 'l' ? 'r' : 'l'}); else if (f === 'wide') { if (k < 9) set({split: k + 1}); else toast('最多占 9 栏，文字栏不能再窄'); }
  else if (f === 'narrow') { if (k > 5) set({split: k - 1}); else toast('最少占 5 栏，图再窄就看不清'); }
  else if (f === 'vtop') set({valign: 'start'}); else if (f === 'vmid') set({valign: 'center'}); else if (f === 'vend') set({valign: 'end'}); else if (f === 'reset') commit(() => { delete s.lay; }); }
function layoutTB(node, s) { const tb = $('#e-tb'); hideTB(); node.classList.add('e-sel'); tb.className = 'lay';
  tb.innerHTML = `<b>版式</b>${layoutButtons(s) || '<span class="e-note">这一页没有可调的版式</span>'}<p class="e-hint">也可以拖动图和文字之间的竖条。宽度按网格吸附，所以页面始终对齐。</p>`;
  tb.onclick = e => { const f = (e.target.closest('[data-f]') || {}).dataset?.f; if (f) layoutAct(s, f); }; placeTB(node.getBoundingClientRect()); }
function gutter(cur, s) { const g = $('#e-gut'); g.style.display = 'none'; if (!layOK(s) || !(s.layout === 'fig' || s.layout === 'paperfig')) return;
  const fig = $('figure', cur), notes = $('.notes', cur); if (!fig || !notes) return; const F = fig.getBoundingClientRect(), N = notes.getBoundingClientRect(), R = cur.getBoundingClientRect(), sc = R.width / 1920;
  const left = F.left < N.left, x = left ? (F.right + N.left) / 2 : (N.right + F.left) / 2; Object.assign(g.style, {display: 'block', left: x - 8 + 'px', top: Math.min(F.top, N.top) + 'px', height: Math.max(F.height, N.height) + 'px'});
  const colX = c => R.left + (120 + c * (1712 / 12) - 16) * sc;
  g.onpointerdown = e => { e.preventDefault(); g.setPointerCapture(e.pointerId); g.classList.add('drag'); let k = (s.lay && s.lay.split) || 8;
    g.onpointermove = ev => { const c = Math.round(((ev.clientX - R.left) / sc - 120 + 16) / (1712 / 12)); k = Math.max(5, Math.min(9, left ? c : 12 - c)); g.style.left = colX(left ? k : 12 - k) - 8 + 'px'; g.dataset.k = `图占 ${k} 栏`; };
    g.onpointerup = () => { g.onpointermove = null; g.classList.remove('drag'); if (k !== ((s.lay && s.lay.split) || 8)) commit(() => { s.lay = {...(s.lay || {}), split: k}; }); }; }; }
function bindStage(cur, s) {
  $$('[data-path]', cur).forEach(elm => elm.onclick = e => { e.stopPropagation(); if (ED.editing !== elm) editText(elm, e); });
  $$('[data-lpath]', cur).forEach(n => n.onclick = e => { e.stopPropagation(); editLabel(n); });
  $$('[data-asset]', cur).forEach(n => n.onclick = e => { e.stopPropagation(); assetTB(n); });
  const ch = $('figure svg.chart', cur) || $('.anchor', cur); if (ch && layOK(s)) ch.onclick = e => { if (e.target.closest('[data-lpath],[data-asset]')) return; e.stopPropagation(); layoutTB(ch, s); };
  cur.onclick = e => { if (!e.target.closest('[data-path],[data-lpath],[data-asset]')) hideTB(); };
  requestAnimationFrame(() => gutter(cur, s));
}
/* inspector panels */
function identityPanel() { const m = LX.D.meta, f = (k, n, ph) => `<label>${n}<input data-m="${k}" value="${esc(m[k] || '')}" placeholder="${ph}"></label>`;
  const logos = (m.logos || []).map((l, k) => { const im = LX.IMG[l.file]; return `<div class="e-logo"><span class="thumb">${im ? `<img src="${im.uri}" alt="">` : ''}</span><span>${esc(l.alt || 'Logo ' + (k + 1))}</span><button data-l="rep" data-k="${k}">换</button><button data-l="del" data-k="${k}">删</button></div>`; }).join('');
  return `<details><summary>署名与标识</summary>${f('short', '页脚短标题', '论文的短标题')}${f('author', '讲者', '姓名')}${f('email', '邮箱', 'name@institute.edu')}${f('cite', '完整出处', 'Author (Year), Journal …')}${f('link', '论文链接（结论页二维码）', 'https://doi.org/…')}
<p class="e-hint">讲者和邮箱显示在每一页的页脚。二维码在重新构建时生成。</p><div class="e-logos">${logos || '<p class="e-hint">还没有 logo。</p>'}</div><button data-l="add">添加 logo</button>
<p class="e-hint">也可以直接点页面上的 logo 或示意图来替换。</p></details>`; }
function layoutPanel(s) { if (!LAYOUTS.includes(s.layout)) return '';
  return `<details${s.lay ? ' open' : ''}><summary>版式</summary><div class="e-row e-layrow">${layoutButtons(s) || ''}</div><p class="e-hint">只改这一页。宽度按 12 栏网格吸附；换风格时这些设置保留。</p></details>`; }
function bindPanels(insp, s) {
  $$('[data-m]', insp).forEach(i => i.onchange = () => commit(() => { const v = i.value.trim(); if (v) LX.D.meta[i.dataset.m] = v; else delete LX.D.meta[i.dataset.m]; }));
  $$('[data-l]', insp).forEach(b => b.onclick = () => { const m = LX.D.meta, k = +b.dataset.k; m.logos ||= [];
    if (b.dataset.l === 'add') pickImage(key => commit(() => m.logos.push({file: key, alt: 'Logo'})));
    if (b.dataset.l === 'rep') pickImage(key => commit(() => { m.logos[k].file = key; delete m.logos[k].dark; }));
    if (b.dataset.l === 'del') commit(() => m.logos.splice(k, 1)); });
  const lr = $('.e-layrow', insp); if (lr) lr.onclick = e => { const f = (e.target.closest('[data-f]') || {}).dataset?.f; if (f) layoutAct(s, f); };
}
addEventListener('keydown', e => { if (ST.mode !== 'edit' || ED.editing || e.target.closest('input,textarea,select')) return;
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); $(`[data-a="${e.shiftKey ? 'redo' : 'undo'}"]`).click(); }
  else if (e.key === 'Escape') hideTB(); else if (e.key === 'ArrowDown' || e.key === 'PageDown') { if (ST.i < LX.D.slides.length - 1) { ST.i++; ED.prev = 99; redraw(); } }
  else if (e.key === 'ArrowUp' || e.key === 'PageUp') { if (ST.i > 0) { ST.i--; ED.prev = 99; redraw(); } } });

/* boot */
(() => { const m = hp[0] && !hp[0].includes('=') ? hp[0] : (DATA.open || 'present');
  if (['flat', 'expand', 'handout'].includes(m)) staticMode(m); else if (m === 'gallery') gallery(); else if (m === 'edit') edit(); else present(0, 0); })();

