# FCC ALLEGRO TileCal Studies

Simulation, reconstruction, and analysis of the Tile Hadronic Calorimeter (HCal)
for the ALLEGRO FCC-ee detector concept, including PandoraPFA particle-flow reconstruction.

## Directory layout

```
FCC_ALLEGRO_TileCal/           # this git repository
    setup.sh                   # environment setup
    compile.sh                 # build all packages from scratch
    README.md
    k4geo/                     # external dependencies (git-ignored, cloned separately)
    k4RecTracker/
    PandoraSDK/
    LCContent/
    DDMarlinPandora/
    CaloNtupleizer/
    Pythia8/
        cards/
            p8_ee_Zuds.cmd     # Z/γ* → uds dijets
            p8_ee_ttbar.cmd    # tt̄, W→e/q only
            p8_ee_WW.cmd       # W+W-, W→e/q only
            p8_ee_ZZ.cmd       # ZZ, Z→udsbee only
    ALLEGRO_PandoraPFA/        # reconstruction configs and auxiliary files
        run/                   # steering file + calibration/map files
            run_reco_pandora.py
            PandoraSettings_v6.xml
            PandoraLikelihoodDataALLEGRO.xml
            ...
            neighbours_map_ecalB_hcalB_hcalE.root      # git-ignored, copy manually
            neighbours_map_ecalE_turbine.root           # git-ignored, copy manually
            cellNoise_map_electronicsNoiseLevel_*.root  # git-ignored, copy manually
    batch/                     # HTCondor batch workflow (see Section 8)
        config.yaml            # single configuration file for all samples and steps
        submit.py              # orchestration script
        status.py              # pipeline status viewer
        requirements.txt       # Python dependencies (pyyaml, jinja2)
        templates/             # Jinja2 job script and submit file templates
    runs/                      # simulation and reconstruction output (git-ignored)
        sim/
        reco/
```

## Dependencies

| Package | Source | Branch |
|---|---|---|
| `k4geo` | `bravina/k4geo` | `hcal-new-geometry` |
| `k4RecTracker` | `bravina/k4RecTracker` | `master-archil` |
| `PandoraSDK` | `giovannimarchiori/PandoraSDK` | `master` |
| `LCContent` | `bravina/LCContent` | `ALLEGRO` |
| `DDMarlinPandora` | `bravina/DDMarlinPandora` | `test-hcal-cell-dimensions` |
| `Pythia8` | `bravina/Pythia8` | `main` |
| `ALLEGRO_PandoraPFA` | `bravina/ALLEGRO_PandoraPFA` | `main` |

> **Note:** `giovannimarchiori/PandoraSDK` adds `POINTING_THETAPHI` geometry
> type and `MessageStream.h`, required by `DDMarlinPandora` but not yet in the
> official PandoraPFA upstream or the Key4hep nightly stack.

> **Note:** `PandoraCMakeSettings.cmake` is not present in the latest nightly.
> It is taken from the `2026-02-26` nightly (see `compile.sh`).

> **Note:** Three large map files are not tracked in git and must be
> copied manually (see first-time setup below).

---

## 1. First-time setup

```bash
cd /afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal

# Clone dependency repos
git clone https://github.com/bravina/k4geo.git && cd k4geo && git checkout hcal-new-geometry && cd ..
git clone https://github.com/bravina/k4RecTracker.git && cd k4RecTracker && git checkout master-archil && cd ..
git clone https://github.com/giovannimarchiori/PandoraSDK.git
git clone https://github.com/bravina/LCContent.git && cd LCContent && git checkout ALLEGRO && cd ..
git clone https://github.com/bravina/DDMarlinPandora.git && cd DDMarlinPandora && git checkout test-hcal-cell-dimensions && cd ..
git clone https://github.com/bravina/Pythia8.git
git clone https://github.com/bravina/ALLEGRO_PandoraPFA.git

# Copy large map files that cannot be stored in git
# (from Archil's directory — ask him if no longer available)
ARCHIL=/afs/cern.ch/work/a/adurglis/public/PandoraPFA/run
cp $ARCHIL/neighbours_map_ecalB_hcalB_hcalE.root          ALLEGRO_PandoraPFA/run/
cp $ARCHIL/neighbours_map_ecalE_turbine.root               ALLEGRO_PandoraPFA/run/
cp $ARCHIL/cellNoise_map_electronicsNoiseLevel_ecalB_hcalB_hcalE.root ALLEGRO_PandoraPFA/run/

# Create runs directory
mkdir -p runs/sim runs/reco

# Set up environment and compile
source setup.sh
source compile.sh
```

