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


# "clustered" is intentionally included even if only a subset of scenarios exists.
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
    1: "ZONE 1: 1 MB TASKOUTPUT",
    2: "ZONE 2: 5 MB TASKOUTPUT",
    3: "ZONE 3: 20 MB TASKOUTPUT",
}

ZONE_SCENARIOS = {
    1: [(50, 1000), (100, 1000), (200, 1000)],
    2: [(10, 5000), (20, 5000), (30, 5000)],
    3: [(1, 20000), (2, 20000), (5, 20000)],
}

SCENARIO_LABELS = {
    (50, 1000): "1 MB\n50 rps",
    (100, 1000): "1 MB\n100 rps",
    (200, 1000): "1 MB\n200 rps",
    (10, 5000): "5 MB\n10 rps",
    (20, 5000): "5 MB\n20 rps",
    (30, 5000): "5 MB\n30 rps",
    (1, 20000): "20 MB\n1 rps",
    (2, 20000): "20 MB\n2 rps",
    (5, 20000): "20 MB\n5 rps",
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
    # Historical file results are split by zone, e.g. file_zone1/file_zone2/file_zone3_1/file_zone3_2.
    if mode.startswith("file_zone"):
        return "file"

    # Allow either naming convention for future clustered runs.
    if mode in ("clustered-infinispan", "clustered"):
        return "clustered"

    return mode


def extract_mode_from_filename(path: str) -> str | None:
    name = os.path.basename(path)
    match = re.search(r"results-taskoutput-handling-(.*?)-\d{8}-\d{6}\.txt$", name)
    if not match:
        return None
    return normalize_mode(match.group(1))


def assign_zone(rate: int, prebuilt_size_kb: int) -> int:
    scenario = (rate, prebuilt_size_kb)
    for zone, scenarios in ZONE_SCENARIOS.items():
        if scenario in scenarios:
            return zone
    raise ValueError(f"Unexpected scenario: RATE={rate} PREBUILT_SIZE_KB={prebuilt_size_kb}")


def parse_k6_log(path: str) -> dict[tuple[int, tuple[int, int]], float]:
    current_scenario = None
    current_zone = None
    results: dict[tuple[int, tuple[int, int]], float] = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            run_match = re.search(r"RUN:\s+RATE=(\d+)\s+\|\s+PREBUILT_SIZE_KB=(\d+)", line)
            if run_match:
                rate = int(run_match.group(1))
                prebuilt_size_kb = int(run_match.group(2))
                current_scenario = (rate, prebuilt_size_kb)
                current_zone = assign_zone(rate, prebuilt_size_kb)

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


def collect_data(input_dir: Path) -> dict[str, dict[tuple[int, tuple[int, int]], float]]:
    data: dict[str, dict[tuple[int, tuple[int, int]], float]] = {mode: {} for mode in MODES}

    files = sorted(glob.glob(str(input_dir / "results-taskoutput-handling-*.txt")))
    if not files:
        raise RuntimeError(f"No results-taskoutput-handling-*.txt files found in {input_dir}")

    for file_path in files:
        mode = extract_mode_from_filename(file_path)
        if mode in MODES:
            # Merge because file mode may be split across several zone files.
            data[mode].update(parse_k6_log(file_path))

    missing_modes = [mode for mode in MODES if not data[mode]]
    if missing_modes:
        raise RuntimeError(f"Missing result files for modes: {', '.join(missing_modes)}")

    # Only clustered is allowed to be partial because some payload/rate combinations are too heavy.
    missing_required = []
    missing_clustered = []
    for mode in MODES:
        for zone, scenarios in ZONE_SCENARIOS.items():
            for scenario in scenarios:
                key = (zone, scenario)
                if key not in data[mode]:
                    msg = f"{mode}: zone {zone}, RATE={scenario[0]}, PREBUILT_SIZE_KB={scenario[1]}"
                    if mode == "clustered":
                        missing_clustered.append(msg)
                    else:
                        missing_required.append(msg)

    if missing_required:
        raise RuntimeError("Missing parsed scenarios:\n" + "\n".join(missing_required))

    if missing_clustered:
        print("WARNING: clustered mode has missing scenarios; those bars will be omitted:")
        for item in missing_clustered:
            print(f"  - {item}")

    return data


def y_formatter(value, _pos):
    if value >= 1000:
        return f"{int(value):,}"
    if value >= 1:
        return f"{value:g}"
    return f"{value:.1f}"


def plot_chart(data: dict[str, dict[tuple[int, tuple[int, int]], float]], output: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)

    bar_width = 0.095
    offsets = (np.arange(len(MODES)) - (len(MODES) - 1) / 2) * bar_width

    for zone, ax in zip([1, 2, 3], axes):
        scenarios = ZONE_SCENARIOS[zone]
        x = np.arange(len(scenarios))

        for idx, mode in enumerate(MODES):
            for scenario_idx, scenario in enumerate(scenarios):
                key = (zone, scenario)
                if key not in data[mode]:
                    continue

                ax.bar(
                    x[scenario_idx] + offsets[idx],
                    data[mode][key],
                    width=bar_width,
                    label=mode if scenario_idx == 0 else "_nolegend_",
                    color=MODE_COLORS[mode],
                    edgecolor="white",
                    linewidth=0.7,
                )

        ax.set_title(ZONE_TITLES[zone], fontsize=13, fontweight="bold", pad=12)
        ax.set_xticks(x)
        ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios], fontsize=10)
        ax.set_xlabel("Payload size / request rate", fontsize=11)
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
        "TaskOutput Handling - Average Response Time by Persistence Strategy",
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
    parser.add_argument("--output", default="taskoutput_handling_bar_chart.png")
    args = parser.parse_args()

    data = collect_data(Path(args.input_dir))
    plot_chart(data, Path(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
