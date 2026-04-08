# FCC ALLEGRO TileCal Studies

Simulation, reconstruction, and analysis of the Tile Calorimeter for the ALLEGRO FCC-ee detector concept.

## Structure
- `simulation/` — DDsim steering files and k4run reconstruction configs
- `pandora/` — PandoraPFA settings
- `analysis/` — Python plotting and analysis scripts
- `particleflow/` — Custom particle-flow algorithm (in development)

## Setup (on LXPLUS)
```bash
source setup.sh
```

## Dependencies
- Key4hep nightly stack (via CVMFS)
- k4geo (fork: your-username/k4geo)
- k4RecCalorimeter (fork: your-username/k4RecCalorimeter)
