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
    1: "ZONE 1: LIGHT LOAD\n20 requests / second",
    2: "ZONE 2: MEDIUM LOAD\n80 requests / second",
    3: "ZONE 3: HIGH LOAD\n150 requests / second",
}

ORDERS = ["order20", "order50", "order100"]


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
    match = re.search(r"results-task-orchestration-(.*?)-\d{8}-\d{6}\.txt$", name)
    return match.group(1) if match else None


def parse_k6_log(path: str) -> dict[tuple[int, str], float]:
    zone = None
    current_order = None
    results: dict[tuple[int, str], float] = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            zone_match = re.search(r"===== ZONE\s+(\d+):", line)
            if zone_match:
                zone = int(zone_match.group(1))

            run_match = re.search(r"RUN:\s+RATE=\d+\s+\|\s+SCRIPT=k6-(order\d+)\.js", line)
            if run_match:
                current_order = run_match.group(1)

            if (
                zone is not None
                and current_order is not None
                and "http_req_duration" in line
                and "avg=" in line
                and "{ expected_response:true }" not in line
            ):
                avg_match = re.search(r"avg=([\d.]+)(ms|s|µs|us)", line)
                if avg_match:
                    results[(zone, current_order)] = parse_duration_ms(avg_match.group(1), avg_match.group(2))
                    current_order = None

    return results


def collect_data(input_dir: Path) -> dict[str, dict[tuple[int, str], float]]:
    data: dict[str, dict[tuple[int, str], float]] = {}

    for file_path in glob.glob(str(input_dir / "results-task-orchestration-*.txt")):
        mode = extract_mode_from_filename(file_path)
        if mode in MODES:
            data[mode] = parse_k6_log(file_path)

    missing_modes = [mode for mode in MODES if mode not in data]
    if missing_modes:
        raise RuntimeError(f"Missing result files for modes: {', '.join(missing_modes)}")

    return data


def y_formatter(value, _pos):
    if value >= 1000:
        return f"{int(value):,}"
    if value >= 1:
        return f"{value:g}"
    return f"{value:.1f}"


def plot_chart(data: dict[str, dict[tuple[int, str], float]], output: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)

    x = np.arange(len(ORDERS))
    bar_width = 0.095
    offsets = (np.arange(len(MODES)) - (len(MODES) - 1) / 2) * bar_width

    for zone, ax in zip([1, 2, 3], axes):
        for idx, mode in enumerate(MODES):
            values = [data[mode][(zone, order)] for order in ORDERS]
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
        ax.set_xticklabels(ORDERS, fontsize=11)
        ax.set_xlabel("Workflow complexity", fontsize=11)
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
        "Task Orchestration - Average Response Time by Persistence Strategy",
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
    parser.add_argument("--output", default="task_orchestration_bar_chart.png")
    args = parser.parse_args()

    data = collect_data(Path(args.input_dir))
    plot_chart(data, Path(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
