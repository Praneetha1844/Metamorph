"""Convenience launcher: `python eval/run_eval.py --cases eval/cases --out results.csv`."""

from metamorph_engine.evaluation import main

if __name__ == "__main__":
    raise SystemExit(main())
