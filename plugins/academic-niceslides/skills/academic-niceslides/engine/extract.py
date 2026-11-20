"""Take a figure or table out of a paper PDF, unaltered, and register where it came from.
  python3 engine/extract.py <project> paper.pdf --find 7                 list candidate regions on page 7 (PDF points)
  python3 engine/extract.py <project> paper.pdf --page 7 --bbox 72,90,540,410 --name fig2 --label "Figure 2"
Writes <project>/assets/<name>.png (300 dpi) and appends to <project>/assets/provenance.json."""
import sys, json, hashlib, pathlib, argparse
import pymupdf as fitz
a = argparse.ArgumentParser(); a.add_argument("project"); a.add_argument("pdf"); a.add_argument("--find", type=int)
a.add_argument("--page", type=int); a.add_argument("--bbox"); a.add_argument("--name"); a.add_argument("--label", default=""); a.add_argument("--dpi", type=int, default=300)
o = a.parse_args(); doc = fitz.open(o.pdf)
if o.find:
    pg = doc[o.find-1]; print(f"page {o.find}: {pg.rect.width:.0f} x {pg.rect.height:.0f} pt")
    for im in pg.get_image_info(): print("  image   ", ",".join(f"{v:.0f}" for v in im["bbox"]))
    for r in pg.cluster_drawings(): print("  drawing ", ",".join(f"{v:.0f}" for v in r))
    for b in pg.get_text("blocks"):
        if b[4].strip().lower().startswith(("fig", "table")): print("  caption ", ",".join(f"{v:.0f}" for v in b[:4]), "|", b[4].strip()[:70].replace("\n", " "))
    sys.exit()
pg = doc[o.page-1]; box = fitz.Rect(*map(float, o.bbox.split(","))) if o.bbox else pg.rect
P = pathlib.Path(o.project); (P / "assets").mkdir(exist_ok=True); out = P / "assets" / f"{o.name}.png"
pix = pg.get_pixmap(clip=box, dpi=o.dpi); pix.save(out)
sizes = [s["size"] for b in pg.get_text("dict", clip=box)["blocks"] for l in b.get("lines", []) for s in l["spans"] if s["text"].strip()]
text_px = round(min(sizes)*o.dpi/72) if sizes else 0
reg = P / "assets/provenance.json"; R = json.load(open(reg)) if reg.exists() else []
R = [r for r in R if r["file"] != f"assets/{o.name}.png"] + [{"file": f"assets/{o.name}.png", "label": o.label, "pdf": pathlib.Path(o.pdf).name,
     "pdf_sha256": hashlib.sha256(open(o.pdf, "rb").read()).hexdigest()[:16], "page": o.page, "bbox_pt": list(box), "dpi": o.dpi,
     "size_px": [pix.width, pix.height], "text_px": text_px}]
json.dump(R, open(reg, "w"), indent=1)
print(f"{out}  {pix.width}x{pix.height}px  smallest text ≈ {text_px}px  → use \"text_px\": {text_px} in the deck")
