#!/usr/bin/env python3
"""
plot_timings.py  —  Parse HTCondor job .out files and plot simulation and
reconstruction timings per sample.

Usage:
    python batch/plot_timings.py --config batch/config.yaml
    python batch/plot_timings.py --config batch/config.yaml --output timings.pdf
    python batch/plot_timings.py --config batch/config.yaml --sample ttbar_ecm365
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path

import yaml

# Optional: fall back gracefully if matplotlib not available
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

# DDSim    INFO Total Time:   917.55 s (User), 20.49 s (System)
RE_SIM_TOTAL = re.compile(
    r"DDSim\s+INFO\s+Total Time:\s+([\d.]+)\s+s\s+\(User\)"
)
# DDSim    INFO StartUp Time: 27.90 s, Processing and Init: 889.65 s (~17.79 s/Event)
RE_SIM_PER_EVENT = re.compile(
    r"DDSim\s+INFO\s+StartUp Time:.*?~([\d.]+)\s+s/Event"
)
# ChronoStatSvc    INFO Time User   : Tot=  116  [s]  #=  1
RE_RECO_TOTAL = re.compile(
    r"ChronoStatSvc\s+INFO\s+Time User\s+:\s+Tot=\s*([\d.]+)\s+\[s\]"
)


def parse_sim_out(path: Path) -> dict | None:
    """Extract sim timing from a single .out file. Returns None if not found."""
    text = path.read_text(errors="replace")
    m_total = RE_SIM_TOTAL.search(text)
    m_per_event = RE_SIM_PER_EVENT.search(text)
    if not m_total:
        return None
    return {
        "total_s": float(m_total.group(1)),
        "per_event_s": float(m_per_event.group(1)) if m_per_event else None,
    }


def parse_reco_out(path: Path) -> dict | None:
    """Extract reco total user time from a single .out file."""
    text = path.read_text(errors="replace")
    # The last match is the overall ChronoStatSvc total
    matches = RE_RECO_TOTAL.findall(text)
    if not matches:
        return None
    total_s = float(matches[-1])
    return {"total_s": total_s}


def collect_timings(submitdir: Path, tag: str) -> dict:
    """Return {'sim': [...], 'reco': [...]} lists of timing dicts for a tag."""
    log_dir = submitdir / "logs" / tag
    result = defaultdict(list)
    if not log_dir.exists():
        return result

    for out_file in sorted(log_dir.glob("sim_*.out")):
        # .out files may be named sim_<tag>_<N>.<ClusterId>.<ProcId>.out
        t = parse_sim_out(out_file)
        if t:
            result["sim"].append(t)

    for out_file in sorted(log_dir.glob("reco_*.out")):
        t = parse_reco_out(out_file)
        if t:
            result["reco"].append(t)

    return result


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

COLOURS = [
    "#378ADD", "#D85A30", "#1D9E75", "#D4537E",
    "#BA7517", "#534AB7", "#639922", "#888780",
]


def plot_timings(all_timings: dict[str, dict], output: str) -> None:
    """
    all_timings: {tag: {'sim': [...], 'reco': [...]}}
    """
    tags_with_sim  = [t for t, d in all_timings.items() if d.get("sim")]
    tags_with_reco = [t for t, d in all_timings.items() if d.get("reco")]

    n_sim_plots  = len(tags_with_sim)
    n_reco_plots = len(tags_with_reco)
    if n_sim_plots == 0 and n_reco_plots == 0:
        print("No timing data found in any .out files.")
        return

    n_cols = min(3, max(n_sim_plots, n_reco_plots, 1))
    n_sim_rows  = int(np.ceil(n_sim_plots  / n_cols)) if n_sim_plots  else 0
    n_reco_rows = int(np.ceil(n_reco_plots / n_cols)) if n_reco_plots else 0
    total_rows = n_sim_rows + n_reco_rows + (1 if n_sim_rows and n_reco_rows else 0)

    fig_height = max(4, total_rows * 3.5)
    fig, axes_flat = plt.subplots(
        total_rows, n_cols,
        figsize=(5 * n_cols, fig_height),
        squeeze=False,
    )
    # Hide all axes initially
    for ax in axes_flat.flat:
        ax.set_visible(False)

    row_offset = 0

    # ---- Simulation histograms ----
    if tags_with_sim:
        fig.text(0.5, 1 - 0.01 / total_rows,
                 "Simulation total wall time per job",
                 ha="center", va="top", fontsize=13, fontweight="bold")

        for idx, tag in enumerate(tags_with_sim):
            r, c = divmod(idx, n_cols)
            ax = axes_flat[row_offset + r, c]
            ax.set_visible(True)

            data = all_timings[tag]["sim"]
            totals = [d["total_s"] / 60 for d in data]          # minutes
            per_ev = [d["per_event_s"] for d in data if d["per_event_s"] is not None]

            colour = COLOURS[idx % len(COLOURS)]
            ax.hist(totals, bins=20, color=colour, alpha=0.85, edgecolor="white", linewidth=0.5)
            ax.set_xlabel("Total time (min)", fontsize=10)
            ax.set_ylabel("Jobs", fontsize=10)
            ax.set_title(tag, fontsize=10, pad=4)
            ax.tick_params(labelsize=9)
            ax.spines[["top", "right"]].set_visible(False)

            if per_ev:
                mean_pe = np.mean(per_ev)
                std_pe  = np.std(per_ev)
                ax.text(
                    0.97, 0.95,
                    f"{mean_pe:.1f} ± {std_pe:.1f} s/event",
                    transform=ax.transAxes,
                    ha="right", va="top", fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=colour, alpha=0.8),
                )

        row_offset += n_sim_rows

    # ---- Spacer row ----
    if n_sim_rows and n_reco_rows:
        row_offset += 1

    # ---- Reconstruction histograms ----
    if tags_with_reco:
        fig.text(0.5, (total_rows - row_offset) / total_rows + 0.01,
                 "Reconstruction total CPU time per job",
                 ha="center", va="bottom", fontsize=13, fontweight="bold")

        for idx, tag in enumerate(tags_with_reco):
            r, c = divmod(idx, n_cols)
            ax = axes_flat[row_offset + r, c]
            ax.set_visible(True)

            data = all_timings[tag]["reco"]
            totals = [d["total_s"] / 60 for d in data]

            colour = COLOURS[(idx + n_sim_plots) % len(COLOURS)]
            ax.hist(totals, bins=20, color=colour, alpha=0.85, edgecolor="white", linewidth=0.5)
            ax.set_xlabel("Total time (min)", fontsize=10)
            ax.set_ylabel("Jobs", fontsize=10)
            ax.set_title(tag, fontsize=10, pad=4)
            ax.tick_params(labelsize=9)
            ax.spines[["top", "right"]].set_visible(False)

            mean_t = np.mean(totals)
            std_t  = np.std(totals)
            ax.text(
                0.97, 0.95,
                f"{mean_t:.1f} ± {std_t:.1f} min/job",
                transform=ax.transAxes,
                ha="right", va="top", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=colour, alpha=0.8),
            )

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig(output, dpi=150, bbox_inches="tight")
    print(f"Saved: {output}")

    # Also print a summary table
    print()
    print(f"{'Tag':<30}  {'Step':<5}  {'N':>5}  {'Mean (min)':>10}  {'Std (min)':>9}  {'s/event':>8}")
    print("-" * 75)
    for tag in sorted(all_timings):
        for step in ("sim", "reco"):
            data = all_timings[tag].get(step, [])
            if not data:
                continue
            totals = [d["total_s"] / 60 for d in data]
            mean_t = np.mean(totals)
            std_t  = np.std(totals)
            # per-event only available for sim
            if step == "sim":
                per_ev = [d["per_event_s"] for d in data if d["per_event_s"]]
                pe_str = f"{np.mean(per_ev):.1f}" if per_ev else "—"
            else:
                pe_str = "—"
            print(f"{tag:<30}  {step:<5}  {len(data):>5}  {mean_t:>10.1f}  {std_t:>9.1f}  {pe_str:>8}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", default="timings.pdf",
                        help="Output plot file (pdf, png, svg — default: timings.pdf)")
    parser.add_argument("--sample", default=None,
                        help="Filter to tags containing this string")
    args = parser.parse_args()

    if not HAS_MPL:
        print("Install matplotlib and numpy first:  pip install --user matplotlib numpy")
        return

    cfg = yaml.safe_load(open(args.config))
    submitdir = Path(cfg["paths"]["submitdir"])

    def tag(s, e):
        ecm_str = f"{e:.3f}".rstrip("0").rstrip(".")
        return f"{s['name']}_ecm{ecm_str}"

    tags = [tag(s, e) for s in cfg["samples"] for e in s["ecm"]]
    if args.sample:
        tags = [t for t in tags if args.sample in t]

    all_timings = {}
    for t in tags:
        timings = collect_timings(submitdir, t)
        if timings:
            all_timings[t] = timings

    if not all_timings:
        print("No .out files with timing information found yet.")
        return

    plot_timings(all_timings, args.output)


if __name__ == "__main__":
    main()
