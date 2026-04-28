#ifndef JETCLUSTERING_H
#define JETCLUSTERING_H

#include <vector>
#include <cmath>

#include "ROOT/RVec.hxx"
#include "edm4hep/ReconstructedParticleData.h"

#include "fastjet/PseudoJet.hh"
#include "fastjet/ClusterSequence.hh"
#include "fastjet/JetDefinition.hh"

namespace JetClustering {

  // PDG codes to exclude from jet clustering
  // Electrons (11), muons (13), photons (22) — and their antiparticles
  inline bool isExcluded(int pdg) {
    int absPdg = std::abs(pdg);
    return absPdg == 11 || absPdg == 13 || absPdg == 22;
  }

  // Build FastJet PseudoJets from PFO collections, excluding leptons and photons
  inline std::vector<fastjet::PseudoJet> buildInputs(
      const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
  {
    std::vector<fastjet::PseudoJet> inputs;
    inputs.reserve(pfos.size());
    for (size_t i = 0; i < pfos.size(); ++i) {
      if (isExcluded(pfos[i].PDG)) continue;
      fastjet::PseudoJet pj(
          pfos[i].momentum.x,
          pfos[i].momentum.y,
          pfos[i].momentum.z,
          pfos[i].energy
      );
      pj.set_user_index(i);
      inputs.push_back(pj);
    }
    return inputs;
  }

  // Cluster jets and return sorted by pt (descending)
  inline std::vector<fastjet::PseudoJet> clusterJets(
      const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
      double R, double ptMin)
  {
    auto inputs = buildInputs(pfos);
    if (inputs.empty()) return {};
    fastjet::JetDefinition jetDef(fastjet::antikt_algorithm, R);
    fastjet::ClusterSequence cs(inputs, jetDef);
    auto jets = cs.inclusive_jets(ptMin);
    fastjet::sorted_by_pt(jets);
    return jets;
  }


  class PyInterface {
  public:

    // --- Jet properties (anti-kt R=0.5, ptMin=1 GeV by default) ---

    static ROOT::VecOps::RVec<float> getJet_pt(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.pt());
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_eta(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.eta());
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_phi(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.phi_std());  // phi in [-pi, pi]
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_e(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.e());
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_mass(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.m());
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_px(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.px());
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_py(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.py());
      return result;
    }

    static ROOT::VecOps::RVec<float> getJet_pz(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      auto jets = clusterJets(pfos, R, ptMin);
      ROOT::VecOps::RVec<float> result;
      for (auto& j : jets)
        result.push_back(j.pz());
      return result;
    }

    static float getJet_n(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos,
        double R = 0.5, double ptMin = 1.0)
    {
      return (float)clusterJets(pfos, R, ptMin).size();
    }

    // --- Isolated leptons (electrons and muons separately) ---

    static ROOT::VecOps::RVec<float> getElectron_px(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 11) result.push_back(p.momentum.x);
      return result;
    }

    static ROOT::VecOps::RVec<float> getElectron_py(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 11) result.push_back(p.momentum.y);
      return result;
    }

    static ROOT::VecOps::RVec<float> getElectron_pz(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 11) result.push_back(p.momentum.z);
      return result;
    }

    static ROOT::VecOps::RVec<float> getElectron_e(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 11) result.push_back(p.energy);
      return result;
    }

    static float getElectron_n(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      float n = 0;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 11) n++;
      return n;
    }

    static ROOT::VecOps::RVec<float> getMuon_px(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 13) result.push_back(p.momentum.x);
      return result;
    }

    static ROOT::VecOps::RVec<float> getMuon_py(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 13) result.push_back(p.momentum.y);
      return result;
    }

    static ROOT::VecOps::RVec<float> getMuon_pz(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 13) result.push_back(p.momentum.z);
      return result;
    }

    static ROOT::VecOps::RVec<float> getMuon_e(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      ROOT::VecOps::RVec<float> result;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 13) result.push_back(p.energy);
      return result;
    }

    static float getMuon_n(
        const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& pfos)
    {
      float n = 0;
      for (auto& p : pfos)
        if (std::abs(p.PDG) == 13) n++;
      return n;
    }

  }; // PyInterface

} // namespace JetClustering

#endif // JETCLUSTERING_H