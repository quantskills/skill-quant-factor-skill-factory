---
name: skill-quant-factor-skill-factory
description: Use when converting OHLCV alpha ideas into QuantSkills organization factor Skills, batch-generating non-duplicate framework-neutral quant factor Skill folders, validating them on cached real market data such as AkShare A-share and Yahoo US data, and writing factor evaluation reports.
license: GPL-3.0-only
metadata:
  short-description: Generate and validate quant factor Skills
  organization: QuantSkills
  organization_url: https://github.com/quantskills
  repository: skill-quant-factor-skill-factory
  repository_url: https://github.com/quantskills/skill-quant-factor-skill-factory
  project_type: skill
  collection: skill-quant-factor-skill-factory
  creator: abgyjaguo
  maintainer: abgyjaguo
  license: GPL-3.0-only
  copyright: Copyright (C) 2026 QuantSkills
---

# Skill Quant Factor Skill Factory

Use this QuantSkills organization Skill when the user wants to create, extend, or maintain a library of framework-neutral quant factor Skills from OHLCV data.

The standard contract is:

- Factors are framework-neutral Python Skills for the QuantSkills organization.
- Users bring their own market data; generated factor code only requires `open`, `high`, `low`, `close`, `volume`, plus optional `date`, `symbol`, and `market`.
- Validation must use cached real OHLCV data when available. Do not describe synthetic validation as real validation.
- For China data, prefer AkShare A-share cache. For US data, prefer Yahoo Finance cache.
- Every generated factor folder must include `SKILL.md`, bilingual `README.md`, `scripts/factor.py`, `scripts/validate.py`, `validation_real/result.json`, `validation_real/report.md`, `references/formula.md`, and `agents/openai.yaml`.
- Before delivery, verify uniqueness across all previous factor indexes and confirm the generated package is complete.

## Workflow

1. Inspect the current project state:

   ```powershell
   Get-ChildItem
   Get-Content .\real_market_data\panels\panel_manifest.json
   ```

2. Confirm the real data panel contains market and vendor evidence:

   ```json
   {
     "markets": {"cn": 98, "us": 50},
     "sources": ["akshare", "yahoo"]
   }
   ```

   Exact counts can vary by project, but the report must state the actual counts.

3. Generate the next batch with the reusable script.

   If the project already has `tools/real_data_factor_pipeline.py`, copy only `scripts/generate_factor_skill_batch.py` from this skill into the project's `tools/` folder. If not, copy the validated pipeline scripts from a previous project first, then adapt data download paths.

   Example:

   ```powershell
   $env:PYTHONUTF8='1'
   python .\tools\generate_factor_skill_batch.py `
     --count 200 `
     --start-id 1001 `
     --existing-index .\real_data_factor_skills_all_1000_index.json `
     --output-root .\real_data_factor_skills_extra_200_next `
     --combined-index .\real_data_factor_skills_all_1200_index.json `
     --report-name extra_200_next_factor_evaluation_report.md
   ```

4. Run validation and acceptance checks:

   ```powershell
   python -m py_compile .\tools\generate_factor_skill_batch.py
   python .\tools\generate_factor_skill_batch.py --count <N> --start-id <ID> --existing-index <index.json> --output-root <folder> --combined-index <index.json> --report-name <report.md>
   ```

5. Audit the output:

   - Count generated factor directories equals the requested count.
   - `validation_summary_real.json` has the requested count.
   - All rows have `status == "pass"` unless the user explicitly accepts review rows.
   - All rows show the expected real-data market coverage.
   - Combined index has no duplicate `slug`.
   - Run `scripts/validate.py` for the first, middle, and last generated factor folders.

## Output Summary

Always finish with:

- output folder
- factor ID range
- pass count
- real data panel counts and market vendors
- combined index count and duplicate count
- report path
- sampled `scripts/validate.py` result

## Important Guardrails

- Do not claim Yahoo data is present unless `real_market_data/raw/yahoo_us/*.parquet` and the panel manifest prove it.
- Do not overwrite previous batches unless the user asks for regeneration.
- Use UTF-8 when reading or writing Chinese filenames and Markdown: set `PYTHONUTF8=1` in PowerShell.
