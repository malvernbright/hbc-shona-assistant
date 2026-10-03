---
name: fixed-hbc-package
description: Resolved uv build error by adding the missing package and configuring setuptools to find modules in src
metadata:
  type: project
---
The `uv add` command failed because the project was being built as a package named `hbc_shona_assistant` but no Python package with that name existed under `src/`.  I created the directory `src/hbc_shona_assistant/` and added a minimal `__init__.py` that defines a `main()` function.  I also updated `pyproject.toml` to include a `[tool.setuptools]` section mapping the root package directory to `src/`, ensuring setuptools can discover the package contents during the build step.

You should now be able to run:
```bash
uv add chromadb sentence-transformers pypdf langchain-chroma
```
and have the command succeed without the previous error.

**Why:** The build system expected a module named `hbc_shona_assistant` in the `src` tree. ‑ **How to apply:** Create the package directory, add an `__init__.py`, and add the `[tool.setuptools]` entry.
