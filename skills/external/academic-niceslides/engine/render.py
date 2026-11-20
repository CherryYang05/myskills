"""Contact sheets and PDFs.  python3 engine/render.py <project> [slug ...] [--handout]
out/sheets/<slug>.png = final state of every slide · out/steps/<slug>.png = every click · out/<slug>.pdf = one page per click
--handout also writes out/<slug>-handout.pdf (A4: each slide with its speaker notes)."""
import sys, pathlib, asyncio, io
from playwright.async_api import async_playwright
from PIL import Image
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import chrome
P = pathlib.Path(sys.argv[1]).resolve(); handout = "--handout" in sys.argv; args = [a for a in sys.argv[2:] if not a.startswith("--")]
def sheet(ims, cols, path, tw=960):
    th = tw*9//16; rows = -(-len(ims)//cols); sh = Image.new("RGB", (cols*(tw+16)-16, rows*(th+16)-16), "#777")
    for i, im in enumerate(ims): sh.paste(im.resize((tw, th), Image.LANCZOS), ((i % cols)*(tw+16), (i//cols)*(th+16)))
    sh.save(path)
async def main(slugs):
    for d in ("sheets", "steps"): (P / "out" / d).mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await chrome.launch(p); pg = await b.new_page(viewport={"width": 1920, "height": 1080})
        await pg.goto(f"file://{P}/out/deck.html#flat"); slugs = slugs or [await pg.evaluate("ST.style")]
        async def mode(s, m):
            await pg.evaluate("([s, m]) => { ST.style = s; staticMode(m); return document.fonts.ready }", [s, m])
            return [Image.open(io.BytesIO(await e.screenshot())) for e in await pg.query_selector_all("#stage .slide")] if m != "handout" else None
        for s in slugs:
            sheet(await mode(s, "flat"), 2, P / f"out/sheets/{s}.png")
            sheet(await mode(s, "expand"), 4, P / f"out/steps/{s}.png", 640)
            await pg.pdf(path=str(P / f"out/{s}.pdf"), width="1920px", height="1080px", print_background=True)
            if handout:
                await mode(s, "handout"); await pg.pdf(path=str(P / f"out/{s}-handout.pdf"), format="A4", print_background=True)
            print(s, "rendered")
        await b.close()
asyncio.run(main(args))
