# FCC ALLEGRO TileCal Studies

Simulation, reconstruction, and analysis of the Tile Hadronic Calorimeter (HCal)
for the ALLEGRO FCC-ee detector concept, including PandoraPFA particle-flow reconstruction.

## Dependencies

All dependencies are built locally on top of the Key4hep nightly stack.
The following external repositories are required — clone them as siblings of
this repo inside `$WORKDIR`:

| Package | Fork source | Branch |
|---|---|---|
| `k4geo` | `Archil-AD/k4geo` | `hcal-new-geometry` |
| `k4RecCalorimeter` | `Archil-AD/k4RecCalorimeter` | `main` |
| `k4RecTracker` | `Archil-AD/k4RecTracker` | `pandora` |
| `PandoraSDK` | `giovannimarchiori/PandoraSDK` | `master` |
| `LCContent` | `Archil-AD/LCContent` | `ALLEGRO` |
| `DDMarlinPandora` | `Archil-AD/DDMarlinPandora` | `test-hcal-cell-dimensions` |

> **Note:** `giovannimarchiori/PandoraSDK` adds `POINTING_THETAPHI` geometry
> type and `MessageStream.h`, which are required by `DDMarlinPandora` but not
> yet in the official PandoraPFA upstream or the Key4hep nightly stack.

> **Note:** `PandoraCMakeSettings.cmake` is not present in the `2026-04-08`
> nightly. It is taken from the `2026-02-26` nightly pandorapfa installation
> (see build instructions below).

---

## 1. Full build (first time only)

```bash
export WORKDIR=/afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal
cd $WORKDIR

source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2026-04-08

# Clone dependency repos (fork these from the sources in the table above)
git clone https://github.com/bravina/k4geo.git
git clone https://github.com/bravina/k4RecCalorimeter.git
git clone https://github.com/bravina/k4RecTracker.git
git clone https://github.com/bravina/PandoraSDK.git
git clone https://github.com/bravina/LCContent.git
git clone https://github.com/bravina/DDMarlinPandora.git

# PandoraCMakeSettings module (from 2026-02-26 nightly, not present in 2026-04-08)
export PANDORA_CMAKE_MODULE_PATH=/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/x86_64-almalinux9-gcc14.2.0-opt/pandorapfa/4.11.2-tyvaev/cmakemodules

# 1. k4geo
cd k4geo && git checkout hcal-new-geometry
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j8
cd .. && k4_local_repo
export K4GEO=$PWD/
cd $WORKDIR

# 2. k4RecCalorimeter (main already contains hcal-endcap-pseudolayer changes)
cd k4RecCalorimeter
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j8
cd .. && k4_local_repo
cd $WORKDIR

# 3. k4RecTracker
cd k4RecTracker && git checkout pandora
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j8
cd .. && k4_local_repo
cd $WORKDIR

# 4. PandoraSDK
cd PandoraSDK
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install \
  -DCMAKE_MODULE_PATH=$PANDORA_CMAKE_MODULE_PATH
make install -j8
cd .. && k4_local_repo
cd $WORKDIR

# 5. LCContent
cd LCContent && git checkout ALLEGRO
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install \
  -DCMAKE_MODULE_PATH=$PANDORA_CMAKE_MODULE_PATH
make install -j8
cd .. && k4_local_repo
cd $WORKDIR

# 6. DDMarlinPandora
cd DDMarlinPandora && git checkout test-hcal-cell-dimensions
mkdir build install && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install \
  -DCMAKE_MODULE_PATH=$PANDORA_CMAKE_MODULE_PATH
make install -j8
cd .. && k4_local_repo
cd $WORKDIR
```

---

## 2. Quick restart (fresh shell, already compiled)

```bash
source /afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal/FCC_ALLEGRO_TileCal/setup.sh
```

To change the ALLEGRO geometry version, edit the `ALLEGRO_VERSION` variable at
the top of `setup.sh`. The compact file path is then available as
`$ALLEGRO_COMPACT` in your shell.

---

## 3. Running the simulation

After sourcing `setup.sh`, the compact file is available as `$ALLEGRO_COMPACT`.

```bash
# Photons — 10 GeV at theta=60 deg
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "10*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle gamma \
  --numberOfEvents 100 \
  --outputFile ALLEGRO_sim_photon.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT

# K0L — 50 GeV at theta=60 deg
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "50*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle kaon0L \
  --numberOfEvents 100 \
  --outputFile ALLEGRO_sim_kaon0L.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT

# Electrons — 10 GeV at theta=60 deg
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "10*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle e- \
  --numberOfEvents 100 \
  --outputFile ALLEGRO_sim_electron.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT

# Pions — 50 GeV at theta=60 deg
ddsim --enableGun --gun.distribution uniform \
  --gun.energy "50*GeV" \
  --gun.thetaMin "60*deg" --gun.thetaMax "60*deg" \
  --gun.particle pi- \
  --numberOfEvents 100 \
  --outputFile ALLEGRO_sim_pi.root \
  --random.enableEventSeed --random.seed 42 \
  --compactFile $ALLEGRO_COMPACT
```

---

## 4. Running the reconstruction

```bash
k4run ALLEGROReconstruction.py --inputFiles ALLEGRO_sim_photon.root   --outputFile ALLEGRO_reco_photon.root
k4run ALLEGROReconstruction.py --inputFiles ALLEGRO_sim_kaon0L.root   --outputFile ALLEGRO_reco_kaon0L.root
k4run ALLEGROReconstruction.py --inputFiles ALLEGRO_sim_electron.root --outputFile ALLEGRO_reco_electron.root
k4run ALLEGROReconstruction.py --inputFiles ALLEGRO_sim_pi.root       --outputFile ALLEGRO_reco_pi.root
```

Inspect output collections:
```bash
podio-dump ALLEGRO_reco_kaon0L.root
```

Quick check in ROOT:
```bash
root -l ALLEGRO_reco_kaon0L.root
# Total PFO energy
events->Draw("Sum$(PandoraPFANewPFOs.energy)","","")
# Compare with raw calorimeter cell sum
events->Draw("Sum$(HCalBarrelReadoutPositioned.energy) + Sum$(ECalBarrelModuleThetaMergedPositioned.energy)","")
```

---

## Notes

- Output ROOT files are large — store them on EOS (`/eos/user/r/ravinab/`)
  rather than AFS, and do not commit them to git.
- The `2026-04-08` nightly may be updated or removed. If it becomes unavailable,
  identify a replacement nightly where the full build chain compiles, update
  `KEY4HEP_RELEASE` in `setup.sh`, and rebuild.
- The geometry version is controlled by `ALLEGRO_VERSION` in `setup.sh`.
  Current value: `ALLEGRO_o2_v01`.