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
    ALLEGRO_PandoraPFA/        # reconstruction configs and auxiliary files
        run/                   # steering file + calibration/map files
            run_reco_pandora.py
            PandoraSettings_v6.xml
            PandoraLikelihoodDataALLEGRO.xml
            ...
            neighbours_map_ecalB_hcalB_hcalE.root      # git-ignored, copy manually
            neighbours_map_ecalE_turbine.root           # git-ignored, copy manually
            cellNoise_map_electronicsNoiseLevel_*.root  # git-ignored, copy manually
    runs/                      # simulation and reconstruction output (git-ignored)
        sim/
        reco/
```

## Dependencies

| Package | Source | Branch |
|---|---|---|
| `k4geo` | `bravina/k4geo` | `hcal-new-geometry` |
| `k4RecTracker` | `bravina/k4RecTracker` | `pandora` |
| `PandoraSDK` | `giovannimarchiori/PandoraSDK` | `master` |
| `LCContent` | `bravina/LCContent` | `ALLEGRO` |
| `DDMarlinPandora` | `bravina/DDMarlinPandora` | `test-hcal-cell-dimensions` |
| `CaloNtupleizer` | `bravina/CaloNtupleizer` | `main` |
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
git clone https://github.com/bravina/k4RecTracker.git && cd k4RecTracker && git checkout pandora && cd ..
git clone https://github.com/giovannimarchiori/PandoraSDK.git
git clone https://github.com/bravina/LCContent.git && cd LCContent && git checkout ALLEGRO && cd ..
git clone https://github.com/bravina/DDMarlinPandora.git && cd DDMarlinPandora && git checkout test-hcal-cell-dimensions && cd ..
git clone https://github.com/bravina/CaloNtupleizer.git
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

Two process cards are available in `Pythia8/cards/`:

| Card | Process | Default ECM |
|---|---|---|
| `p8_ee_Zuds.cmd` | Z/γ* → uds dijets | 91.188 GeV |
| `p8_ee_ttbar.cmd` | tt̄ → W b W̄ b̄, W→e/q only | 365 GeV |

Both cards support `--ecm` and `--seed` overrides on the command line.
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
  --numberOfEvents -1 \
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
  the build, pin a specific release by changing the `source` line in `setup.sh`
  to e.g. `source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-04-08`.
- `genParticle_cosThetaQQ` in the ntuple is only meaningful for Pythia8 dijet
  events (uses generator status 23 = outgoing hard-process parton). It will
  return -1 for single-particle gun events.