---

## 2. Quick restart (fresh shell, already compiled)

```bash
source /afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal/setup.sh
```

To change the ALLEGRO geometry version, edit `ALLEGRO_VERSION` in `setup.sh`.

---

## 3. Event generation with Pythia8

Four process cards are available in `Pythia8/cards/`:

| Card | Process | Default ECM |
|---|---|---|
| `p8_ee_Zuds.cmd` | Z/γ* → uds dijets | 91.188 GeV |
| `p8_ee_ttbar.cmd` | tt̄ → Wb W̄b̄, W→e/q only | 365 GeV |
| `p8_ee_WW.cmd` | W+W-, W→e/q only | 240 GeV |
| `p8_ee_ZZ.cmd` | ZZ, Z→udsbee only | 240 GeV |

All cards support `--ecm` and `--seed` overrides on the command line.
Output is a HepMC file that is passed directly to `ddsim`.

```bash
cd $RUNSDIR

# Z->uds at Z pole
pythia --card $WORKDIR/Pythia8/cards/p8_ee_Zuds.cmd \
  --ecm 91.188 --seed 42 --nevents 1000 --output Zuds_ecm91

# Z->uds off-shell (e.g. for jet energy resolution studies)
pythia --card $WORKDIR/Pythia8/cards/p8_ee_Zuds.cmd \
  --ecm 200 --seed 42 --nevents 1000 --output Zuds_ecm200

# ttbar at threshold
pythia --card $WORKDIR/Pythia8/cards/p8_ee_ttbar.cmd \
  --ecm 365 --seed 42 --nevents 1000 --output ttbar_ecm365

# WW at 240 GeV
pythia --card $WORKDIR/Pythia8/cards/p8_ee_WW.cmd \
  --ecm 240 --seed 42 --nevents 1000 --output WW_ecm240

# ZZ at 240 GeV
pythia --card $WORKDIR/Pythia8/cards/p8_ee_ZZ.cmd \
  --ecm 240 --seed 42 --nevents 1000 --output ZZ_ecm240
```

---

## 4. Running the simulation

### Single particle gun

```bash
mkdir -p $RUNSDIR/sim/photon_10GeV_theta60
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "10*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle gamma \
  --numberOfEvents 100 \
  --outputFile $RUNSDIR/sim/photon_10GeV_theta60/ALLEGRO_sim.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT

mkdir -p $RUNSDIR/sim/kaon0L_50GeV_theta60
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "50*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle kaon0L \
  --numberOfEvents 100 \
  --outputFile $RUNSDIR/sim/kaon0L_50GeV_theta60/ALLEGRO_sim.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT

mkdir -p $RUNSDIR/sim/electron_10GeV_theta60
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "10*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle e- \
  --numberOfEvents 100 \
  --outputFile $RUNSDIR/sim/electron_10GeV_theta60/ALLEGRO_sim.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT

mkdir -p $RUNSDIR/sim/pion_50GeV_theta60
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "50*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle pi- \
  --numberOfEvents 100 \
  --outputFile $RUNSDIR/sim/pion_50GeV_theta60/ALLEGRO_sim.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT
```

### Two-particle gun

Uses the `two-particle-gun` script from k4Gen
(`https://github.com/key4hep/k4Gen/blob/main/scripts/two-particle-gun`).
Output is a HepMC file passed to `ddsim` via `--inputFiles`.

### Pythia8 events

```bash
cd $RUNSDIR
pythia --card $WORKDIR/Pythia8/cards/p8_ee_Zuds.cmd \
  --ecm 91.188 --seed 42 --nevents 1000 --output Zuds_ecm91
ddsim --inputFiles Zuds_ecm91.hepmc \
  --random.enableEventSeed --random.seed 42 \
  --numberOfEvents 100 \
  --outputFile ALLEGRO_sim_Zuds_ecm91.root \
  --compactFile $ALLEGRO_COMPACT
```

---

## 5. Running the reconstruction

Must be run from `$RUNDIR` since `run_reco_pandora.py` looks for auxiliary
files (calibration maps, Pandora settings XML) in `./`.

