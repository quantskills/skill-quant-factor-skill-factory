---
name: skill-quant-factor-skill-factory
description: Use when converting OHLCV alpha ideas into QuantSkills organization factor
  Skills, batch-generating non-duplicate framework-neutral quant factor Skill folders,
  validating them on cached real market data such as AkShare A-share and Yahoo US
  data, and writing factor evaluation reports.
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
quantSkills:
  project_type: skill
  collection: skill-quant-factor-skill-factory
  creator: abgyjaguo
  maintainer: abgyjaguo
  category: tooling
  tags:
  - factor-factory
  - alpha
  - ohlcv
  - validation
  - skill-generation
  platforms:
  - claude-code
  - codex
  - hermes
  - openclaw
  - cursor
  status: stable
  validation_level: runnable
  maintainer_type: official
  summary_zh: 不是因子库本身，而是继续生产因子库的工具：批量生成、验证和打包框架中立的 OHLCV 量化因子 Skill。
  summary_en: Factory skill for turning OHLCV alpha ideas into QuantSkills factor
    skills with real-market validation and packaging.
  license: GPL-3.0
---

```json qsh-form
{
  "version": 1,
  "task": {
    "placeholder": "请说明要生成或维护的 OHLCV 因子技能主题、现有索引与输出要求",
    "required": true
  },
  "fields": [
    {
      "key": "count",
      "label": "生成数量",
      "type": "number",
      "default": "10",
      "required": true
    },
    {
      "key": "start_id",
      "label": "起始因子 ID",
      "type": "number",
      "placeholder": "例如：1001"
    },
    {
      "key": "market",
      "label": "验证市场",
      "type": "select",
      "default": "both",
      "options": [
        { "value": "both", "label": "A 股与美股" },
        { "value": "cn", "label": "A 股" },
        { "value": "us", "label": "美股" }
      ]
    }
  ],
  "prompt_template": "{{#task}}任务与材料：\n{{task}}\n\n{{/task}}{{#attachments}}用户上传的材料（已放入工作区）：\n{{attachments}}\n\n{{/attachments}}使用量化因子技能工厂生成 {{count}} 个框架无关的 OHLCV 因子 Skill。{{#start_id}}从起始 ID {{start_id}} 起生成；{{/start_id}}未指定起始 ID 时按既有索引推断下一个可用编号。并在 {{market}} 真实缓存行情上验证；生成前检查既有索引避免重复，确保每个目录具备规定的技能说明、双语文档、因子与验证脚本、真实验证结果、公式参考和适配文件，核验通过数、数据供应商、市场覆盖、合并索引重复数及抽样验证结果，输出中文报告。"
}
```

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
