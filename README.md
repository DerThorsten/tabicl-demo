# TabICL in the browser

[TabICL](https://github.com/soda-inria/tabicl), a tabular foundation model, running fully client-side in
[JupyterLite](https://jupyterlite.readthedocs.io) with the [xeus-python](https://github.com/jupyter-xeus/xeus-python)
kernel. PyTorch, scikit-learn and TabICL are WebAssembly packages from
[emscripten-forge](https://github.com/emscripten-forge/recipes). No server, no install.

**Try it:** https://derthorsten.github.io/tabicl-demo/

The notebook [`content/tabicl.ipynb`](content/tabicl.ipynb) downloads the pretrained checkpoint from the
Hugging Face Hub in the browser, draws decision boundaries on toy data and compares TabICL with
scikit-learn models on a real table.

The kernel environment is defined in [`environment.yml`](environment.yml).

## Build locally

```bash
pixi run build   # jupyter lite build -> dist/
pixi run serve   # build, then serve on http://localhost:8000
```

Headless check of the notebook (needs `pixi run serve` in another shell):

```bash
pixi run -e test playwright install chromium
pixi run -e test python tests/run_notebook.py tabicl.ipynb
```
