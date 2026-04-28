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
    1: "ZONE 1: LIGHT LOAD\n20 rps / 1,000 items",
    2: "ZONE 2: HIGH THROUGHPUT\n150 rps / 1,000 items",
    3: "ZONE 3: HEAVY PROCESSING\n5 rps / 1,000 items; 1 rps / 10,000 items",
}

ZONE_SCENARIOS = {
    1: [(20, 1000, 10), (20, 1000, 100), (20, 1000, 300)],
    2: [(150, 1000, 10), (150, 1000, 30), (150, 1000, 60), (150, 1000, 80), (150, 1000, 100)],
    3: [(5, 1000, 300), (5, 1000, 600), (5, 1000, 1000), (1, 10000, 300)],
}

SCENARIO_LABELS = {
    (20, 1000, 10): "1k×10",
    (20, 1000, 100): "1k×100",
    (20, 1000, 300): "1k×300",
    (150, 1000, 10): "1k×10",
    (150, 1000, 30): "1k×30",
    (150, 1000, 60): "1k×60",
    (150, 1000, 80): "1k×80",
    (150, 1000, 100): "1k×100",
    (5, 1000, 300): "1k×300",
    (5, 1000, 600): "1k×600",
    (5, 1000, 1000): "1k×1000",
    (1, 10000, 300): "10k×300",
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


def extract_mode_from_filename(path: str) -> str | None:
    name = os.path.basename(path)
    match = re.search(r"results-json-(.*?)-\d{8}-\d{6}\.txt$", name)
    return match.group(1) if match else None


def assign_zone(rate: int, items: int, iterations: int) -> int:
    scenario = (rate, items, iterations)
    for zone, scenarios in ZONE_SCENARIOS.items():
        if scenario in scenarios:
            return zone
    raise ValueError(f"Unexpected scenario: RATE={rate} ITEMS={items} ITERATIONS={iterations}")


def parse_k6_log(path: str) -> dict[tuple[int, tuple[int, int, int]], float]:
    current_scenario = None
    current_zone = None
    results: dict[tuple[int, tuple[int, int, int]], float] = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            run_match = re.search(r"RUN:\s+RATE=(\d+)\s+\|\s+ITEMS=(\d+)\s+\|\s+ITERATIONS=(\d+)", line)
            if run_match:
                rate = int(run_match.group(1))
                items = int(run_match.group(2))
                iterations = int(run_match.group(3))
                current_scenario = (rate, items, iterations)
                current_zone = assign_zone(rate, items, iterations)

            if (
                current_scenario is not None
                and current_zone is not None
                and "http_req_duration" in line
                and "avg=" in line
                and "{ expected_response:true }" not in line
            ):
                avg_match = re.search(r"avg=([\d.]+)(ms|s|µs|us)", line)
                if avg_match:
                    results[(current_zone, current_scenario)] = parse_duration_ms(avg_match.group(1), avg_match.group(2))
                    current_scenario = None
                    current_zone = None

    return results


def collect_data(input_dir: Path) -> dict[str, dict[tuple[int, tuple[int, int, int]], float]]:
    data = {}

    for file_path in glob.glob(str(input_dir / "results-json-*.txt")):
        mode = extract_mode_from_filename(file_path)
        if mode in MODES:
            data[mode] = parse_k6_log(file_path)

    missing_modes = [mode for mode in MODES if mode not in data]
    if missing_modes:
        raise RuntimeError(f"Missing result files for modes: {', '.join(missing_modes)}")

    missing_scenarios = []
    for mode in MODES:
        for zone, scenarios in ZONE_SCENARIOS.items():
            for scenario in scenarios:
                if (zone, scenario) not in data[mode]:
                    missing_scenarios.append(f"{mode}: zone {zone}, {scenario}")

    if missing_scenarios:
        raise RuntimeError("Missing parsed scenarios:\n" + "\n".join(missing_scenarios))

    return data


def y_formatter(value, _pos):
    if value >= 1000:
        return f"{int(value):,}"
    if value >= 1:
        return f"{value:g}"
    return f"{value:.1f}"


def plot_chart(data, output: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)

    bar_width = 0.095
    offsets = (np.arange(len(MODES)) - (len(MODES) - 1) / 2) * bar_width

    for zone, ax in zip([1, 2, 3], axes):
        scenarios = ZONE_SCENARIOS[zone]
        x = np.arange(len(scenarios))

        for idx, mode in enumerate(MODES):
            values = [data[mode][(zone, scenario)] for scenario in scenarios]
            ax.bar(
                x + offsets[idx],
                values,
                width=bar_width,
                label=mode,
                color=MODE_COLORS[mode],
                edgecolor="white",
                linewidth=0.7,
            )

        ax.set_title(ZONE_TITLES[zone], fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], fontsize=10)
        ax.set_xlabel("Items × iterations", fontsize=11)
        ax.set_yscale("log")
        ax.grid(axis="y", which="major", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_axisbelow(True)
        ax.set_ylim(1, 10000)

    axes[0].set_ylabel("Average response time (ms, log scale)", fontsize=12)
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
        "JSON / TaskOutput Processing - Average Response Time by Persistence Strategy",
        fontsize=18,
        fontweight="bold",
        y=0.99,
    )

    fig.tight_layout(rect=[0.03, 0.05, 0.99, 0.88])
    fig.savefig(output, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=".", help="Directory containing k6 result txt files")
    parser.add_argument("--output", default="taskoutput_processing_bar_chart.png")
    args = parser.parse_args()

    data = collect_data(Path(args.input_dir))
    plot_chart(data, Path(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
