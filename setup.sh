#!/bin/bash
# Setup script for FCC ALLEGRO TileCal studies
# Usage: source setup.sh
# Run this at the start of every new shell session on LXPLUS.
# Assumes all dependency repos have already been compiled (see compile.sh and README).

# --- Configuration ---
export WORKDIR=/afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal/FCC_ALLEGRO_TileCal
export RUNSDIR=${WORKDIR}/runs
export ALLEGRO_VERSION=ALLEGRO_o1_v03   # change here if geometry version changes

# --- Key4hep environment (latest nightly) ---
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh

# --- Local packages ---
cd ${WORKDIR}/PandoraSDK
export PANDORASDK_DIR=$(pwd)
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/k4geo
k4_local_repo
export K4GEO=${PWD}/
cd ${WORKDIR}

cd ${WORKDIR}/k4RecTracker
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/LCContent
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/DDMarlinPandora
k4_local_repo
cd ${WORKDIR}

cd ${WORKDIR}/CaloNtupleizer
export LD_LIBRARY_PATH=/cvmfs/sw-nightlies.hsf.org/key4hep/releases/2026-02-26/x86_64-almalinux9-gcc14.2.0-opt/xerces-c/3.3.0-kq5wkb/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=${PWD}/install/lib64:$LD_LIBRARY_PATH
export PATH=${PATH}:${PWD}/scripts
cd ${WORKDIR}

# --- Convenience ---
export ALLEGRO_COMPACT=${K4GEO}/FCCee/ALLEGRO/compact/${ALLEGRO_VERSION}/${ALLEGRO_VERSION}.xml
export RUNDIR=${WORKDIR}/ALLEGRO_PandoraPFA/run   # directory with reco config and auxiliary files

echo "Environment ready."
echo "  Key4hep release : latest nightly"
echo "  ALLEGRO geometry: ${ALLEGRO_VERSION}"
echo "  Compact file    : ${ALLEGRO_COMPACT}"
echo "  Runs directory  : ${RUNSDIR}"
echo "  Reco config dir : ${RUNDIR}"
