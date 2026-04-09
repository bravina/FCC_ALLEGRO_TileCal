#!/bin/bash
# Compile all local packages from scratch.
# Usage: source compile.sh
# Must be run AFTER sourcing setup.sh (Key4hep environment must be active).
# Note: this wipes and rebuilds all build/install directories.

# PandoraCMakeSettings module needed to build PandoraSDK, LCContent, DDMarlinPandora
# (not present in latest nightly, taken from 2026-02-26 nightly)
export PANDORA_CMAKE_MODULE_PATH=/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/x86_64-almalinux9-gcc14.2.0-opt/pandorapfa/4.11.2-tyvaev/cmakemodules

cd ${WORKDIR}/PandoraSDK
export PANDORASDK_DIR=$(pwd)
rm -rf build install && mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install \
  -DCMAKE_MODULE_PATH=${PANDORA_CMAKE_MODULE_PATH}
make install -j16
cd ..
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/k4geo
rm -rf build install && mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j16
cd ..
k4_local_repo
export K4GEO=${PWD}/
cd ${WORKDIR}

cd ${WORKDIR}/k4RecTracker
rm -rf build install && mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j16
cd ..
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/LCContent
rm -rf build install && mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install \
  -DCMAKE_MODULE_PATH=${PANDORA_CMAKE_MODULE_PATH}
make install -j16
cd ..
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/DDMarlinPandora
rm -rf build install && mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install \
  -DCMAKE_MODULE_PATH=${PANDORA_CMAKE_MODULE_PATH}
make install -j16
cd ..
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/CaloNtupleizer
rm -rf build install && mkdir build install
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../install
make install -j16
cd ..
cd ${WORKDIR}

# Pythia8: compiled as a standalone C++ executable (not cmake)
cd ${WORKDIR}/Pythia8
export HEPMC3=/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/x86_64-almalinux9-gcc14.2.0-opt/hepmc3/3.3.1-3o4ayl/
export LD_LIBRARY_PATH=$PYTHIA8/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$HEPMC3/lib64:$LD_LIBRARY_PATH
mkdir -p bin
c++ -O2 -std=c++20 main.cc \
  -I$PYTHIA8/include \
  -I$HEPMC3/include \
  -L$PYTHIA8/lib \
  -L$HEPMC3/lib64 \
  -Wl,-rpath,$PYTHIA8/lib:$HEPMC3/lib64 \
  -lpythia8 -lHepMC3 -ldl \
  -o bin/pythia
cd ${WORKDIR}

echo "All packages compiled successfully."
