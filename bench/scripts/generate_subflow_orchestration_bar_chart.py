#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter


MODES = ["nopersistence", "file", "infinispan", "clustered", "redis", "valkey", "jpa"]

MODE_COLORS = {
    "nopersistence": "#2ca02c",
    "file": "#ff7f0e",
    "infinispan": "#1f77ff",
    "clustered": "#17becf",
    "redis": "#e41a1c",
    "valkey": "#7b2cbf",
    "jpa": "#8c4a2f",
}

ZONE_TITLES = {
    1: "ZONE 1: LOW LOAD\n100 requests / second",
    2: "ZONE 2: MEDIUM LOAD\n200 requests / second",
    3: "ZONE 3: HIGH LOAD\n300 requests / second",
}

# Scenarios are represented as: (rate, script)
ZONE_SCENARIOS = {
    1: [(100, "fork3"), (100, "fork5"), (100, "fork10")],
    2: [(200, "fork3"), (200, "fork5"), (200, "fork10")],
    3: [(300, "fork3"), (300, "fork5"), (300, "fork10")],
}

SCENARIO_LABELS = {
    (100, "fork3"): "fork3",
    (100, "fork5"): "fork5",
    (100, "fork10"): "fork10",
    (200, "fork3"): "fork3",
    (200, "fork5"): "fork5",
    (200, "fork10"): "fork10",
    (300, "fork3"): "fork3",
    (300, "fork5"): "fork5",
    (300, "fork10"): "fork10",
}


def parse_duration_ms(value: str, unit: str) -> float:
    number = float(value)
    if unit == "s":
        return number * 1000.0
    if unit == "ms":
        return number
    if unit in ("µs", "us"):
        return number / 1000.0
    return number


def normalize_mode(mode: str) -> str:
    if mode in ("clustered-infinispan", "clustered"):
        return "clustered"
    return mode


def extract_mode_from_filename(path: str) -> str | None:
    name = os.path.basename(path)
    match = re.search(r"results-subflow-orchestration-(.*?)-\d{8}-\d{6}\.txt$", name)
    if not match:
        return None
    return normalize_mode(match.group(1))


def assign_zone(rate: int, script_name: str) -> int:
    scenario = (rate, script_name)
    for zone, scenarios in ZONE_SCENARIOS.items():
        if scenario in scenarios:
            return zone
    raise ValueError(f"Unexpected scenario: RATE={rate} SCRIPT=k6-{script_name}.js")


def parse_k6_log(path: str) -> dict[tuple[int, tuple[int, str]], float]:
    current_scenario = None
    current_zone = None
    results: dict[tuple[int, tuple[int, str]], float] = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            run_match = re.search(r"RUN:\s+RATE=(\d+)\s+\|\s+SCRIPT=k6-(fork\d+)\.js", line)
            if run_match:
                rate = int(run_match.group(1))
                script_name = run_match.group(2)
                current_scenario = (rate, script_name)
                current_zone = assign_zone(rate, script_name)

            if (
                current_scenario is not None
                and current_zone is not None
                and "http_req_duration" in line
                and "avg=" in line
                and "{ expected_response:true }" not in line
            ):
                avg_match = re.search(r"avg=([\d.]+)(ms|s|µs|us)", line)
                if avg_match:
                    results[(current_zone, current_scenario)] = parse_duration_ms(
                        avg_match.group(1),
                        avg_match.group(2),
                    )
                    current_scenario = None
                    current_zone = None

    return results


def collect_data(input_dir: Path) -> dict[str, dict[tuple[int, tuple[int, str]], float]]:
    data: dict[str, dict[tuple[int, tuple[int, str]], float]] = {mode: {} for mode in MODES}

    files = sorted(glob.glob(str(input_dir / "results-subflow-orchestration-*.txt")))
    if not files:
        raise RuntimeError(f"No results-subflow-orchestration-*.txt files found in {input_dir}")

    for file_path in files:
        mode = extract_mode_from_filename(file_path)
        if mode in MODES:
            data[mode].update(parse_k6_log(file_path))

    missing_modes = [mode for mode in MODES if not data[mode]]
    if missing_modes:
        raise RuntimeError(f"Missing result files for modes: {', '.join(missing_modes)}")

    missing_scenarios = []
    for mode in MODES:
        for zone, scenarios in ZONE_SCENARIOS.items():
            for scenario in scenarios:
                if (zone, scenario) not in data[mode]:
                    missing_scenarios.append(
                        f"{mode}: zone {zone}, RATE={scenario[0]}, SCRIPT=k6-{scenario[1]}.js"
                    )

    if missing_scenarios:
        raise RuntimeError("Missing parsed scenarios:\n" + "\n".join(missing_scenarios))

    return data


def y_formatter(value, _pos):
    if value >= 1000:
        return f"{int(value):,}"
    if value >= 1:
        return f"{value:g}"
    return f"{value:.1f}"


def plot_chart(
    data: dict[str, dict[tuple[int, tuple[int, str]], float]],
    output: Path,
    log_scale: bool,
    show_values: bool,
) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)

    bar_width = 0.095
    offsets = (np.arange(len(MODES)) - (len(MODES) - 1) / 2) * bar_width

    max_value = max(
        value
        for mode_data in data.values()
        for value in mode_data.values()
    )

    for zone, ax in zip([1, 2, 3], axes):
        scenarios = ZONE_SCENARIOS[zone]
        x = np.arange(len(scenarios))

        for idx, mode in enumerate(MODES):
            for scenario_idx, scenario in enumerate(scenarios):
                key = (zone, scenario)
                value = data[mode][key]
                bar = ax.bar(
                    x[scenario_idx] + offsets[idx],
                    value,
                    width=bar_width,
                    label=mode if scenario_idx == 0 else "_nolegend_",
                    color=MODE_COLORS[mode],
                    edgecolor="white",
                    linewidth=0.7,
                )

                if show_values:
                    ax.bar_label(
                        bar,
                        labels=[f"{value:.1f}"],
                        padding=3,
                        fontsize=7,
                        rotation=90,
                    )

        ax.set_title(ZONE_TITLES[zone], fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], fontsize=10)
        ax.set_xlabel("Subflow fan-out", fontsize=11)
        ax.grid(axis="y", which="major", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_axisbelow(True)

        if log_scale:
            ax.set_yscale("log")
            ax.set_ylim(1, max(10000, max_value * 1.3))
        else:
            ax.set_ylim(0, max_value * 1.15)

    ylabel = "Average response time (ms, log scale)" if log_scale else "Average response time (ms)"
    axes[0].set_ylabel(ylabel, fontsize=12)
    axes[0].yaxis.set_major_formatter(FuncFormatter(y_formatter))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.94),
        ncol=len(MODES),
        frameon=False,
        fontsize=11,
    )

    fig.suptitle(
        "Subflow Orchestration - Average Response Time by Persistence Strategy",
        fontsize=18,
        fontweight="bold",
        y=0.99,
    )

    fig.tight_layout(rect=[0.03, 0.05, 0.99, 0.88])
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=".", help="Directory containing k6 result txt files")
    parser.add_argument("--output", default="subflow_orchestration_bar_chart.png")
    parser.add_argument(
        "--linear",
        action="store_true",
        help="Use linear y-axis instead of the default log scale",
    )
    parser.add_argument(
        "--show-values",
        action="store_true",
        help="Print exact average values above the bars",
    )
    args = parser.parse_args()

    data = collect_data(Path(args.input_dir))
    plot_chart(
        data=data,
        output=Path(args.output),
        log_scale=not args.linear,
        show_values=args.show_values,
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
