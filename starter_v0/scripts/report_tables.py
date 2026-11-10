"""Build the REPORT.md Part B tables (B1-B4) from real logs.

Run from starter_v0/:
    python scripts/report_tables.py                      # print markdown
    python scripts/report_tables.py --output analysis/report_tables.md

Sources:
    B1  artifacts/version_log.csv
    B2  failed cases in the newest suite=base run (or --base-run)
    B3  data/eval_group.json + results from the newest suite=group run (or --group-run)
    B4  every turn in transcripts/*.transcript.json

The "Fix" column in B2 is left empty on purpose: the team writes it by hand.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def cell(value: Any, limit: int = 160) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 3] + "..."


def table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(cell(value) for value in row) + " |" for row in rows]
    if not rows:
        lines.append("| " + " | ".join(["(chưa có dữ liệu)"] + [""] * (len(headers) - 1)) + " |")
    return "\n".join(lines)


def short_arg(value: Any) -> str:
    """Shorten long args (digest text, item lists) so small args like confirmed=true stay visible."""
    if isinstance(value, list):
        return f"[{len(value)} items]"
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 40 else text[:37] + '..."'


def calls_text(calls: list[dict[str, Any]]) -> str:
    if not calls:
        return "(no tool)"
    return "; ".join(
        f"{c.get('name')}({', '.join(f'{k}={short_arg(v)}' for k, v in (c.get('args') or {}).items())})"
        for c in calls
    )


def expected_text(expect: dict[str, Any]) -> str:
    if expect.get("no_tool"):
        return f"no tool ({expect.get('behavior', 'answer')})"
    return calls_text(expect.get("tool_calls", []))


def load_runs(runs_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    runs = []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            runs.append((path, json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(runs, key=lambda item: item[1].get("generated_at", ""))


def pick_run(runs: list[tuple[Path, dict[str, Any]]], explicit: Path | None, suite: str) -> tuple[Path, dict[str, Any]] | None:
    if explicit:
        return explicit, json.loads(explicit.read_text(encoding="utf-8"))
    matching = [item for item in runs if item[1].get("suite") == suite]
    return matching[-1] if matching else None


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def b1(version_log: Path) -> str:
    rows = []
    if version_log.exists():
        with version_log.open(encoding="utf-8", newline="") as file:
            for row in csv.DictReader(file):
                if (row.get("version") or "").strip():
                    rows.append([row.get("version"), row.get("changed_artifact"), row.get("hypothesis"),
                                 row.get("metric_before"), row.get("metric_after"), row.get("run_file")])
    return table(["Version", "Changed Artifact", "Hypothesis", "Metric Before", "Metric After", "Run File"], rows)


def b2(run: tuple[Path, dict[str, Any]] | None) -> str:
    rows = []
    if run:
        for item in run[1].get("results", []):
            result = item["result"]
            if result.get("passed"):
                continue
            rows.append([item["id"], result.get("failure_type"), calls_text(result.get("actual_tool_calls", [])),
                         "; ".join(result.get("failures", [])), ""])
    source = f"Nguồn: `{relative(run[0])}` (version `{run[1].get('version')}`)\n\n" if run else ""
    return source + table(["Case ID", "Failure Type", "Actual Tool Calls", "What Failed", "Fix"], rows)


def b3(eval_group: Path, run: tuple[Path, dict[str, Any]] | None) -> str:
    results = {item["id"]: item["result"] for item in (run[1].get("results", []) if run else [])}
    rows = []
    if eval_group.exists():
        for case in json.loads(eval_group.read_text(encoding="utf-8")).get("cases", []):
            result = results.get(case["id"])
            if result is None:
                outcome = "(chưa chạy)"
            elif result.get("passed"):
                outcome = "PASS"
            else:
                outcome = f"FAIL: {'; '.join(result.get('failures', []))}"
            kind = "multi" if "turns" in case else "single"
            rows.append([f"{case['id']} ({kind})", case.get("metadata", {}).get("what_it_tests", ""),
                         expected_text(case.get("expect", {})), outcome])
    source = f"Kết quả từ: `{relative(run[0])}` (version `{run[1].get('version')}`)\n\n" if run else ""
    return source + table(["Case ID", "What It Tests", "Expected Tool/Behavior", "Result"], rows)


def b4(transcripts_dir: Path) -> str:
    rows = []
    for path in sorted(transcripts_dir.glob("*.transcript.json")):
        try:
            transcript = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        version = f"{transcript.get('artifact_version')} · {relative(path)}"
        for turn in transcript.get("turns", []):
            calls = [call for item in turn.get("rounds", []) for call in item.get("tool_calls", [])]
            outcome = turn.get("status", "")
            if turn.get("assistant_text"):
                outcome += f": {turn['assistant_text']}"
            elif turn.get("error"):
                outcome += f": {turn['error']}"
            rows.append([turn.get("turn_index"), turn.get("user"), calls_text(calls), version, outcome])
    return table(["Turn", "User Request", "Tool Calls", "Version Evidence", "Outcome"], rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate REPORT.md Part B tables from run logs.")
    parser.add_argument("--version-log", type=Path, default=ROOT / "artifacts" / "version_log.csv")
    parser.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    parser.add_argument("--base-run", type=Path, default=None, help="Run JSON for B2. Default: newest suite=base run.")
    parser.add_argument("--group-run", type=Path, default=None, help="Run JSON for B3. Default: newest suite=group run.")
    parser.add_argument("--eval-group", type=Path, default=ROOT / "data" / "eval_group.json")
    parser.add_argument("--transcripts-dir", type=Path, default=ROOT / "transcripts")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    runs = load_runs(args.runs_dir) if args.runs_dir.exists() else []
    sections = [
        "## B1. Version Evidence\n\n" + b1(args.version_log),
        "## B2. Failure Analysis\n\n" + b2(pick_run(runs, args.base_run, "base")),
        "## B3. Team Eval Cases\n\n" + b3(args.eval_group, pick_run(runs, args.group_run, "group")),
        "## B4. Live Chat Evidence\n\n" + b4(args.transcripts_dir),
    ]
    markdown = "\n\n".join(sections) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Saved {args.output}")
    else:
        print(markdown)


if __name__ == "__main__":
    main()
