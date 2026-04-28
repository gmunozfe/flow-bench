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
from matplotlib.ticker import MultipleLocator

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

# Two output charts:
# 1) Short delay: 50 ms and 200 ms, split by rate zones.
# 2) Long delay: 1000 ms, split by rate zones.
SHORT_DELAY_SCENARIOS = {
    1: [(20, 50), (20, 200)],
    2: [(50, 50), (50, 200)],
    3: [(150, 50), (150, 200)],
}

# Long-delay chart intentionally skips 150 rps / 1000 ms because that run is
# saturated by load-generator/concurrency pressure and is not useful for
# persistence-backend comparison.
LONG_DELAY_SCENARIOS = {
    1: [(20, 1000)],
    2: [(50, 1000)],
    # intentionally skip zone 3: (150, 1000)
}

ALL_SCENARIOS = {
    1: [(20, 50), (20, 200), (20, 1000)],
    2: [(50, 50), (50, 200), (50, 1000)],
    3: [(150, 50), (150, 200), (150, 1000)],
}

ZONE_TITLES = {
    1: "ZONE 1: LIGHT LOAD\n20 requests / second",
    2: "ZONE 2: MEDIUM LOAD\n50 requests / second",
    3: "ZONE 3: HIGH LOAD\n150 requests / second",
}

SCENARIO_LABELS = {
    (20, 50): "50 ms\ndelay",
    (20, 200): "200 ms\ndelay",
    (20, 1000): "1000 ms\ndelay",
    (50, 50): "50 ms\ndelay",
    (50, 200): "200 ms\ndelay",
    (50, 1000): "1000 ms\ndelay",
    (150, 50): "50 ms\ndelay",
    (150, 200): "200 ms\ndelay",
    (150, 1000): "1000 ms\ndelay",
}

for zone, scenarios in LONG_DELAY_SCENARIOS.items():
    ALL_SCENARIOS.setdefault(zone, [])
    ALL_SCENARIOS[zone] = ALL_SCENARIOS[zone] + scenarios


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
    match = re.search(r"results-external-call-(.*?)-\d{8}-\d{6}\.txt$", name)
    if not match:
        return None
    return normalize_mode(match.group(1))


def assign_zone(rate: int, delay_ms: int) -> int:
    scenario = (rate, delay_ms)
    for zone, scenarios in ALL_SCENARIOS.items():
        if scenario in scenarios:
            return zone
    raise ValueError(f"Unexpected scenario: RATE={rate} DELAY_MS={delay_ms}")


def parse_k6_log(path: str) -> dict[tuple[int, tuple[int, int]], float]:
    current_scenario = None
    current_zone = None
    results: dict[tuple[int, tuple[int, int]], float] = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            run_match = re.search(r"RUN:\s+RATE=(\d+)\s+\|\s+DELAY_MS=(\d+)", line)
            if run_match:
                rate = int(run_match.group(1))
                delay_ms = int(run_match.group(2))
                current_scenario = (rate, delay_ms)
                current_zone = assign_zone(rate, delay_ms)

            if (
                current_scenario is not None
                and current_zone is not None
                and "external_call_overhead_ms" in line
                and "avg=" in line
            ):
                avg_match = re.search(r"avg=([\d.]+)", line)
                if avg_match:
                    results[(current_zone, current_scenario)] = float(avg_match.group(1))
                    current_scenario = None
                    current_zone = None

    return results


def collect_data(input_dir: Path) -> dict[str, dict[tuple[int, tuple[int, int]], float]]:
    data: dict[str, dict[tuple[int, tuple[int, int]], float]] = {mode: {} for mode in MODES}

    files = sorted(glob.glob(str(input_dir / "results-external-call-*.txt")))
    if not files:
        raise RuntimeError(f"No results-external-call-*.txt files found in {input_dir}")

    for file_path in files:
        mode = extract_mode_from_filename(file_path)
        if mode in MODES:
            data[mode].update(parse_k6_log(file_path))

    missing_modes = [mode for mode in MODES if not data[mode]]
    if missing_modes:
        raise RuntimeError(f"Missing result files for modes: {', '.join(missing_modes)}")

    return data


def y_formatter(value, _pos):
    if value >= 1000:
        return f"{int(value):,}"
    if value >= 1:
        return f"{value:g}"
    return f"{value:.1f}"


def missing_scenarios_for_chart(data, scenario_map):
    missing = []
    for mode in MODES:
        for zone, scenarios in scenario_map.items():
            for scenario in scenarios:
                if (zone, scenario) not in data[mode]:
                    missing.append(f"{mode}: zone {zone}, RATE={scenario[0]}, DELAY_MS={scenario[1]}")
    return missing


def plot_chart(
    data: dict[str, dict[tuple[int, tuple[int, int]], float]],
    scenario_map: dict[int, list[tuple[int, int]]],
    output: Path,
    title: str,
    y_min: int,
    y_max: int,
) -> None:
    zones = list(scenario_map.keys())
    fig, axes = plt.subplots(1, len(zones), figsize=(18, 7), sharey=True)
    if len(zones) == 1:
        axes = [axes]

    bar_width = 0.095
    offsets = (np.arange(len(MODES)) - (len(MODES) - 1) / 2) * bar_width

    for zone, ax in zip(zones, axes):
        scenarios = scenario_map[zone]
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
        ax.set_xlabel("External service delay", fontsize=11)
        ax.grid(axis="y", which="major", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_axisbelow(True)
        ax.set_ylim(y_min, y_max)
        ax.yaxis.set_major_locator(MultipleLocator(2))

    axes[0].set_ylabel("Average overhead time (ms)", fontsize=12)
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

    fig.suptitle(title, fontsize=18, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0.03, 0.05, 0.99, 0.88])
    fig.savefig(output, dpi=200)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=".", help="Directory containing k6 result txt files")
    parser.add_argument(
        "--output-prefix",
        default="external_call_bar_chart",
        help="Output prefix. The script writes <prefix>_short_delay.png and <prefix>_long_delay.png",
    )
    args = parser.parse_args()

    data = collect_data(Path(args.input_dir))

    short_missing = missing_scenarios_for_chart(data, SHORT_DELAY_SCENARIOS)
    if short_missing:
        print("WARNING: missing short-delay scenarios; corresponding bars will be omitted:")
        for item in short_missing:
            print(f"  - {item}")

    long_missing = missing_scenarios_for_chart(data, LONG_DELAY_SCENARIOS)
    if long_missing:
        print("WARNING: missing long-delay scenarios; corresponding bars will be omitted:")
        for item in long_missing:
            print(f"  - {item}")

    prefix = Path(args.output_prefix)

    short_output = prefix.with_name(prefix.name + "_short_delay.png")
    long_output = prefix.with_name(prefix.name + "_long_delay.png")

    plot_chart(
        data=data,
        scenario_map=SHORT_DELAY_SCENARIOS,
        output=short_output,
        title="External Call - Short Delay Average Response Time by Persistence Strategy",
        y_min=0,
        y_max=40,
    )

    plot_chart(
        data=data,
        scenario_map=LONG_DELAY_SCENARIOS,
        output=long_output,
        title="External Call - Long Delay Effective Overhead by Persistence Strategy",
        y_min=0,
        y_max=30,
    )

    print(f"Wrote {short_output}")
    print(f"Wrote {long_output}")


if __name__ == "__main__":
    main()
