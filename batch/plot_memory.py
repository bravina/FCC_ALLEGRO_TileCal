#!/usr/bin/env python3
"""
plot_memory.py  —  Parse HTCondor .log files and plot memory usage for
simulation and reconstruction jobs.

Usage:
    python batch/plot_memory.py --config batch/config.yaml
    python batch/plot_memory.py --config batch/config.yaml --output memory.pdf
    python batch/plot_memory.py --config batch/config.yaml --sample ttbar_ecm365
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path

import yaml

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("WARNING: matplotlib/numpy not found. Install with: pip install matplotlib numpy")


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

# Matches the "Memory (MB)  :  6281  9000  9000" line inside a termination block
RE_MEMORY = re.compile(
    r"Memory \(MB\)\s*:\s*(\d+)\s+(\d+)\s+(\d+)"
)
# Marks the start of a termination event block
RE_TERMINATE = re.compile(r"^005 \(")


def parse_log(path: Path) -> list[dict]:
    """Parse a single HTCondor .log file and return a list of termination records.
    Each record has: usage_mb, request_mb, allocated_mb.
    A log file may contain multiple termination events if the job was retried.
    """
    records = []
    in_terminate = False
    block_lines = []

    for line in path.read_text(errors="replace").splitlines():
        if RE_TERMINATE.match(line):
            in_terminate = True
            block_lines = [line]
        elif in_terminate:
            block_lines.append(line)
            if line.strip() == "...":
                # End of block — search for memory line
                block = "\n".join(block_lines)
                m = RE_MEMORY.search(block)
                if m:
                    records.append({
                        "usage_mb":     int(m.group(1)),
                        "request_mb":   int(m.group(2)),
                        "allocated_mb": int(m.group(3)),
                    })
                in_terminate = False
                block_lines = []

    return records


def collect_memory(submitdir: Path, tag: str) -> dict:
    """Return {'sim': [...], 'reco': [...]} lists of memory records for a tag."""
    log_dir = submitdir / "logs" / tag
    result = defaultdict(list)
    if not log_dir.exists():
        return result

    for step in ("sim", "reco"):
        log_files = sorted(log_dir.glob(f"{step}_*.log"))
        n = len(log_files)
        if not n:
            continue
        for i, log_file in enumerate(log_files):
            print(f"  [{tag}] {step} {i+1}/{n} ", end="\r", flush=True)
            records = parse_log(log_file)
            # Use the last termination record (most recent attempt)
            if records:
                result[step].append(records[-1])
        print(f"  [{tag}] {step} {n}/{n} — {len(result[step])} records{' '*20}")

    return result


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

COLOURS = [
    "#378ADD", "#D85A30", "#1D9E75", "#D4537E",
    "#BA7517", "#534AB7", "#639922", "#888780",
]


def plot_memory(all_memory: dict[str, dict], output: str) -> None:
    tags_with_sim  = [t for t, d in all_memory.items() if d.get("sim")]
    tags_with_reco = [t for t, d in all_memory.items() if d.get("reco")]

    n_sim  = len(tags_with_sim)
    n_reco = len(tags_with_reco)
    if not n_sim and not n_reco:
        print("No memory data found.")
        return

    n_cols = min(3, max(n_sim, n_reco, 1))
    n_sim_rows  = int(np.ceil(n_sim  / n_cols)) if n_sim  else 0
    n_reco_rows = int(np.ceil(n_reco / n_cols)) if n_reco else 0
    total_rows  = n_sim_rows + n_reco_rows + (1 if n_sim_rows and n_reco_rows else 0)

    fig, axes_flat = plt.subplots(
        total_rows, n_cols,
        figsize=(5 * n_cols, max(4, total_rows * 3.5)),
        squeeze=False,
    )
    for ax in axes_flat.flat:
        ax.set_visible(False)

    row_offset = 0

    def _plot_step(tags, step_label, colour_offset):
        nonlocal row_offset
        if not tags:
            return
        fig.text(
            0.5, 1 - (row_offset * 0.01),
            f"{step_label} memory usage per job",
            ha="center", va="top", fontsize=13, fontweight="bold",
        )
        for idx, tag in enumerate(tags):
            r, c = divmod(idx, n_cols)
            ax = axes_flat[row_offset + r, c]
            ax.set_visible(True)

            records = all_memory[tag][step_label.lower()]
            usage   = [rec["usage_mb"]   / 1024 for rec in records]  # GB
            request = records[0]["request_mb"]   / 1024 if records else None

            colour = COLOURS[(idx + colour_offset) % len(COLOURS)]
            ax.hist(usage, bins=20, color=colour, alpha=0.85,
                    edgecolor="white", linewidth=0.5)
            ax.set_xlabel("Memory usage (GB)", fontsize=10)
            ax.set_ylabel("Jobs", fontsize=10)
            ax.set_title(tag, fontsize=10, pad=4)
            ax.tick_params(labelsize=9)
            ax.spines[["top", "right"]].set_visible(False)

            mean_u = np.mean(usage)
            std_u  = np.std(usage)
            max_u  = np.max(usage)

            # Vertical line for the requested memory
            if request is not None:
                ax.axvline(request, color="black", linestyle="--",
                           linewidth=1.0, label=f"request: {request:.1f} GB")
                ax.legend(fontsize=8)

            ax.text(
                0.97, 0.95,
                f"mean: {mean_u:.2f} ± {std_u:.2f} GB\nmax: {max_u:.2f} GB",
                transform=ax.transAxes,
                ha="right", va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=colour, alpha=0.8),
            )

        row_offset += int(np.ceil(len(tags) / n_cols))

    _plot_step(tags_with_sim,  "Sim",  0)
    if n_sim_rows and n_reco_rows:
        row_offset += 1
    _plot_step(tags_with_reco, "Reco", n_sim)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"Saved: {output}")

    # Summary table
    print()
    print(f"{'Tag':<30}  {'Step':<5}  {'N':>5}  {'Mean (GB)':>10}  "
          f"{'Std (GB)':>9}  {'Max (GB)':>9}  {'Request (GB)':>13}")
    print("-" * 85)
    for tag in sorted(all_memory):
        for step in ("sim", "reco"):
            records = all_memory[tag].get(step, [])
            if not records:
                continue
            usage   = [r["usage_mb"] / 1024 for r in records]
            request = records[0]["request_mb"] / 1024
            print(f"{tag:<30}  {step:<5}  {len(records):>5}  "
                  f"{np.mean(usage):>10.2f}  {np.std(usage):>9.2f}  "
                  f"{np.max(usage):>9.2f}  {request:>13.1f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config",  required=True)
    parser.add_argument("--output",  default="memory.pdf",
                        help="Output plot file (default: memory.pdf)")
    parser.add_argument("--sample",  default=None,
                        help="Filter to tags containing this string")
    args = parser.parse_args()

    if not HAS_MPL:
        print("Install matplotlib and numpy first:  pip install --user matplotlib numpy")
        return

    cfg = yaml.safe_load(open(args.config))
    submitdir = Path(cfg["paths"]["submitdir"])

    def make_tag(s, e):
        ecm_str = f"{e:.3f}".rstrip("0").rstrip(".")
        return f"{s['name']}_ecm{ecm_str}"

    tags = [make_tag(s, e) for s in cfg["samples"] for e in s["ecm"]]
    if args.sample:
        tags = [t for t in tags if args.sample in t]

    print(f"Scanning {len(tags)} sample(s) in {submitdir}/logs/ ...")
    all_memory = {}
    for t in tags:
        memory = collect_memory(submitdir, t)
        if memory:
            all_memory[t] = memory

    if not all_memory:
        print("No .log files with memory information found yet.")
        return

    plot_memory(all_memory, args.output)


if __name__ == "__main__":
    main()
