# tools

Scripts used to generate the first version of this documentation from the
LaTeX sources of the Persistent-1 CDR (`cdr.zip`).

| Script        | What it does |
|---------------|--------------|
| `tex2rst.py`  | Converts the CDR chapters (`chapters/*.tex`, `appendices/link_budget.tex`) to reStructuredText: sections, figures, tables (incl. `longtable`), equations, lists, `\autoref`/`\ref` → `:numref:`/`:eq:`/`:ref:`, `\cite` → `:cite:`, `\ac` → acronym. Also writes `figures.json`, the list of images used. |
| `copyfigs.py` | Copies the images listed in `figures.json` into `figures/` and `curves/`, rendering PDF figures to PNG with the same `trim` crop used in the LaTeX. |

## Usage

```
pip install pymupdf
mkdir -p /tmp/cdr && python -c "import zipfile; zipfile.ZipFile('cdr.zip').extractall('/tmp/cdr')"

python tools/tex2rst.py /tmp/cdr /tmp/rst-out          # first-pass .rst + figures.json
python tools/copyfigs.py /tmp/cdr . /tmp/rst-out/figures.json
```

## Caveats

* **Always write to a separate output directory**, never the repository root:
  the chapters in the repository were edited by hand after conversion (labels,
  typos, captions, requirements merged into `budgets.rst`, red `:red:` markers
  for TBD/TBC/TODO, etc.) and would be overwritten. Use the output to diff
  against the current chapters when the LaTeX sources change.
* The chapter list is hard-coded in `CHAPTERS` (`tex2rst.py`) and still
  produces a separate `requirements.rst`; in this documentation that content
  lives in the *Requirements* section of `budgets.rst`.
* It only handles the LaTeX commands used by the CDR sources; it is not a
  general LaTeX-to-RST converter.
* Some figures referenced by the CDR are not in `cdr.zip` and are reported as
  `MISSING` by `copyfigs.py`.
