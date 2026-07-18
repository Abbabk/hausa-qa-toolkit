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
