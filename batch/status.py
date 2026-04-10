#!/usr/bin/env python3
"""
status.py  —  Show pipeline status per (sample, ECM) and per step.

Usage:
    python batch/status.py --config batch/config.yaml
    python batch/status.py --config batch/config.yaml --sample ttbar_ecm365
    python batch/status.py --config batch/config.yaml --failed   # show failed job names
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path

import yaml

STEP_ORDER = ["gen", "sim", "reco", "merge", "ntuple"]

# HTCondor log event codes
# https://htcondor.readthedocs.io/en/latest/classad-attributes/job-classad-attributes.html
EVT_SUBMIT    = 0
EVT_START     = 1
EVT_TERMINATE = 5
EVT_EVICT     = 4
EVT_HOLD      = 12
EVT_RELEASE   = 13
EVT_ABORT     = 9

TERM_NORMAL   = "Normal"
TERM_SIGNAL   = "Signal"


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def sample_tag(name: str, ecm: float) -> str:
    ecm_str = f"{ecm:.3f}".rstrip("0").rstrip(".")
    return f"{name}_ecm{ecm_str}"


def parse_log(log_path: Path) -> dict[str, dict]:
    """Parse an HTCondor event log file.
    Returns {job_name: {state, exit_code, host}} where state is one of:
    idle, running, done, failed, held, evicted.
    Job name is inferred from the log filename (one log per job).
    """
    if not log_path.exists():
        return {}

    # Log filename pattern: <job_name>.<ClusterId>.log
    # We derive the job name from the parent directory + stem
    stem = log_path.stem  # e.g. gen_ttbar_ecm365_0000.10169854
    job_name = stem.rsplit(".", 1)[0]

    state = "idle"
    exit_code = None

    text = log_path.read_text(errors="replace")

    # HTCondor log events are separated by "..."
    for block in text.split("..."):
        block = block.strip()
        if not block:
            continue

        first_line = block.splitlines()[0] if block.splitlines() else ""
        # Event code is the 3-digit number at the start: "005 (12345.000.000)"
        m = re.match(r"^(\d{3})\s", first_line)
        if not m:
            continue
        code = int(m.group(1))

        if code == EVT_SUBMIT:
            state = "idle"
        elif code == EVT_START:
            state = "running"
        elif code == EVT_HOLD:
            state = "held"
        elif code == EVT_EVICT:
            state = "evicted"
        elif code == EVT_ABORT:
            state = "failed"
        elif code == EVT_TERMINATE:
            # Check normal termination and return value
            if "Normal termination" in block:
                m2 = re.search(r"Return value (\d+)", block)
                exit_code = int(m2.group(1)) if m2 else 0
                state = "done" if exit_code == 0 else "failed"
            else:
                state = "failed"

    return {job_name: {"state": state, "exit_code": exit_code}}


def collect_log_states(submitdir: Path, tag: str) -> dict[str, dict]:
    """Read all log files for a given tag and return merged job state dict."""
    log_dir = submitdir / "logs" / tag
    states = {}
    if not log_dir.exists():
        return states
    for log_file in sorted(log_dir.glob("*.log")):
        states.update(parse_log(log_file))
    return states


def step_of(job_name: str) -> str:
    for step in STEP_ORDER:
        if job_name.startswith(f"{step}_"):
            return step
    return "unknown"


def format_bar(done: int, running: int, failed: int, held: int, total: int,
               width: int = 30) -> str:
    """Simple ASCII progress bar."""
    if total == 0:
        return "[" + "-" * width + "]"
    done_w    = int(done    / total * width)
    run_w     = int(running / total * width)
    fail_w    = int(failed  / total * width)
    held_w    = int(held    / total * width)
    idle_w    = width - done_w - run_w - fail_w - held_w
    bar = ("█" * done_w + "▶" * run_w + "✗" * fail_w +
           "H" * held_w + "·" * idle_w)
    return f"[{bar}]"


STATE_COLOURS = {
    "done":    "\033[32m",   # green
    "running": "\033[34m",   # blue
    "failed":  "\033[31m",   # red
    "held":    "\033[33m",   # yellow
    "evicted": "\033[33m",
    "idle":    "\033[0m",
}
RESET = "\033[0m"


def colour(text: str, state: str) -> str:
    return STATE_COLOURS.get(state, "") + text + RESET


def print_tag_status(tag: str, states: dict[str, dict],
                     show_failed: bool) -> None:
    # Group by step
    by_step: dict[str, list] = defaultdict(list)
    for job_name, info in states.items():
        by_step[step_of(job_name)].append((job_name, info))

    print(f"  {'Step':<8}  {'Done':>6}  {'Run':>6}  {'Fail':>6}  "
          f"{'Held':>6}  {'Idle':>6}  {'Total':>6}  Progress")
    print("  " + "-" * 85)

    any_failed = False
    for step in STEP_ORDER:
        jobs = by_step.get(step, [])
        if not jobs:
            continue
        counts = defaultdict(int)
        failed_names = []
        for job_name, info in jobs:
            counts[info["state"]] += 1
            if info["state"] == "failed":
                failed_names.append(job_name)
        total = len(jobs)
        done    = counts["done"]
        running = counts["running"]
        failed  = counts["failed"]
        held    = counts["held"]
        idle    = counts["idle"] + counts["evicted"]

        bar = format_bar(done, running, failed, held, total)

        # Overall step state for colouring
        if failed:
            step_state = "failed"
        elif done == total:
            step_state = "done"
        elif running:
            step_state = "running"
        else:
            step_state = "idle"

        # Use a fixed-width placeholder for the coloured step name
        # (ANSI codes add invisible characters that confuse f-string alignment)
        step_coloured = colour(step, step_state)
        padding = " " * (8 - len(step))
        print(f"  {step_coloured}{padding}  "
              f"{done:>6}  {running:>6}  {failed:>6}  "
              f"{held:>6}  {idle:>6}  {total:>6}  {bar}")

        if show_failed and failed_names:
            any_failed = True
            for name in failed_names:
                ec = states[name]["exit_code"]
                ec_str = f"(exit {ec})" if ec is not None else ""
                print(f"           {colour('FAILED', 'failed')} {name} {ec_str}")

    if not any(by_step.values()):
        print("  No log files found — jobs may not have started yet.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True)
    parser.add_argument("--sample", default=None,
                        help="Filter to a specific sample tag, e.g. ttbar_ecm365")
    parser.add_argument("--failed", action="store_true",
                        help="Also print names of failed jobs")
    args = parser.parse_args()

    cfg = load_config(args.config)
    submitdir = Path(cfg["paths"]["submitdir"])

    tags = []
    for sample in cfg["samples"]:
        for ecm in sample["ecm"]:
            tags.append(sample_tag(sample["name"], ecm))

    if args.sample:
        tags = [t for t in tags if args.sample in t]
        if not tags:
            print(f"No tags matching '{args.sample}'")
            return

    print(f"Pipeline status  —  submitdir: {submitdir}")
    print(f"{'Tag'}")
    print("=" * 82)

    for tag in tags:
        states = collect_log_states(submitdir, tag)
        if not states and not args.sample:
            # Skip tags with no logs at all unless explicitly requested
            continue
        total = len(states)
        done  = sum(1 for s in states.values() if s["state"] == "done")
        failed = sum(1 for s in states.values() if s["state"] == "failed")
        tag_state = "failed" if failed else ("done" if done == total and total else "running")
        print(f"\n{colour(tag, tag_state)}  ({done}/{total} done"
              + (f", {colour(str(failed)+' failed', 'failed')}" if failed else "") + ")")
        print_tag_status(tag, states, show_failed=args.failed)

    print()


if __name__ == "__main__":
    main()
