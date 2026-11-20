"""Deterministic lint on the rendered deck, every style.  python3 engine/lint.py <project> [slug ...]   Exit 1 on any failure."""
import sys, json, pathlib, asyncio
from playwright.async_api import async_playwright
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); import chrome
P = pathlib.Path(sys.argv[1]).resolve()
async def main(slugs):
    bad = 0
    async with async_playwright() as p:
        b = await chrome.launch(p); pg = await b.new_page(viewport={"width": 1920, "height": 1080})
        await pg.goto(f"file://{P}/out/deck.html#flat"); slugs = slugs or await pg.evaluate("ORDER")
        for s in slugs:
            await pg.evaluate("s => { ST.style = s; staticMode('flat'); return document.fonts.ready }", s)
            res = await pg.evaluate("LINT(document.getElementById('stage'))"); bad += len(res)
            print(f"{s}: {'PASS' if not res else str(len(res))+' FAIL'}")
            for r in res: print(f"   slide {r['slide']} [{r['rule']}] {r['msg']}")
        await b.close()
    sys.exit(1 if bad else 0)
asyncio.run(main(sys.argv[2:]))
