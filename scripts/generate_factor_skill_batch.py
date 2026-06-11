from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd


def import_core(project_root: Path):
    tools = project_root / "tools"
    sys.path.insert(0, str(tools))
    import real_data_factor_pipeline as core  # type: ignore

    return core


BASES = [
    ("return", "动量", "Momentum", "收益动量", "Return Momentum"),
    ("skip_return", "动量", "Momentum", "跳期收益动量", "Skip-Period Momentum"),
    ("reversal", "反转", "Reversal", "收益反转", "Return Reversal"),
    ("sma_gap", "趋势", "Trend", "均线偏离", "SMA Gap"),
    ("ema_gap", "趋势", "Trend", "EMA偏离", "EMA Gap"),
    ("dual_ema_gap", "趋势", "Trend", "双EMA趋势差", "Dual EMA Gap"),
    ("sma_slope", "趋势", "Trend", "均线斜率", "SMA Slope"),
    ("range_position", "通道", "Channel", "区间位置", "Range Position"),
    ("breakout", "突破", "Breakout", "上轨突破", "Upper Breakout"),
    ("breakdown", "突破", "Breakout", "下轨跌破", "Lower Breakdown"),
    ("rsi", "震荡", "Oscillator", "RSI强度", "RSI Strength"),
    ("rsi_reversal", "震荡", "Oscillator", "RSI反转", "RSI Reversal"),
    ("stoch", "震荡", "Oscillator", "随机区间位置", "Stochastic Position"),
    ("atr_ratio", "波动率", "Volatility", "ATR占比", "ATR Ratio"),
    ("range_ratio", "波动率", "Volatility", "振幅占比", "Range Ratio"),
    ("realized_vol", "波动率", "Volatility", "实现波动率", "Realized Volatility"),
    ("downside_vol", "波动率", "Volatility", "下行波动率", "Downside Volatility"),
    ("trend_strength", "趋势", "Trend", "风险调整趋势", "Risk-Adjusted Trend"),
    ("efficiency", "趋势", "Trend", "趋势效率", "Trend Efficiency"),
    ("volume_ratio", "量能", "Volume", "成交量放大", "Volume Expansion"),
    ("volume_z", "量能", "Volume", "成交量标准分", "Volume Z-Score"),
    ("dollar_volume", "流动性", "Liquidity", "成交额活跃度", "Dollar Volume Activity"),
    ("price_volume_corr", "量价", "Price Volume", "量价相关", "Price Volume Correlation"),
    ("obv_slope", "量价", "Price Volume", "OBV斜率", "OBV Slope"),
    ("gap_sum", "形态", "Pattern", "缺口累积", "Gap Sum"),
    ("intraday", "形态", "Pattern", "日内收益", "Intraday Return"),
    ("upper_wick", "形态", "Pattern", "上影线压力", "Upper Wick Pressure"),
    ("lower_wick", "形态", "Pattern", "下影线支撑", "Lower Wick Support"),
    ("drawdown", "回撤", "Drawdown", "距高点回撤", "Drawdown From High"),
    ("ts_rank_close", "排序", "Time Series Rank", "收盘时序排名", "Close TS Rank"),
    ("ts_rank_volume", "排序", "Time Series Rank", "成交量时序排名", "Volume TS Rank"),
    ("ret_skew", "分布", "Distribution", "收益偏度", "Return Skewness"),
    ("ret_kurt", "分布", "Distribution", "收益峰度", "Return Kurtosis"),
]

TRANSFORMS = [
    ("z", "标准化", "Z-Scored"),
    ("delta", "变化", "Delta"),
    ("smooth", "平滑", "Smoothed"),
    ("rank", "时序排名", "Time-Series Ranked"),
    ("vol_scaled", "波动缩放", "Volatility Scaled"),
    ("stability", "稳定度缩放", "Stability Scaled"),
    ("confirm_volume", "量能确认", "Volume Confirmed"),
    ("compress", "压缩", "Compressed"),
]

