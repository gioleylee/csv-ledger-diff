# CSV Ledger Diff

Compare two UTF-8 CSV exports using a unique key. The JSON report lists added rows, removed rows, and field-level edits. Column order and row order can differ. Values are compared as text, including whitespace and leading zeroes.

```sh
python ledger_diff.py before.csv after.csv --key id
```

Both exports must use the same set of named columns. Use Python 3.11 or later. The tool uses only the Python standard library.

Run tests from the project directory with `python -m unittest -v`.
