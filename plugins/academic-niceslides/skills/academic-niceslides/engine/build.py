"""Pack a talk into one self-contained HTML file that presents, edits and exports itself.
  python3 engine/build.py <project> [--styles plate,grid] [--open present|gallery|edit]
<project> holds deck.json, facts.json and assets/. Writes <project>/out/deck.html."""
import json, re, base64, sys, pathlib, mimetypes
E = pathlib.Path(__file__).resolve().parent; ROOT = E.parent
P = pathlib.Path(sys.argv[1]).resolve(); arg = lambda k, d=None: sys.argv[sys.argv.index(k)+1] if k in sys.argv else d
only = arg("--styles"); only = only.split(",") if only else None
D = json.load(open(P / "deck.json")); F = json.load(open(P / "facts.json"))
# 0. images uploaded in the editor travel inside an exported deck.json; unpack them into assets/uploads once
if D.get("uploads"):
    (P / "assets/uploads").mkdir(parents=True, exist_ok=True); ups = D.pop("uploads"); txt = json.dumps(D, ensure_ascii=False)
    for key, u in ups.items():
        name = re.sub(r"[^\w.-]+", "_", key.split("/", 1)[1]); (P / "assets/uploads" / name).write_bytes(base64.b64decode(u.split(",", 1)[1]))
        txt = txt.replace(json.dumps(key)[1:-1], "assets/uploads/" + name)
    D = json.loads(txt); json.dump(D, open(P / "deck.json", "w"), indent=1, ensure_ascii=False)
    print(f"unpacked {len(ups)} uploaded image(s) into assets/uploads/ and updated deck.json")
# 1. every number must be registered
need = set()
def walk(o, key=None):
    if isinstance(o, dict): [walk(v, k) for k, v in o.items()]
    elif isinstance(o, list): [walk(v, key) for v in o]
    elif isinstance(o, str):
        need.update(re.findall(r"\{(\w+)\}", o))
        if key in ("v", "lo", "hi", "b", "se", "cells"): need.add(o)
walk(D["slides"]); missing = sorted(k for k in need if k not in F)
if missing: raise SystemExit("UNREGISTERED FACTS (add them to facts.json through analysis.py, never by hand in the deck): " + ", ".join(missing))
# 2. images, embedded once
def uri(f): return f"data:{mimetypes.guess_type(f.name)[0] or 'image/png'};base64,{base64.b64encode(f.read_bytes()).decode()}"
IMG = {}
def add(rel):
    if not rel or rel in IMG: return
    f = P / rel
    if not f.exists(): raise SystemExit(f"missing asset {rel}")
    w = h = 0
    if f.suffix.lower() != ".svg":
        from PIL import Image; w, h = Image.open(f).size
    IMG[rel] = {"uri": uri(f), "w": w, "h": h}
for l in D["meta"].get("logos", []): add(l.get("file")); add(l.get("dark"))
if D["meta"].get("anchor", {}).get("src"): add(D["meta"]["anchor"]["src"])
for s in D["slides"]:
    if "figure" in s: add(s["figure"]["src"])
if D["meta"].get("link"):
    import segno
    IMG["__qr"] = {"uri": segno.make(D["meta"]["link"], error="m").svg_data_uri(scale=8, border=1, dark="#000", light="#fff"), "w": 0, "h": 0}
# 3. styles
STY, css, order = {}, [], []
pref = ["plate", "grid", "riso", "arch", "seal", "transit", "marker", "chalk", "rail", "chapter", "feature", "cite", "mono", "access", "night", "fingerprint", "kraft"]
dirs = sorted((d for d in (ROOT / "styles").iterdir() if (d / "style.json").exists()), key=lambda d: (pref.index(d.name) if d.name in pref else 99, json.load(open(d / "style.json")).get("order", 50), d.name))
for d in dirs:
    if only and d.name not in only: continue
    st = json.load(open(d / "style.json")); order.append(st["slug"])
    STY[st["slug"]] = {k: st[k] for k in ("slug", "en", "cn", "line", "family", "ground", "slots", "use", "title_lines", "group", "fig_side", "fixed_layout") if k in st}
    css.append("".join(f'@font-face{{font-family:"{st["family"]}";font-weight:{f["weight"]};font-style:{f.get("style","normal")};'
                       f'src:url(data:font/woff2;base64,{base64.b64encode((d/"fonts"/f["file"]).read_bytes()).decode()}) format("woff2")}}' for f in st["fonts"]))
    css.append((d / "style.css").read_text())
data = json.dumps({"deck": D, "facts": F, "styles": STY, "order": order, "images": IMG, "open": arg("--open", "present")}, ensure_ascii=False).replace("<", "\\u003c")
js = "".join(f'<script data-keep>{(E / "js" / n).read_text()}</script>' for n in ("render.js", "lint.js", "app.js", "editor.js"))
(P / "out").mkdir(exist_ok=True)
(P / "out/deck.html").write_text(
    f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{D["meta"].get("short","Deck")}</title>'
    f'<style>{(E / "app.css").read_text()}{(E / "base.css").read_text()}</style><style>{"".join(css)}</style></head><body>'
    f'<script id="lectern-data" type="application/json">{data}</script><div id="stage"></div><div id="ui"></div>{js}</body></html>')
print(f"built out/deck.html · {len(order)} styles · {len(D['slides'])} slides · {(P/'out/deck.html').stat().st_size//1024} KB")