WINDOWS = [5, 7, 10, 14, 20, 30, 45, 60, 90, 120]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def all_candidate_specs(core: Any) -> list[Any]:
    specs = []
    seen = set()
    for window in WINDOWS:
        for transform, trans_cn, trans_en in TRANSFORMS:
            for base, cat_cn, cat_en, base_cn, base_en in BASES:
                params = {
                    "window": window,
                    "norm": max(20, min(120, window * 2)),
                    "lag": max(1, window // 5),
                    "smooth": max(3, window // 3),
                    "skip": 5,
                    "fast": max(3, window // 3),
                    "slow": window,
                }
                name_cn = f"{window}日{trans_cn}{base_cn}"
                name_en = f"{window}D {trans_en} {base_en}"
                slug = core.slugify(name_en)
                if slug in seen:
                    continue
                seen.add(slug)
                specs.append(
                    core.FactorSpec(
                        factor_id=f"R{len(specs) + 1:03d}",
                        slug=slug,
                        name_cn=name_cn,
                        name_en=name_en,
                        category_cn=cat_cn,
                        category_en=cat_en,
                        base=base,
                        transform=transform,
                        params=params,
                        formula_cn=f"{transform}({base}, window={window})",
                        formula_en=f"{transform}({base}, window={window})",
                        rationale_cn=f"该因子把“{base_cn}”与“{trans_cn}”处理结合，用来刻画价格、量能或波动状态在横截面上的可排序性。",
                        rationale_en=f"This factor combines {base_en} with a {trans_en} transform to test cross-sectional sortability in price, volume, or volatility states.",
                    )
                )
    return specs


def make_specs(core: Any, existing_indexes: list[Path], count: int, start_id: int) -> list[Any]:
    existing_slugs = set()
    for index_path in existing_indexes:
        if index_path.exists():
            existing_slugs.update(row["slug"] for row in read_json(index_path))
    specs = []
    for spec in all_candidate_specs(core):
        if spec.slug in existing_slugs:
            continue
        specs.append(core.FactorSpec(**{**asdict(spec), "factor_id": f"R{start_id + len(specs):03d}"}))
        if len(specs) == count:
            return specs
    raise RuntimeError(f"only found {len(specs)} new specs")


def make_readme(spec: Any, metrics: dict[str, Any]) -> str:
    return f"""# {spec.name_cn}

中文 | [English](#english)

## 中文

`{spec.name_cn}` 是一个框架中立的 OHLCV 因子 Skill，属于 `{spec.category_cn}` 类。它只依赖用户传入的行情字段，不绑定任何交易框架或数据供应商。

### 因子逻辑

```text
{spec.formula_cn}
```

{spec.rationale_cn}

### 能做什么

- 从 `open/high/low/close/volume` 计算一个可排序的横截面因子值
- 输出简单的分位数多空信号，方便 agent 做研究原型
- 可嵌入用户自己的数据源、股票池、调仓频率和交易成本模型

### 真实数据验证

- 样本行数: `{metrics['sample_rows']}`
- 可用行数: `{metrics['usable_rows']}`
- 市场覆盖: `{json.dumps(metrics.get('markets', {}), ensure_ascii=False)}`
- 覆盖率: `{metrics['coverage']:.4f}`
- 5日 Rank IC 均值: `{metrics['ic_mean_5d']:.6f}`
- 5日 ICIR: `{metrics['icir_5d']:.4f}`
- 五分组 Q5-Q1 均值: `{metrics['long_short_mean_5d']:.6f}`
- Top 组换手: `{metrics['turnover_top_quintile']:.4f}`
- 无未来函数检查: `{metrics.get('no_future_check')}`
- 状态: `{metrics['status']}`

详细结果见 `validation_real/report.md` 和 `validation_real/result.json`。

## English

`{spec.name_en}` is a framework-neutral OHLCV factor Skill in the `{spec.category_en}` family. It depends only on caller-supplied market fields and is not tied to any trading framework or data vendor.

### Factor Logic

```text
{spec.formula_en}
```

{spec.rationale_en}

### What It Does

- Computes a cross-sectionally sortable factor from `open/high/low/close/volume`
- Emits simple quantile long/short prototype signals for agent research workflows
- Lets the caller plug in their own market data, universe, rebalance calendar, and cost model

### Real-Data Validation

- Sample rows: `{metrics['sample_rows']}`
- Usable rows: `{metrics['usable_rows']}`
- Markets: `{json.dumps(metrics.get('markets', {}), ensure_ascii=False)}`
- Coverage: `{metrics['coverage']:.4f}`
- 5-day Rank IC mean: `{metrics['ic_mean_5d']:.6f}`
- 5-day ICIR: `{metrics['icir_5d']:.4f}`
- Quintile Q5-Q1 mean: `{metrics['long_short_mean_5d']:.6f}`
- Top-quintile turnover: `{metrics['turnover_top_quintile']:.4f}`
- No-lookahead check: `{metrics.get('no_future_check')}`
- Status: `{metrics['status']}`
"""


def make_skill(core: Any, spec: Any) -> str:
    return f"""---
name: {core.safe_skill_name(spec.slug)}
description: Use when computing the {spec.name_en} factor from user-supplied OHLCV data or reviewing its bundled real-data validation metrics.
---

# {spec.name_en}

Use this Skill to compute `{spec.name_cn}` / `{spec.name_en}` from caller-provided OHLCV data.

## Workflow

1. Load a `pandas.DataFrame` with `open`, `high`, `low`, `close`, `volume`; include `date` and `symbol` for cross-sectional research.
2. Call `scripts/factor.py::compute_factor(df)` to compute the factor column.
3. Call `generate_signals(df)` for a simple rank-based long/short signal.
4. Review `validation_real/report.md` before using the factor in a model.

## Runtime Contract

- Framework-neutral Python: `pandas` and `numpy`.
- The caller owns data vendor, universe, calendar, costs, slippage, and execution modeling.
"""


def write_batch_report(core: Any, output_root: Path, report_name: str, metrics_rows: list[dict[str, Any]]) -> None:
    manifest = read_json(core.PANEL_ROOT / "panel_manifest.json")
    pass_count = sum(1 for row in metrics_rows if row.get("status") == "pass")
    report = f"""# 追加因子真实数据评价报告

## 数据口径

- 面板行数: `{manifest.get('rows')}`
- 标的数量: `{manifest.get('symbols')}`
- 市场覆盖: `{json.dumps(manifest.get('markets', {}), ensure_ascii=False)}`
- 日期范围: `{manifest.get('start')}` 到 `{manifest.get('end')}`
- 行情供应: `{', '.join(manifest.get('sources', []))}`

本批次复用 QuantSkills 因子生产流程，并跳过已提供索引中的 slug。

## 验证结果

- 新增数量: `{len(metrics_rows)}`
- 通过数量: `{pass_count}`
- 复核/错误: `{len(metrics_rows) - pass_count}`
- 输出目录: `{output_root.name}/`
- 汇总文件: `{output_root.name}/validation_summary_real.json`

### 类别汇总

{core.format_category_rows(metrics_rows)}

### Top Absolute IC

{core.format_top_rows(metrics_rows, 'name_cn')}
"""
    core.write_text(core.REPORT_ROOT / report_name, report)


def generate(args: argparse.Namespace) -> dict[str, Any]:
    project_root = Path(args.project_root).resolve()
    core = import_core(project_root)
    panel = pd.read_parquet(project_root / args.panel)
    output_root = (project_root / args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    existing_indexes = [(project_root / value).resolve() for value in args.existing_index]
    specs = make_specs(core, existing_indexes, args.count, args.start_id)
    metrics_rows = []
    for i, spec in enumerate(specs, start=1):
        folder = output_root / f"{spec.factor_id}-{spec.name_cn}"
        metrics = core.validate_spec(panel, spec)
        metrics_rows.append(metrics)
        for sub in ["scripts", "references", "agents", "validation_real"]:
            (folder / sub).mkdir(parents=True, exist_ok=True)
        core.write_text(folder / "scripts" / "factor.py", core.FACTOR_TEMPLATE.replace("{spec_json}", json.dumps(asdict(spec), ensure_ascii=False, indent=2)).strip() + "\n")
        core.write_text(folder / "scripts" / "validate.py", core.VALIDATE_TEMPLATE.strip() + "\n")
        core.write_text(folder / "README.md", make_readme(spec, metrics))
        core.write_text(folder / "SKILL.md", make_skill(core, spec))
        core.write_json(folder / "validation_real" / "result.json", metrics)
        core.write_text(folder / "validation_real" / "report.md", core.validation_report(spec.name_cn, metrics))
        core.write_text(folder / "references" / "formula.md", f"# {spec.name_cn}\n\n```text\n{spec.formula_en}\n```\n\n```json\n{json.dumps(spec.params, ensure_ascii=False, indent=2)}\n```\n")
        core.write_text(folder / "agents" / "openai.yaml", f'''interface:\n  display_name: "{spec.name_cn}"\n  short_description: "Real-data validated {spec.category_en} OHLCV factor."\n  default_prompt: "Use ${core.safe_skill_name(spec.slug)} to compute this factor from my OHLCV DataFrame."\npolicy:\n  allow_implicit_invocation: true\n''')
        if i % 50 == 0:
            print(f"generated and validated {i}/{args.count}", file=sys.stderr)
    core.write_json(output_root / "factor_index.json", [asdict(spec) for spec in specs])
    core.write_json(output_root / "validation_summary_real.json", metrics_rows)
    pass_count = sum(1 for row in metrics_rows if row.get("status") == "pass")
    core.write_text(output_root / ".gitignore", "__pycache__/\n*.pyc\n")
    if args.combined_index:
        combined_rows = []
        for index_path in existing_indexes:
            if index_path.exists():
                combined_rows.extend(read_json(index_path))
        combined_rows.extend(asdict(spec) for spec in specs)
        core.write_json(project_root / args.combined_index, combined_rows)
    if args.report_name:
        write_batch_report(core, output_root, args.report_name, metrics_rows)
    return {"generated": len(metrics_rows), "pass": pass_count, "output": str(output_root)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--panel", default="real_market_data/panels/ohlcv_panel.parquet")
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--start-id", type=int, required=True)
    parser.add_argument("--existing-index", action="append", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--combined-index")
    parser.add_argument("--report-name")
    args = parser.parse_args()
    print(json.dumps(generate(args), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