```bash
cd $RUNDIR

k4run run_reco_pandora.py \
  --pandoraSettings PandoraSettings_v6.xml \
  --IOSvc.Input $RUNSDIR/sim/kaon0L_50GeV_theta60/ALLEGRO_sim.root \
  --IOSvc.Output $RUNSDIR/reco/kaon0L_50GeV_theta60/ALLEGRO_reco.root
```

---

## 6. Running the CaloNtupleizer

```bash
calo-ntupleizer \
  --inputFiles $RUNSDIR/reco/kaon0L_50GeV_theta60/ALLEGRO_reco.root \
  --outputFile $RUNSDIR/reco/kaon0L_50GeV_theta60/ALLEGRO_ntuple.root
```

---

## 7. Quick look in ROOT

```bash
root -l $RUNSDIR/reco/kaon0L_50GeV_theta60/ALLEGRO_ntuple.root
# Total PFO energy
events->Draw("PandoraPFANewPFOs_totalEnergy")
# Jet energy resolution (barrel, Pythia8 dijets only)
events->Draw("PandoraPFANewPFOs_totalEnergy", "abs(genParticle_cosThetaQQ) < 0.7")
```

---

## 8. HTCondor batch workflow

The `batch/` folder provides a fully automated pipeline for running generation,
simulation, reconstruction, merging, and ntupling at scale on the LXPLUS HTCondor
batch system. Steps are chained using HTCondor DAGMan so each step only starts
after all upstream jobs complete successfully.

### Pipeline overview

```
gen (Pythia8)
  └─► sim (ddsim, 100 events/job, sliced from HepMC)
        └─► reco (k4run PandoraPFA, one job per sim file)
              └─► merge (hadd, groups reco files to target size)
                    └─► ntuple (calo-ntupleizer, single output per sample)
```

One independent DAG is created per `(sample, ECM)` combination, so energy scan
points run fully in parallel with each other.

### Python dependencies

`submit.py` requires Python ≥ 3.10 and two lightweight packages. Install once
into your user environment on LXPLUS:

```bash
pip install --user pyyaml jinja2
# or: pip install -r batch/requirements.txt --user
```

### First-time setup: cloning and compiling packages

If you have not already compiled the dependencies (i.e. you are starting from a
fresh clone of this repo), generate and run the setup script:

```bash
python batch/submit.py --config batch/config.yaml --setup
# This writes batch/jobs/setup_and_compile.sh — read it, then run:
bash batch/jobs/setup_and_compile.sh
```

This script will clone all repositories listed in the `packages` block of
`config.yaml`, compile them in the correct order, and copy the large map files
from Archil's AFS directory. It only needs to be run once; subsequent
recompiles can use `source compile.sh` directly.

If you already have a compiled installation somewhere, you can skip cloning by
pointing to it in `config.yaml` using `local_path` instead of `git`:

```yaml
packages:
  k4geo:
    local_path: /afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal/k4geo
```

### Configuration file

All workflow parameters live in `batch/config.yaml`. The main sections are:

**`paths`** — working directory, EOS output directory, submit file directory,
geometry version, Key4hep nightly, and Pandora settings XML.

```yaml
paths:
  workdir:         /afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal
  runsdir:         /eos/user/r/ravinab/FCC_ALLEGRO_TileCal/runs
  submitdir:       /afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal/batch/jobs
  allegro_version: ALLEGRO_o1_v03
  key4hep_setup:   latest          # or a date string, e.g. 2026-04-08
  pandora_settings: PandoraSettings_v6.xml
```

> **Note:** `submitdir` (DAG files, scripts, logs) should be on AFS.
> `runsdir` (HepMC, ROOT files) should be on EOS to avoid AFS quota issues.

**`workflow`** — per-step settings including events per job and HTCondor job
flavour (controls wall-clock limit).

```yaml
workflow:
  gen:
    enabled: true
    events_per_job: 10000
    job_flavour: longlunch      # ~2h
  sim:
    enabled: true
    events_per_job: 100
    job_flavour: longlunch
  reco:
    enabled: true
    events_per_job: 100
    job_flavour: longlunch
  merge:
    enabled: true
    events_per_merged_file: 10000
    job_flavour: longlunch
  ntuple:
    enabled: true
    job_flavour: longlunch
```

Available HTCondor job flavours on LXPLUS and their wall-clock limits:

