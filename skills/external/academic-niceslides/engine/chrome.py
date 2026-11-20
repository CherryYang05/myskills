import os, shutil
async def launch(p):
    for c in (os.environ.get("ACADEMIC_NICESLIDES_CHROME") or os.environ.get("LECTERN_CHROME"), shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser"),
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if c and os.path.exists(c): return await p.chromium.launch(executable_path=c)
    return await p.chromium.launch()
