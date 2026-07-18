# Release process

HausaQA uses semantic versioning.

## Local release checklist

1. Confirm the tree contains no secrets, private paths, or non-clean-room material.
2. Confirm the version in `pyproject.toml`, `src/hausaqa/__init__.py`, reports, and changelog agrees.
3. Run `python -m pytest --cov` and keep core-engine coverage at or above 85 percent.
4. Run `ruff check .`.
5. Run `python scripts/evaluate.py` and compare the result with `docs/evaluation.md`.
6. Build an sdist and wheel with `python -m build` in a clean environment.
7. Install the wheel into a fresh virtual environment and run the CLI fixture.
8. Review generated package contents and hashes.

## Public release checklist

Public hosting, remote pushes, package uploads, tags, and hosted releases are separate actions. Before them, establish protected required CI on the default branch, review repository settings, publish signed or hashed artifacts, and record the release URL and digest in the changelog.

## Local Python compatibility evidence

On 2026-07-18, the complete local release gate was run from clean detached worktrees and fresh virtual environments with CPython 3.11.15 and CPython 3.12.13. Each interpreter completed `ruff check .`, 102 tests with 96.72 percent branch coverage, the synthetic evaluation, an isolated sdist and wheel build, clean-wheel import and console-entrypoint smoke tests, `pip check`, and a two-run deterministic CLI output comparison.

The same test suite also passed under `PYTHONWARNINGS=error` on both interpreters. This proves the local Python 3.11 and 3.12 compatibility matrix for commit `8902d23917b6d0f182150a06c4207aa23f952487`. Hosted GitHub Actions remained unverified because the account billing lock stopped both required jobs before any workflow step ran. The required checks and branch protection were not changed.
