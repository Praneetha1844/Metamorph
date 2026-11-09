# Evaluation harness

Runs the refactor-and-verify loop over a folder of legacy snippets and writes one CSV row per
case. **No results are published in this repository.** Run it against your own model to
produce them.

## Case format

```
eval/cases/<case-name>/
  source.py   the legacy module
  tests.py    pytest tests that import it as `solution`
```

The three cases in `eval/cases/` are short samples written by hand for this project.
A case whose tests fail on the original source is reported as `baseline_failed`.

## Run

```bash
# from engine/, with the model configured through METAMORPH_* variables
python eval/run_eval.py --cases eval/cases --out results.csv
# or: make eval CASES=eval/cases OUT=results.csv
```

## Output columns

`case, provider, verdict, attempts, baseline_passed, sloc_before, sloc_after, cc_mean_before,
cc_mean_after, mi_before, mi_after, duration_s`

Metric columns are filled only for accepted refactors. `results*.csv` is git-ignored.

## Reading the numbers

A single run on a handful of snippets says little. Model output varies between runs, so
repeat runs and report the spread. "Accepted" means the supplied tests passed, nothing more.