| Flavour | Limit |
|---|---|
| `espresso` | 20 min |
| `microcentury` | 1 h |
| `longlunch` | 2 h |
| `workday` | 8 h |
| `tomorrow` | 1 day |
| `testmatch` | 3 days |
| `nextweek` | 1 week |

**`samples`** — list of physics samples. Each entry defines a process card,
a list of ECM values, a total event count, and a base random seed.

```yaml
samples:
  - name: ttbar
    card: Pythia8/cards/p8_ee_ttbar.cmd
    base_seed: 1000
    total_events: 10000
    ecm:
      - 365

  - name: ttbar_scan
    card: Pythia8/cards/p8_ee_ttbar.cmd
    base_seed: 3000
    total_events: 10000
    ecm: [330, 331, 332, 333, 334, 335]   # one DAG per ECM point
```

Each gen job `i` receives seed `base_seed + i`; sim jobs are offset by 10000
to avoid collisions. Seeds are therefore unique across all jobs within a sample.

### Submitting jobs
 
The `--steps` argument controls which pipeline stages to include. Any subset
may be specified; when multiple steps are given they are chained via DAGMan.
 
```bash
# Full pipeline for all samples in config.yaml
python batch/submit.py --config batch/config.yaml \
  --steps gen sim reco merge ntuple
 
# Simulation and reconstruction only (generation already done)
python batch/submit.py --config batch/config.yaml \
  --steps sim reco
 
# Reconstruction, merge, and ntuple only
python batch/submit.py --config batch/config.yaml \
  --steps reco merge ntuple
 
# Dry run: generate all job scripts and DAG files without submitting
python batch/submit.py --config batch/config.yaml \
  --steps sim reco merge ntuple --dry-run
```
 
When steps are run independently (e.g. `--steps sim` after gen has already
finished), `submit.py` reconstructs the expected input file paths from the
config rather than relying on DAG dependencies — so as long as the files exist
on disk at the paths derived from `runsdir`, everything will work.
 
#### EosSubmit schedds (recommended for large campaigns)
 
For campaigns with many jobs (energy scans, large event counts), set `submitdir`
in `config.yaml` to an EOS path. `submit.py` will detect this automatically and
use the EosSubmit schedd, which reads all job files directly from EOS via xrootd
and avoids AFS quota issues entirely.
 
Before submitting, load the EosSubmit schedd in your shell:
 
```bash
module load lxbatch/eossubmit
```
 
This only needs to be done once per session. `submit.py` will attempt to load
it automatically when submitting, but loading it manually first is recommended.
 
When using EosSubmit, **all files** (DAGs, scripts, sub files, logs) must be on
EOS — set `submitdir` to an EOS path and leave `scriptsdir` unset in `config.yaml`:
 
```yaml
paths:
  submitdir: /eos/user/r/ravinab/FCC_ALLEGRO_TileCal/batch/jobs
  # scriptsdir: leave unset — defaults to submitdir
```
 
To switch back to the standard schedd (e.g. for small tests):
 
```bash
module unload lxbatch/eossubmit
# and set submitdir back to AFS in config.yaml
```
 
For large campaigns with `scriptsdir` on EOS and `submitdir` on AFS (not
recommended with EosSubmit), `submit.py` will zip the scripts, transfer them
to EOS via `xrdcp`, and rewrite the paths in the `.sub` files automatically.
 
### Output directory structure
 
All output lands under `runsdir` (configured in `config.yaml`), organised by
step and sample tag (e.g. `ttbar_ecm365`):
 
```
$RUNSDIR/
    gen/
        ttbar_ecm365/
            gen_ttbar_ecm365_0000.hepmc   # one file per gen job
    sim/
        ttbar_ecm365/
            sim_ttbar_ecm365_0000.root    # 50 events each (default)
            sim_ttbar_ecm365_0001.root
            ...
    reco/
        ttbar_ecm365/
            reco_ttbar_ecm365_0000.root   # 200 events each (default, 4 sim files)
            ...
    merge/
        ttbar_ecm365/
            merge_ttbar_ecm365_0000.root  # 10k events each (hadd)
    ntuple/
        ttbar_ecm365/
            ntuple_ttbar_ecm365.root      # single output per sample+ECM
```
 
For energy scan samples each ECM point is a separate subdirectory, e.g.
`ttbar_scan_ecm330/`, `ttbar_scan_ecm332/`, etc.
 
