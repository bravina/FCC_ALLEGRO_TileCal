#!/bin/bash
# Setup script for FCC ALLEGRO TileCal studies
# Usage: source setup.sh
# Run this at the start of every new shell session on LXPLUS.
# Assumes all dependency repos have already been built (see README).

# --- Configuration ---
export WORKDIR=/afs/cern.ch/work/r/ravinab/public/FCC_ALLEGRO_TileCal
export ALLEGRO_VERSION=ALLEGRO_o2_v01   # change here if geometry version changes
export KEY4HEP_RELEASE=2026-04-08

# --- Key4hep environment ---
source /cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r ${KEY4HEP_RELEASE}

# --- Local packages ---
cd ${WORKDIR}/k4geo            && k4_local_repo && export K4GEO=${PWD}/ && cd ${WORKDIR}
cd ${WORKDIR}/k4RecCalorimeter && k4_local_repo && cd ${WORKDIR}
cd ${WORKDIR}/k4RecTracker     && k4_local_repo && cd ${WORKDIR}
cd ${WORKDIR}/PandoraSDK       && k4_local_repo && cd ${WORKDIR}
cd ${WORKDIR}/LCContent        && k4_local_repo && cd ${WORKDIR}
cd ${WORKDIR}/DDMarlinPandora  && k4_local_repo && cd ${WORKDIR}

# --- Convenience ---
export ALLEGRO_COMPACT=$K4GEO/FCCee/ALLEGRO/compact/${ALLEGRO_VERSION}/${ALLEGRO_VERSION}.xml

echo "Environment ready."
echo "  Key4hep release : ${KEY4HEP_RELEASE}"
echo "  ALLEGRO geometry: ${ALLEGRO_VERSION}"
echo "  Compact file    : ${ALLEGRO_COMPACT}"
