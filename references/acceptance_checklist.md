# Acceptance Checklist

Use this checklist before reporting completion.

## Data

- `real_market_data/panels/panel_manifest.json` exists.
- Manifest records row count, symbol count, market counts, date range, and market vendors.
- Raw cache folders match the stated vendors.

## Generation

- Requested factor count equals generated directory count.
- Factor IDs are contiguous and start from the requested ID.
- Combined index count equals previous count plus generated count.
- Combined index slug count equals combined index row count.

## Validation

- `validation_summary_real.json` exists in the output folder.
- Each metrics row has `status: pass` unless review rows are intentionally accepted.
- Each metrics row records `markets`.
- Each factor has a self-contained `scripts/validate.py`.

## Documentation

- Every factor folder has bilingual README content.
- `SKILL.md` describes when to use the factor.
- `references/formula.md` contains formula text and params.
- `agents/openai.yaml` contains display metadata.

## Publishing Package

- Keep only workflow instructions, scripts, references, and agent metadata.
- Do not include cached market data in the skill repository.
- Do not include local proxy settings, personal paths, tokens, or account material.
