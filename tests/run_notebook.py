"""Run a notebook of the built site headlessly and print its outputs.

usage: python tests/run_notebook.py <notebook.ipynb> [base url] [timeout s]
Exits 1 if a cell shows an error.
"""
import sys
import time

from playwright.sync_api import sync_playwright

nb = sys.argv[1]
base = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 900

STATE = """() => {
  const cells = [...document.querySelectorAll('.jp-Notebook .jp-Cell.jp-CodeCell')];
  return cells.map(c => ({
    prompt: (c.querySelector('.jp-InputPrompt') || {}).textContent || '',
    out: [...c.querySelectorAll('.jp-OutputArea-output')].map(o =>
      o.querySelector('img') ? '[image]' : o.textContent.slice(0, 2000)),
    error: !!c.querySelector('[data-mime-type="application/vnd.jupyter.stderr"], .jp-RenderedText[data-mime-type="application/vnd.jupyter.error"]'),
  }));
}"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 1000})
    page.on("console", lambda m: m.type == "error" and print("console:", m.text[:300]))
    page.goto(f"{base}/notebooks/index.html?path={nb}")
    page.wait_for_selector(".jp-Notebook .jp-Cell", timeout=120_000)
    # wait for the kernel to be ready
    page.wait_for_function(
        "() => window.jupyterapp && document.querySelector('.jp-Notebook-ExecutionIndicator, .jp-Toolbar')",
        timeout=120_000,
    )
    time.sleep(5)
    t0 = time.time()
    page.evaluate("window.jupyterapp.commands.execute('notebook:run-all-cells')")
    while True:
        time.sleep(3)
        cells = page.evaluate(STATE)
        busy = [c for c in cells if "*" in c["prompt"]]
        done = all(c["prompt"].strip() not in ("", "[ ]:") for c in cells)
        if (not busy and done) or time.time() - t0 > timeout:
            break
    print(f"--- {nb}: {time.time() - t0:.0f}s ---")
    failed = False
    for i, c in enumerate(cells):
        print(f"[{i}] {c['prompt'].strip()}")
        for o in c["out"]:
            print("   ", o.replace("\n", "\n    "))
        failed |= any("Traceback" in o or "Error" in o.split("\n")[0] for o in c["out"])
    page.screenshot(path=f"dist/{nb}.png", full_page=True)
    browser.close()
    sys.exit(1 if failed or busy else 0)
