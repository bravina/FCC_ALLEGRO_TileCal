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


# Matches "DAG Node: gen_ttbar_ecm330_0000" in submit event blocks (EosSubmit)
RE_DAG_NODE = re.compile(r"DAG Node:\s+(\S+)")
# Matches "Cmd: /path/to/gen_ttbar_ecm330_0000.sh" in execute event blocks (fallback)
RE_CMD = re.compile(r"Cmd:\s+\S+/(\w+)\.sh")


def parse_shared_log(log_path: Path) -> dict[str, dict]:
    """Parse a shared HTCondor log file (one per step per tag).
    Returns {job_name: {state, exit_code}} for all jobs in the file.
    Job names are extracted from the Cmd field in execute event blocks.
    """
    if not log_path.exists():
        return {}

    # proc_id -> job_name mapping, built from execute events
    proc_to_name: dict[str, str] = {}
    # proc_id -> {state, exit_code}
    proc_states: dict[str, dict] = {}

    text = log_path.read_text(errors="replace")

    for block in text.split("..."):
        block = block.strip()
        if not block:
            continue

        first_line = block.splitlines()[0] if block.splitlines() else ""
        m = re.match(r"^(\d{3}) \((\d+)\.(\d+)\.\d+\)", first_line)
        if not m:
            continue
        code = int(m.group(1))
        # Use cluster.proc as key — each job is a separate cluster (proc always 0)
        proc = f"{m.group(2)}.{m.group(3)}"

        if proc not in proc_states:
            proc_states[proc] = {"state": "idle", "exit_code": None}

        if code == EVT_SUBMIT:
            proc_states[proc]["state"] = "idle"
            # EosSubmit logs "DAG Node: <job_name>" in submit event
            m_node = RE_DAG_NODE.search(block)
            if m_node:
                proc_to_name[proc] = m_node.group(1)
        elif code == EVT_START:
            proc_states[proc]["state"] = "running"
            # Fallback: try Cmd field in execute event
            if proc not in proc_to_name:
                m_cmd = RE_CMD.search(block)
                if m_cmd:
                    proc_to_name[proc] = m_cmd.group(1)
        elif code == EVT_HOLD:
            proc_states[proc]["state"] = "held"
        elif code == EVT_EVICT:
            proc_states[proc]["state"] = "evicted"
        elif code == EVT_ABORT:
            proc_states[proc]["state"] = "failed"
        elif code == EVT_TERMINATE:
            if "Normal termination" in block:
                m2 = re.search(r"Return value (\d+)", block)
                exit_code = int(m2.group(1)) if m2 else 0
                proc_states[proc]["state"] = "done" if exit_code == 0 else "failed"
                proc_states[proc]["exit_code"] = exit_code
            else:
                proc_states[proc]["state"] = "failed"

    # Build result: prefer job name from Cmd, fall back to proc ID
    result = {}
    for proc, info in proc_states.items():
        name = proc_to_name.get(proc, f"proc_{proc}")
        result[name] = info
    return result


def collect_log_states(submitdir: Path, tag: str) -> dict[str, dict]:
    """Read all log files for a given tag and return merged job state dict."""
    log_dir = submitdir / "logs" / tag
    states = {}
    if not log_dir.exists():
        return states
    for log_file in sorted(log_dir.glob("*.log")):
        parsed = parse_shared_log(log_file)
        # If job names were not resolved from Cmd, use log filename stem
        # e.g. "gen_ttbar_scan_ecm330.log" -> prefix jobs as "gen_<proc>"
        stem = log_file.stem  # e.g. gen_ttbar_scan_ecm330
        fixed = {}
        for name, info in parsed.items():
            if name.startswith("proc_"):
                name = f"{stem}_{name}"
            fixed[name] = info
        states.update(fixed)
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
    parser.add_argument("--condorq", action="store_true",
                        help="Also show condor_q -dag output (loads lxbatch/eossubmit if submitdir is on EOS)")
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

    if args.condorq:
        import subprocess
        use_eos = str(submitdir).startswith("/eos/")
        cmd = "module load lxbatch/eossubmit && condor_q -dag" if use_eos else "condor_q -dag"
        result = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"[condor_q failed] {result.stderr}")

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