export HEPMC3=/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/x86_64-almalinux9-gcc14.2.0-opt/hepmc3/3.3.1-3o4ayl/
export LD_LIBRARY_PATH=$PYTHIA8/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$HEPMC3/lib64:$LD_LIBRARY_PATH

c++ -O2 -std=c++20 main.cc   -I$PYTHIA8/include   -I$HEPMC3/include   -L$PYTHIA8/lib   -L$HEPMC3/lib64   -Wl,-rpath,$PYTHIA8/lib:$HEPMC3/lib64 -lpythia8 -lHepMC3 -ldl   -o bin/pythia
