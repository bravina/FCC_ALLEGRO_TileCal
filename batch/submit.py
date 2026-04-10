#!/usr/bin/env python3
"""
submit.py  —  FCC ALLEGRO batch workflow orchestrator

Usage:
    # Generate DAG + all job files, then submit
    python batch/submit.py --config batch/config.yaml --steps gen sim reco merge ntuple

    # Dry-run: generate files only, do not submit
    python batch/submit.py --config batch/config.yaml --steps sim reco --dry-run

    # Generate the environment setup/compile script (run once before first submission)
    python batch/submit.py --config batch/config.yaml --setup

Available steps (can be any subset, chained in this fixed order):
    gen   — Pythia8 event generation
    sim   — ddsim full simulation
    reco  — k4run PandoraPFA reconstruction
    merge — hadd reco files
    ntuple— CaloNtupleizer
"""

import argparse
import math
import os
import stat
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STEP_ORDER = ["gen", "sim", "reco", "merge", "ntuple"]

# Packages that use cmake + k4_local_repo (order matters for cmake deps)
CMAKE_PACKAGES = [
    "PandoraSDK", "k4geo", "k4RecTracker", "LCContent",
    "DDMarlinPandora", "CaloNtupleizer",
]
PANDORA_CMAKE_PACKAGES = {"PandoraSDK", "LCContent", "DDMarlinPandora"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def render(env: Environment, template_name: str, **kwargs) -> str:
    return env.get_template(template_name).render(**kwargs)


def write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def sample_tag(sample_name: str, ecm: float) -> str:
    """Unique tag for a (sample, ecm) combination, e.g. ttbar_ecm365."""
    ecm_str = f"{ecm:.3f}".rstrip("0").rstrip(".")
    return f"{sample_name}_ecm{ecm_str}"


# ---------------------------------------------------------------------------
# Package path resolution
# ---------------------------------------------------------------------------

def resolve_package_paths(cfg: dict) -> dict[str, Path]:
    """Return {pkg_name: absolute_root_path} for every package in the config.

    For git-based packages the root is workdir/PackageName (where the repo
    is cloned).  For local_path packages it is the path as given.
    """
    workdir = Path(cfg["paths"]["workdir"])
    resolved = {}
    for pkg_name, pkg_cfg in cfg["packages"].items():
        if "local_path" in pkg_cfg:
            resolved[pkg_name] = Path(pkg_cfg["local_path"])
        else:
            resolved[pkg_name] = workdir / pkg_name
    return resolved


def build_env_context(cfg: dict) -> dict:
    """Build the dict of environment variables passed to every job template.

    All paths come from the config — nothing is hardcoded here.
    """
    paths = cfg["paths"]
    pkg_paths = resolve_package_paths(cfg)

    allegro_version = paths["allegro_version"]
    k4geo_dir = pkg_paths["k4geo"]
    allegro_compact = (
        f"{k4geo_dir}/FCCee/ALLEGRO/compact"
        f"/{allegro_version}/{allegro_version}.xml"
    )

    # Packages that need k4_local_repo called on them (cmake-based)
    k4_local_repo_dirs = [
        str(pkg_paths[p]) for p in CMAKE_PACKAGES if p in pkg_paths
    ]

    # Extra LD_LIBRARY_PATH entries from config (cvmfs overrides, local libs)
    extra_ld = list(cfg["paths"].get("extra_ld_library_paths", []))
    # Always add CaloNtupleizer's lib64
    calo_lib = str(pkg_paths["CaloNtupleizer"] / "install" / "lib64")
    if calo_lib not in extra_ld:
        extra_ld.append(calo_lib)

    return {
        "key4hep_setup":      paths["key4hep_setup"],
        "allegro_version":    allegro_version,
        "allegro_compact":    allegro_compact,
        "pandora_sdk_dir":    str(pkg_paths["PandoraSDK"]),
        "k4_local_repo_dirs": k4_local_repo_dirs,
        "extra_ld_paths":     extra_ld,
        "pythia_bin":                  str(pkg_paths["Pythia8"] / "bin" / "pythia"),
        "calo_ntupleizer_scripts_dir": str(pkg_paths["CaloNtupleizer"] / "scripts"),
        "pythia8_bin_dir":             str(pkg_paths["Pythia8"] / "bin"),
        "rundir":             str(pkg_paths["ALLEGRO_PandoraPFA"] / "run"),
        "pandora_settings":   paths["pandora_settings"],
    }


# ---------------------------------------------------------------------------
# Setup / compile script generation
# ---------------------------------------------------------------------------

def generate_setup_script(cfg: dict, submitdir: Path) -> None:
    """Write a one-time setup_and_compile.sh from the packages config."""
    workdir = cfg["paths"]["workdir"]
    k4hep = cfg["paths"]["key4hep_setup"]
    packages = cfg.get("packages", {})
    pkg_paths = resolve_package_paths(cfg)

    k4hep_source = (
        "source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh"
        if k4hep == "latest"
        else f"source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r {k4hep}"
    )

    pandora_cmake_path = (
        "/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/"
        "x86_64-almalinux9-gcc14.2.0-opt/pandorapfa/4.11.2-tyvaev/cmakemodules"
    )

    lines = [
        "#!/bin/bash",
        "# Auto-generated by submit.py --setup",
        "# Run this ONCE to clone and compile all dependencies.",
        "# Usage: bash batch/jobs/setup_and_compile.sh",
        "set -euo pipefail",
        "",
        f"export WORKDIR={workdir}",
        f"cd ${{WORKDIR}}",
        "",
        "# --- Key4hep environment ---",
        k4hep_source,
        "",
        "# PandoraCMakeSettings (not in latest nightly)",
        f"export PANDORA_CMAKE_MODULE_PATH={pandora_cmake_path}",
        "",
    ]

    lines.append("# --- Clone or update repositories ---")
    for pkg_name, pkg_cfg in packages.items():
        if "local_path" in pkg_cfg:
            lines.append(
                f"# {pkg_name}: using local path {pkg_cfg['local_path']} (skipping clone)"
            )
            continue
        git = pkg_cfg["git"]
        url, branch = git["url"], git["branch"]
        dest = pkg_paths[pkg_name]
        lines += [
            f"if [ ! -d {dest} ]; then",
            f"  git clone {url} {dest}",
            f"fi",
            f"cd {dest} && git checkout {branch} && git pull && cd ${{WORKDIR}}",
            "",
        ]

    lines.append("# --- Compile cmake-based packages ---")
    pandora_flag = "-DCMAKE_MODULE_PATH=${PANDORA_CMAKE_MODULE_PATH}"
    for pkg in CMAKE_PACKAGES:
        if pkg not in packages:
            continue
        pkg_cfg = packages[pkg]
        if "local_path" in pkg_cfg:
            lines.append(f"# {pkg}: using local path, skipping compile")
            continue
        dest = pkg_paths[pkg]
        extra = pandora_flag if pkg in PANDORA_CMAKE_PACKAGES else ""
        lines += [
            f"cd {dest}",
            "rm -rf build install && mkdir build install",
            "cd build",
            f"cmake .. -DCMAKE_INSTALL_PREFIX=../install {extra}".strip(),
            "make install -j$(nproc)",
            "cd ..",
            "k4_local_repo",
            f"cd ${{WORKDIR}}",
            "",
        ]

    lines.append("# --- Compile Pythia8 (standalone C++) ---")
    pythia_pkg = "Pythia8"
    if pythia_pkg in packages and "local_path" not in packages[pythia_pkg]:
        dest = pkg_paths[pythia_pkg]
        # Use HepMC3 from the extra_ld_library_paths if available, otherwise
        # fall back to the known 2026-02-26 path.
        hepmc3_default = (
            "/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/"
            "x86_64-almalinux9-gcc14.2.0-opt/hepmc3/3.3.1-3o4ayl/"
        )
        lines += [
            f"cd {dest}",
            f"export HEPMC3={hepmc3_default}",
            "export LD_LIBRARY_PATH=$PYTHIA8/lib:$LD_LIBRARY_PATH",
            "export LD_LIBRARY_PATH=$HEPMC3/lib64:$LD_LIBRARY_PATH",
            "mkdir -p bin",
            "c++ -O2 -std=c++20 main.cc \\",
            "  -I$PYTHIA8/include -I$HEPMC3/include \\",
            "  -L$PYTHIA8/lib -L$HEPMC3/lib64 \\",
            "  -Wl,-rpath,$PYTHIA8/lib:$HEPMC3/lib64 \\",
            "  -lpythia8 -lHepMC3 -ldl \\",
            "  -o bin/pythia",
            f"cd ${{WORKDIR}}",
            "",
        ]

    allegro_run = pkg_paths.get("ALLEGRO_PandoraPFA", Path(workdir) / "ALLEGRO_PandoraPFA") / "run"
    lines += [
        "# --- Copy large map files (if not already present) ---",
        "ARCHIL=/afs/cern.ch/work/a/adurglis/public/PandoraPFA/run",
        f"RUNDIR={allegro_run}",
        "for f in neighbours_map_ecalB_hcalB_hcalE.root \\",
        "         neighbours_map_ecalE_turbine.root \\",
        "         cellNoise_map_electronicsNoiseLevel_ecalB_hcalB_hcalE.root; do",
        '  [ -f "${RUNDIR}/${f}" ] || cp "${ARCHIL}/${f}" "${RUNDIR}/"',
        "done",
        "",
        "echo 'Setup and compile complete.'",
    ]

    out = submitdir / "setup_and_compile.sh"
    write_executable(out, "\n".join(lines) + "\n")
    print(f"[setup] Written: {out}")
    print("[setup] WARNING: run  bash batch/jobs/setup_and_compile.sh  before submitting any jobs.")


# ---------------------------------------------------------------------------
# Per-step job generation
# ---------------------------------------------------------------------------

def make_gen_jobs(sample: dict, ecm: float, cfg: dict,
                  submitdir: Path, jinja_env: Environment,
                  env_ctx: dict) -> list[dict]:
    paths = cfg["paths"]
    wf = cfg["workflow"]["gen"]
    tag = sample_tag(sample["name"], ecm)
    nevents_total = sample["total_events"]
    nevents_job = wf["events_per_job"]
    n_jobs = math.ceil(nevents_total / nevents_job)
    base_seed = sample["base_seed"]

    # Resolve card path: relative paths are relative to workdir
    card = sample["card"]
    if not Path(card).is_absolute():
        card = str(Path(paths["workdir"]) / card)

    nodes = []
    for i in range(n_jobs):
        job_name = f"gen_{tag}_{i:04d}"
        seed = base_seed + i
        output_dir = f"{paths['runsdir']}/gen/{tag}"
        output_file = f"gen_{tag}_{i:04d}"

        script_content = render(
            jinja_env, "gen.sh.j2",
            sample_name=sample["name"], ecm=ecm, job_index=i,
            card=card,
            output_dir=output_dir, output_file=output_file,
            nevents=nevents_job, seed=seed,
            **env_ctx,
        )
        script_path = submitdir / "scripts" / f"{job_name}.sh"
        write_executable(script_path, script_content)

        log_dir = submitdir / "logs" / tag
        log_dir.mkdir(parents=True, exist_ok=True)

        sub_content = render(
            jinja_env, "condor.sub.j2",
            job_name=job_name, script=script_path,
            log_dir=log_dir, job_flavour=wf["job_flavour"], request_memory_mb=wf["request_memory_mb"],
        )
        sub_path = submitdir / "condor" / f"{job_name}.sub"
        write_file(sub_path, sub_content)

        nodes.append({
            "name": job_name,
            "sub": sub_path,
            "step": "gen",
            "output_hepmc": f"{output_dir}/{output_file}.hepmc",
            "parents": [],
        })
    return nodes


def make_sim_jobs(sample: dict, ecm: float, cfg: dict,
                  submitdir: Path, jinja_env: Environment,
                  env_ctx: dict, gen_nodes: list[dict]) -> list[dict]:
    paths = cfg["paths"]
    wf_sim = cfg["workflow"]["sim"]
    wf_gen = cfg["workflow"]["gen"]
    tag = sample_tag(sample["name"], ecm)
    base_seed = sample["base_seed"]

    nodes = []
    sim_index = 0
    for gen_node in gen_nodes:
        hepmc_file = gen_node["output_hepmc"]
        n_sim_per_gen = math.ceil(wf_gen["events_per_job"] / wf_sim["events_per_job"])

        for j in range(n_sim_per_gen):
            job_name = f"sim_{tag}_{sim_index:04d}"
            skip = j * wf_sim["events_per_job"]
            seed = base_seed + 10000 + sim_index
            output_dir = f"{paths['runsdir']}/sim/{tag}"
            output_file = f"sim_{tag}_{sim_index:04d}.root"

            script_content = render(
                jinja_env, "sim.sh.j2",
                sample_name=sample["name"], ecm=ecm, job_index=sim_index,
                hepmc_file=hepmc_file,
                output_dir=output_dir, output_file=output_file,
                nevents=wf_sim["events_per_job"], skip_events=skip, seed=seed,
                **env_ctx,
            )
            script_path = submitdir / "scripts" / f"{job_name}.sh"
            write_executable(script_path, script_content)

            log_dir = submitdir / "logs" / tag
            log_dir.mkdir(parents=True, exist_ok=True)

            sub_content = render(
                jinja_env, "condor.sub.j2",
                job_name=job_name, script=script_path,
                log_dir=log_dir, job_flavour=wf_sim["job_flavour"], request_memory_mb=wf_sim["request_memory_mb"],
            )
            sub_path = submitdir / "condor" / f"{job_name}.sub"
            write_file(sub_path, sub_content)

            nodes.append({
                "name": job_name,
                "sub": sub_path,
                "step": "sim",
                "output_root": f"{output_dir}/{output_file}",
                "parents": [gen_node["name"]],
            })
            sim_index += 1
    return nodes


def make_reco_jobs(sample: dict, ecm: float, cfg: dict,
                   submitdir: Path, jinja_env: Environment,
                   env_ctx: dict, sim_nodes: list[dict]) -> list[dict]:
    paths = cfg["paths"]
    wf_reco = cfg["workflow"]["reco"]
    wf_sim  = cfg["workflow"]["sim"]
    tag = sample_tag(sample["name"], ecm)

    # Group sim files so each reco job processes events_per_job events.
    # Since each sim file contains sim.events_per_job events, the number
    # of sim files per reco job is reco.events_per_job / sim.events_per_job.
    sim_per_reco = max(1, wf_reco["events_per_job"] // wf_sim["events_per_job"])
    chunks = [sim_nodes[i:i + sim_per_reco]
              for i in range(0, len(sim_nodes), sim_per_reco)]

    nodes = []
    for i, chunk in enumerate(chunks):
        job_name = f"reco_{tag}_{i:04d}"
        output_dir = f"{paths['runsdir']}/reco/{tag}"
        output_file = f"reco_{tag}_{i:04d}.root"
        sim_files = [n["output_root"] for n in chunk]

        script_content = render(
            jinja_env, "reco.sh.j2",
            sample_name=sample["name"], ecm=ecm, job_index=i,
            sim_files=sim_files,
            output_dir=output_dir, output_file=output_file,
            **env_ctx,
        )
        script_path = submitdir / "scripts" / f"{job_name}.sh"
        write_executable(script_path, script_content)

        log_dir = submitdir / "logs" / tag
        log_dir.mkdir(parents=True, exist_ok=True)

        sub_content = render(
            jinja_env, "condor.sub.j2",
            job_name=job_name, script=script_path,
            log_dir=log_dir, job_flavour=wf_reco["job_flavour"],
            request_memory_mb=wf_reco["request_memory_mb"],
        )
        sub_path = submitdir / "condor" / f"{job_name}.sub"
        write_file(sub_path, sub_content)

        nodes.append({
            "name": job_name,
            "sub": sub_path,
            "step": "reco",
            "output_root": f"{output_dir}/{output_file}",
            "parents": [n["name"] for n in chunk],
        })
    return nodes


def make_merge_jobs(sample: dict, ecm: float, cfg: dict,
                    submitdir: Path, jinja_env: Environment,
                    env_ctx: dict, reco_nodes: list[dict]) -> list[dict]:
    paths = cfg["paths"]
    wf = cfg["workflow"]["merge"]
    wf_reco = cfg["workflow"]["reco"]
    tag = sample_tag(sample["name"], ecm)

    reco_per_merge = max(1, wf["events_per_merged_file"] // wf_reco["events_per_job"])
    chunks = [reco_nodes[i:i + reco_per_merge]
              for i in range(0, len(reco_nodes), reco_per_merge)]

    nodes = []
    for i, chunk in enumerate(chunks):
        job_name = f"merge_{tag}_{i:04d}"
        output_dir = f"{paths['runsdir']}/merge/{tag}"
        output_file = f"merge_{tag}_{i:04d}.root"
        input_files = [n["output_root"] for n in chunk]

        script_content = render(
            jinja_env, "merge.sh.j2",
            sample_name=sample["name"], ecm=ecm,
            output_dir=output_dir, output_file=output_file,
            input_files=input_files,
            **env_ctx,
        )
        script_path = submitdir / "scripts" / f"{job_name}.sh"
        write_executable(script_path, script_content)

        log_dir = submitdir / "logs" / tag
        log_dir.mkdir(parents=True, exist_ok=True)

        sub_content = render(
            jinja_env, "condor.sub.j2",
            job_name=job_name, script=script_path,
            log_dir=log_dir, job_flavour=wf["job_flavour"], request_memory_mb=wf["request_memory_mb"],
        )
        sub_path = submitdir / "condor" / f"{job_name}.sub"
        write_file(sub_path, sub_content)

        nodes.append({
            "name": job_name,
            "sub": sub_path,
            "step": "merge",
            "output_root": f"{output_dir}/{output_file}",
            "parents": [n["name"] for n in chunk],
        })
    return nodes


def make_ntuple_job(sample: dict, ecm: float, cfg: dict,
                    submitdir: Path, jinja_env: Environment,
                    env_ctx: dict, merge_nodes: list[dict]) -> dict:
    paths = cfg["paths"]
    wf = cfg["workflow"]["ntuple"]
    tag = sample_tag(sample["name"], ecm)

    job_name = f"ntuple_{tag}"
    output_dir = f"{paths['runsdir']}/ntuple/{tag}"
    output_file = f"ntuple_{tag}.root"
    input_files = [n["output_root"] for n in merge_nodes]

    script_content = render(
        jinja_env, "ntuple.sh.j2",
        sample_name=sample["name"], ecm=ecm,
        output_dir=output_dir, output_file=output_file,
        input_files=input_files,
        **env_ctx,
    )
    script_path = submitdir / "scripts" / f"{job_name}.sh"
    write_executable(script_path, script_content)

    log_dir = submitdir / "logs" / tag
    log_dir.mkdir(parents=True, exist_ok=True)

    sub_content = render(
        jinja_env, "condor.sub.j2",
        job_name=job_name, script=script_path,
        log_dir=log_dir, job_flavour=wf["job_flavour"], request_memory_mb=wf["request_memory_mb"],
    )
    sub_path = submitdir / "condor" / f"{job_name}.sub"
    write_file(sub_path, sub_content)

    return {
        "name": job_name,
        "sub": sub_path,
        "step": "ntuple",
        "output_root": f"{output_dir}/{output_file}",
        "parents": [n["name"] for n in merge_nodes],
    }


# ---------------------------------------------------------------------------
# DAG generation
# ---------------------------------------------------------------------------

def write_dag(nodes: list[dict], dag_path: Path) -> None:
    lines = ["# Auto-generated DAGMan file", ""]
    for node in nodes:
        lines.append(f"JOB {node['name']} {node['sub']}")
    lines.append("")
    for node in nodes:
        if node["parents"]:
            parents_str = " ".join(node["parents"])
            lines.append(f"PARENT {parents_str} CHILD {node['name']}")
    write_file(dag_path, "\n".join(lines) + "\n")
    print(f"[dag] Written: {dag_path}")


# ---------------------------------------------------------------------------
# Phantom node helpers (upstream step not in this DAG)
# ---------------------------------------------------------------------------

def phantom_gen_nodes(sample: dict, ecm: float, cfg: dict) -> list[dict]:
    wf_gen = cfg["workflow"]["gen"]
    n_gen = math.ceil(sample["total_events"] / wf_gen["events_per_job"])
    tag = sample_tag(sample["name"], ecm)
    runsdir = cfg["paths"]["runsdir"]
    return [
        {"name": None,
         "output_hepmc": f"{runsdir}/gen/{tag}/gen_{tag}_{i:04d}.hepmc"}
        for i in range(n_gen)
    ]


def phantom_sim_nodes(sample: dict, ecm: float, cfg: dict) -> list[dict]:
    wf_gen = cfg["workflow"]["gen"]
    wf_sim = cfg["workflow"]["sim"]
    n_gen = math.ceil(sample["total_events"] / wf_gen["events_per_job"])
    n_sim = n_gen * math.ceil(wf_gen["events_per_job"] / wf_sim["events_per_job"])
    tag = sample_tag(sample["name"], ecm)
    runsdir = cfg["paths"]["runsdir"]
    return [
        {"name": None,
         "output_root": f"{runsdir}/sim/{tag}/sim_{tag}_{i:04d}.root"}
        for i in range(n_sim)
    ]


def phantom_reco_nodes(sample: dict, ecm: float, cfg: dict) -> list[dict]:
    sim_nodes = phantom_sim_nodes(sample, ecm, cfg)
    wf_reco = cfg["workflow"]["reco"]
    wf_sim  = cfg["workflow"]["sim"]
    sim_per_reco = max(1, wf_reco["events_per_job"] // wf_sim["events_per_job"])
    n_reco = math.ceil(len(sim_nodes) / sim_per_reco)
    tag = sample_tag(sample["name"], ecm)
    runsdir = cfg["paths"]["runsdir"]
    return [
        {"name": None,
         "output_root": f"{runsdir}/reco/{tag}/reco_{tag}_{i:04d}.root"}
        for i in range(n_reco)
    ]


def phantom_merge_nodes(sample: dict, ecm: float, cfg: dict) -> list[dict]:
    wf_merge = cfg["workflow"]["merge"]
    wf_reco = cfg["workflow"]["reco"]
    reco_nodes = phantom_reco_nodes(sample, ecm, cfg)
    reco_per_merge = max(1, wf_merge["events_per_merged_file"] // wf_reco["events_per_job"])
    n_merge = math.ceil(len(reco_nodes) / reco_per_merge)
    tag = sample_tag(sample["name"], ecm)
    runsdir = cfg["paths"]["runsdir"]
    return [
        {"name": None,
         "output_root": f"{runsdir}/merge/{tag}/merge_{tag}_{i:04d}.root"}
        for i in range(n_merge)
    ]


def strip_phantom_parents(nodes: list[dict]) -> None:
    for n in nodes:
        n["parents"] = [p for p in n["parents"] if p is not None]


# ---------------------------------------------------------------------------
# Main workflow builder
# ---------------------------------------------------------------------------

def build_workflow(cfg: dict, steps: list[str],
                   submitdir: Path, jinja_env: Environment) -> list[Path]:
    env_ctx = build_env_context(cfg)
    dag_paths = []

    for sample in cfg["samples"]:
        for ecm in sample["ecm"]:
            tag = sample_tag(sample["name"], ecm)
            all_nodes: list[dict] = []

            gen_nodes = sim_nodes = reco_nodes = merge_nodes = []

            if "gen" in steps and cfg["workflow"]["gen"]["enabled"]:
                gen_nodes = make_gen_jobs(sample, ecm, cfg, submitdir, jinja_env, env_ctx)
                all_nodes.extend(gen_nodes)

            if "sim" in steps and cfg["workflow"]["sim"]["enabled"]:
                upstream = gen_nodes or phantom_gen_nodes(sample, ecm, cfg)
                sim_nodes = make_sim_jobs(sample, ecm, cfg, submitdir, jinja_env, env_ctx, upstream)
                strip_phantom_parents(sim_nodes)
                all_nodes.extend(sim_nodes)

            if "reco" in steps and cfg["workflow"]["reco"]["enabled"]:
                upstream = sim_nodes or phantom_sim_nodes(sample, ecm, cfg)
                reco_nodes = make_reco_jobs(sample, ecm, cfg, submitdir, jinja_env, env_ctx, upstream)
                strip_phantom_parents(reco_nodes)
                all_nodes.extend(reco_nodes)

            if "merge" in steps and cfg["workflow"]["merge"]["enabled"]:
                upstream = reco_nodes or phantom_reco_nodes(sample, ecm, cfg)
                merge_nodes = make_merge_jobs(sample, ecm, cfg, submitdir, jinja_env, env_ctx, upstream)
                strip_phantom_parents(merge_nodes)
                all_nodes.extend(merge_nodes)

            if "ntuple" in steps and cfg["workflow"]["ntuple"]["enabled"]:
                upstream = merge_nodes or phantom_merge_nodes(sample, ecm, cfg)
                ntuple_node = make_ntuple_job(sample, ecm, cfg, submitdir, jinja_env, env_ctx, upstream)
                ntuple_node["parents"] = [p for p in ntuple_node["parents"] if p is not None]
                all_nodes.append(ntuple_node)

            if not all_nodes:
                print(f"[{tag}] No enabled steps — skipping.")
                continue

            dag_path = submitdir / "dags" / f"{tag}.dag"
            write_dag(all_nodes, dag_path)
            dag_paths.append(dag_path)
            steps_in_dag = sorted({n["step"] for n in all_nodes}, key=STEP_ORDER.index)
            print(f"[{tag}] DAG with {len(all_nodes)} jobs, steps: {' -> '.join(steps_in_dag)}")

    return dag_paths


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--steps", nargs="+", choices=STEP_ORDER, metavar="STEP",
                        help="Steps to include (gen sim reco merge ntuple). "
                             "Multiple steps are chained via DAGMan.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate job files but do not submit to HTCondor.")
    parser.add_argument("--setup", action="store_true",
                        help="Generate setup_and_compile.sh and exit.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    submitdir = Path(cfg["paths"]["submitdir"])
    submitdir.mkdir(parents=True, exist_ok=True)

    script_dir = Path(__file__).parent
    jinja_env = Environment(loader=FileSystemLoader(str(script_dir / "templates")),
                            keep_trailing_newline=True)

    if args.setup:
        generate_setup_script(cfg, submitdir)
        return

    if not args.steps:
        parser.error("--steps is required unless --setup is given.")

    steps = [s for s in STEP_ORDER if s in args.steps]
    dag_paths = build_workflow(cfg, steps, submitdir, jinja_env)

    if not dag_paths:
        print("No DAGs generated.")
        return

    if args.dry_run:
        print(f"\n[dry-run] {len(dag_paths)} DAG(s) written. Not submitting.")
        for p in dag_paths:
            print(f"  {p}")
        return

    print(f"\nSubmitting {len(dag_paths)} DAG(s)...")
    for dag in dag_paths:
        result = subprocess.run(["condor_submit_dag", str(dag)],
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [OK] {dag.name}")
        else:
            print(f"  [FAIL] {dag.name}")
            print(result.stderr)


if __name__ == "__main__":
    main()