### Monitoring jobs
 
For a per-step breakdown of the pipeline, use `batch/status.py`. It parses
the HTCondor log files written to `submitdir/logs/` in real time and shows
how many jobs in each step are idle, running, done, or failed:
 
```bash
# Status of all samples that have started running
python batch/status.py --config batch/config.yaml
 
# Filter to a single sample or ECM point
python batch/status.py --config batch/config.yaml --sample ttbar_ecm365
 
# Also print the names and exit codes of any failed jobs
python batch/status.py --config batch/config.yaml --failed
```
 
Example output:
 
```
Pipeline status  —  submitdir: .../batch/jobs
 
ttbar_ecm365  (101/253 done)
  Step        Done     Run    Fail    Held    Idle   Total  Progress
  -------------------------------------------------------------------------------------
  gen            1       0       0       0       0       1  [██████████████████████████████]
  sim          200       0       0       0       0     200  [██████████████████████████████]
  reco           0      50       0       0       0      50  [▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶···············]
  merge          0       0       0       0       1       1  [······························]
  ntuple         0       0       0       0       1       1  [······························]
```
 
Unlike `condor_q`, `status.py` works by reading the log files directly so it
reflects the current state even for jobs that have already finished and left
the queue. Samples with no log files yet are silently skipped unless explicitly
requested with `--sample`.
 
For a higher-level view of the HTCondor queue:
 
```bash
# Overview of all running/idle/held jobs
condor_q
 
# DAG-level status (shows which nodes are done/running/failed)
condor_q -dag
 
# Why is a job held?
condor_q -held -af ClusterId HoldReason
 
# Kill all jobs
condor_rm -all
```

Note: if `submitdir` is on EOS (EosSubmit schedd), prefix all `condor_q`
commands with `module load lxbatch/eossubmit`, or use `status.py --condorq`
which handles this automatically.
 
### Re-running failed jobs
 
If individual jobs fail, DAGMan marks them as failed and holds the downstream
steps. To retry:
 
```bash
# Resubmit the DAG in recovery mode — DAGMan skips already-completed nodes
condor_submit_dag -DoRecovery -Force batch/jobs/dags/ttbar_ecm365.dag
```
 
A `.rescue` file is written automatically by DAGMan after any failure.
DAGMan finds it automatically when `-DoRecovery` is passed — no need to
specify the rescue file explicitly. The `-Force` flag overwrites the stale
`.condor.sub` and log files from the previous submission.
 
To release held jobs after fixing the underlying issue (e.g. memory limit):
 
```bash
condor_release -all
# or for a specific job:
condor_release <ClusterId>
```
 
### Adding a new sample
 
Add an entry to the `samples` list in `config.yaml` and re-run `submit.py`.
Previously submitted DAGs are unaffected. Example — adding ZZ at 240 GeV:
 
```yaml
  - name: ZZ
    card: Pythia8/cards/p8_ee_ZZ.cmd
    base_seed: 7000
    total_events: 10000
    ecm:
      - 240
```


---

## Notes

- Three large map files are not stored in git — copy from Archil's AFS
  directory as described in the first-time setup. If unavailable, check
  `https://fccsw.web.cern.ch/fccsw/filesForSimDigiReco/ALLEGRO/`.
- Output ROOT files are stored under `runs/` (git-ignored).
  If AFS quota becomes an issue, move `runs/` to EOS at
  `/eos/user/r/ravinab/FCC_ALLEGRO_TileCal/runs/` and update `RUNSDIR` in `setup.sh`.
- The geometry version is controlled by `ALLEGRO_VERSION` in `setup.sh`.
  Current value: `ALLEGRO_o1_v03`.
- The latest Key4hep nightly is used (no pinned release). If a nightly breaks
  the build, pin a specific release by changing `key4hep_setup` in `batch/config.yaml`
  to a date string, e.g. `2026-04-08`. This affects all batch jobs generated
  from that config. Also change the `source` line in `setup.sh`
  to e.g. `source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-04-08`.
- `genParticle_cosThetaQQ` in the ntuple is only meaningful for Pythia8 dijet
  events (uses generator status 23 = outgoing hard-process parton). It will
  return -1 for single-particle gun events.
- `batch/jobs/` is git-ignored. The generated job scripts, DAG files, and
  HTCondor logs are all written there and do not need to be committed.