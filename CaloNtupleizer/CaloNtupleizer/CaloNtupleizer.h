
#ifndef  CALONTUPLEIZER_ANALYZERS_H
#define  CALONTUPLEIZER_ANALYZERS_H

#include <cmath>
#include <vector>
#include <map>
#include "ROOT/RVec.hxx"
#include "edm4hep/CalorimeterHitData.h"
#include "edm4hep/SimCalorimeterHitData.h"
#include "edm4hep/ClusterData.h"
#include "edm4hep/MCParticleData.h"
#include "edm4hep/MCParticle.h"
#include "edm4hep/ReconstructedParticleData.h"
#include "DD4hep/Detector.h"

#include "TVector3.h"
#include "TLorentzVector.h"


namespace CaloNtupleizer{
  std::map<std::string,dd4hep::DDSegmentation::BitFieldCoder*> m_decoder;
  std::map<std::string,dd4hep::DDSegmentation::Segmentation*> m_segmentation;

  class PyInterface {
     public:
        static void loadGeometry(std::string xmlGeometryPath, std::vector<std::string> readoutName);

        /*
        /// select layers
        struct sel_layers {
          public:
            sel_layers(int arg_min=0, int arg_max=10);
            ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> operator()(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);

          private:
           int _min;//> min layer
           int _max;//> max layer
        };
        */

    // SIM calo hits (single cells)
    static  ROOT::VecOps::RVec<float> getSimCellID (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_r (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_x (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_y (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_z (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_phi (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_theta (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_eta (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<int> getSimCaloHit_depth (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in,const int decodingVal);
    static  ROOT::VecOps::RVec<float> getSimCaloHit_energy (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<TVector3> getSimCaloHit_positionVector3 (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in);


    // calo hits (single cells)
    static  ROOT::VecOps::RVec<float> getCaloHit_x (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getCaloHit_y (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getCaloHit_z (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getCaloHit_dEdl (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<float> getCaloHit_phi (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<int> getCaloHit_phiIdx(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<int> getCaloHit_moduleIdx(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<float> getCaloHit_theta (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<int> getCaloHit_thetaIdx(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<int> getCaloHit_layer (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<int> getCaloHit_pseudoLayer (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<float> getCaloHit_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<TVector3> getCaloHit_positionVector3 (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);
    static  ROOT::VecOps::RVec<float> getCaloLayer_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName);
    static  ROOT::VecOps::RVec<float> getCaloPseudoLayer_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName);
    static float getTotalCalo_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in);

    // calo clusters
    static  ROOT::VecOps::RVec<float> getCaloCluster_x (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<float> getCaloCluster_y (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<float> getCaloCluster_z (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<float> getCaloCluster_phi (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<float> getCaloCluster_theta (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<float> getCaloCluster_eta (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<float> getCaloCluster_energy (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<TVector3> getCaloCluster_positionVector3 (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<int> getCaloCluster_firstCell (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<int> getCaloCluster_lastCell (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in);
    static  ROOT::VecOps::RVec<std::vector<float>> getCaloCluster_energyInLayers (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in, const   ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& cells, const int nLayers=12);

    // PFO
    static  ROOT::VecOps::RVec<int32_t> getPFO_PDG (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static  ROOT::VecOps::RVec<float> getPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static  ROOT::VecOps::RVec<TVector3> getPFO_positionVector3 (const   ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static  ROOT::VecOps::RVec<TVector3> getPFO_momentumVector3 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getTotalPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getNeutralHadronPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getChargedHadronPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getPhotonPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getElectronPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getNeutralHadronPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getChargedHadronPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getPhotonPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getElectronPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in);
    static float getKlongPFO_dphi (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2);
    static float getKlongPFO_dtheta (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2);
    static float getKlongPFO_dphi1 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2);
    static float getKlongPFO_dtheta1 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2);


    // SimParticleSecondary
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_x (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_y (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_z (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_phi (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_theta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_eta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_energy (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getSimParticleSecondaries_PDG (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);

    // MCParticles
    static  ROOT::VecOps::RVec<float> getMCParticle_phi (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getMCParticle_theta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<float> getMCParticle_energy (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<int> getMCParticle_PDG (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  ROOT::VecOps::RVec<int> getMCParticle_status (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  float getQQ_cosTheta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);
    static  float getMCParticle_vertex_z (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in);


  }; // PyInterface

  //-------------------------------------------------
  // Function definition
  //-------------------------------------------------
  void PyInterface::loadGeometry(std::string xmlGeometryPath, std::vector<std::string> readoutName){
    dd4hep::Detector* dd4hepgeo = &(dd4hep::Detector::getInstance());
    dd4hepgeo->fromCompact(xmlGeometryPath);
    dd4hepgeo->volumeManager();
    dd4hepgeo->apply("DD4hepVolumeManager", 0, 0);
    for(const auto readout : readoutName)
    {
      m_decoder[readout] = dd4hepgeo->readout(readout).idSpec().decoder();
      m_segmentation[readout] = dd4hepgeo->readout(readout).segmentation().segmentation();
    }
  }

/*
PyInterface::sel_layers::sel_layers(int arg_min, int arg_max) : _min(arg_min), _max(arg_max) {};

ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>  PyInterface::sel_layers::operator() (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in) {
  ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> res;
  for (auto & p: in){
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    int layer = m_decoder->get(cellId, "layer");
    if (layer>_min && layer<_max)res.emplace_back(p);
  }
  return res;
}
*/
// SIM calo hit
ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_r (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(std::sqrt(p.position.x * p.position.x + p.position.y * p.position.y));
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_x (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.x);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_y (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.y);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_z (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.z);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_phi (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Phi());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_theta (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Theta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_eta (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Eta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCellID (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    result.push_back(p.cellID);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimCaloHit_energy (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.energy);
  }
  return result;
}

ROOT::VecOps::RVec<int> PyInterface::getSimCaloHit_depth (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in,const int decodingVal){
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    result.push_back(p.cellID >> decodingVal & (8-1) );
  }
  return result;
}

ROOT::VecOps::RVec<TVector3> PyInterface::getSimCaloHit_positionVector3 (const ROOT::VecOps::RVec<edm4hep::SimCalorimeterHitData>& in){
  ROOT::VecOps::RVec<TVector3> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3);
  }
  return result;
}

// calo hit
ROOT::VecOps::RVec<float> PyInterface::getCaloHit_x (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.x);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloHit_y (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.y);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloHit_z (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.z);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloHit_dEdl(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName) {
  ROOT::VecOps::RVec<float> result;
  for (auto &p : in) {
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    float dz = m_segmentation[readoutName]->cellDimensions(cellId)[0];
    result.push_back(p.energy/dz*fabs(cos(t3.Theta())) );
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloHit_phi (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Phi());
  }
  return result;
}

ROOT::VecOps::RVec<int>
PyInterface::getCaloHit_phiIdx(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName) {
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    result.push_back(m_decoder[readoutName]->get(cellId, "phi"));
  }
  return result;
}

ROOT::VecOps::RVec<int> PyInterface::getCaloHit_moduleIdx(
    const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName) {
  ROOT::VecOps::RVec<int> result;
  for (auto &p : in) {
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    result.push_back(m_decoder[readoutName]->get(cellId, "module"));
  }
  return result;
}

ROOT::VecOps::RVec<int>
PyInterface::getCaloHit_thetaIdx(const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData> &in, const std::string &readoutName) {
  ROOT::VecOps::RVec<int> result;
  for (auto &p : in) {
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    result.push_back(m_decoder[readoutName]->get(cellId, "theta"));
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloHit_theta (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Theta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloHit_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.energy);
  }
  return result;
}

ROOT::VecOps::RVec<int> PyInterface::getCaloHit_layer (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName){
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    result.push_back(m_decoder[readoutName]->get(cellId, "layer"));
  }
  return result;
}

ROOT::VecOps::RVec<int> PyInterface::getCaloHit_pseudoLayer (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName){
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    result.push_back(m_decoder[readoutName]->get(cellId, "pseudoLayer"));
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloLayer_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName){
  ROOT::VecOps::RVec<float> result;
  if(in.size()==0) return result;
  dd4hep::DDSegmentation::CellID aCellId = in[0].cellID;
  int systemId = m_decoder[readoutName]->get(aCellId, "system");
  size_t nLayers = 0;
  if( systemId == 4 ) nLayers = 11; // ECal barrel
  if( systemId == 8 ) nLayers = 13; // HCal barrel
  if( systemId == 9 ) nLayers = 37; // HCal endcap

  std::vector<float> totalEnergy(nLayers);

  for (auto & p: in){
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    totalEnergy[m_decoder[readoutName]->get(cellId, "layer")] += p.energy;
  }
  for(auto energy: totalEnergy) result.push_back(energy);

  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloPseudoLayer_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in, const std::string &readoutName){
  ROOT::VecOps::RVec<float> result;
  if(in.size()==0) return result;
  std::vector<float> totalEnergy(16);

  for (auto & p: in){
    dd4hep::DDSegmentation::CellID cellId = p.cellID;
    totalEnergy[m_decoder[readoutName]->get(cellId, "pseudoLayer")] += p.energy;
  }
  for(auto energy: totalEnergy) result.push_back(energy);

  return result;
}

ROOT::VecOps::RVec<TVector3> PyInterface::getCaloHit_positionVector3 (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  ROOT::VecOps::RVec<TVector3> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3);
  }
  return result;
}

float PyInterface::getTotalCalo_energy (const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& in){
  float result = 0;
  for (auto & p: in){
    result += p.energy;
  }
  return result;
}


// calo cluster
ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_x (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.x);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_y (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.y);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_z (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.position.z);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_phi (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Phi());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_theta (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Theta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_eta (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3.Eta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getCaloCluster_energy (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.energy);
  }
  return result;
}

ROOT::VecOps::RVec<TVector3> PyInterface::getCaloCluster_positionVector3 (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<TVector3> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.position.x, p.position.y, p.position.z);
    result.push_back(t3);
  }
  return result;
}

ROOT::VecOps::RVec<int> PyInterface::getCaloCluster_firstCell (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    result.push_back(p.hits_begin);
  }
  return result;
}

ROOT::VecOps::RVec<int> PyInterface::getCaloCluster_lastCell (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in){
  ROOT::VecOps::RVec<int> result;
  for (auto & p: in){
    result.push_back(p.hits_end);
  }
  return result;
}

/*
ROOT::VecOps::RVec<std::vector<float>>
PyInterface::getCaloCluster_energyInLayers (const ROOT::VecOps::RVec<edm4hep::ClusterData>& in,
                               const ROOT::VecOps::RVec<edm4hep::CalorimeterHitData>& cells,
                               const int nLayers) {
  static const int layer_idx = m_decoder->index("layer");
  static const int cryo_idx = m_decoder->index("cryo");
  ROOT::VecOps::RVec<std::vector<float>> result;
  result.reserve(in.size());

  for (const auto & c: in) {
    std::vector<float> energies(nLayers, 0);
    for (auto i = c.hits_begin; i < c.hits_end; i++) {
      int layer = m_decoder->get(cells[i].cellID, layer_idx);
      int cryoID = m_decoder->get(cells[i].cellID, cryo_idx);
      if(cryoID == 0) {
        energies[layer] += cells[i].energy;
      }
    }
    result.push_back(energies);
  }
  return result;
}
*/

// PFO
ROOT::VecOps::RVec<int32_t> PyInterface::getPFO_PDG (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  ROOT::VecOps::RVec<int32_t> result;
  for (auto & p: in){
    result.push_back(p.PDG);
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.energy);
  }
  return result;
}

ROOT::VecOps::RVec<TVector3> PyInterface::getPFO_positionVector3 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  ROOT::VecOps::RVec<TVector3> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.referencePoint.x, p.referencePoint.y, p.referencePoint.z);
    result.push_back(t3);
  }
  return result;
}

ROOT::VecOps::RVec<TVector3> PyInterface::getPFO_momentumVector3 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  ROOT::VecOps::RVec<TVector3> result;
  for (auto & p: in){
    TVector3 t3;
    t3.SetXYZ(p.momentum.x, p.momentum.y, p.momentum.z);
    result.push_back(t3);
  }
  return result;
}

float PyInterface::getTotalPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  float result = 0;
  for (auto & p: in){
    result += p.energy;
  }
  return result;
}

float PyInterface::getNeutralHadronPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  float result = 0;
  for (auto & p: in){
    if(p.PDG == 2112) result += p.energy;
  }
  return result;
}

float PyInterface::getChargedHadronPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  float result = 0;
  for (auto & p: in){
    if(p.PDG == 211 || p.PDG == -211) result += p.energy;
  }
  return result;
}

float PyInterface::getPhotonPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  float result = 0;
  for (auto & p: in){
    if(p.PDG == 22) result += p.energy;
  }
  return result;
}

float PyInterface::getElectronPFO_energy (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  float result = 0;
  for (auto & p: in){
    if(p.PDG == 11 || p.PDG == -11) result += p.energy;
  }
  return result;
}

float PyInterface::getPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  return in.size();
}

float PyInterface::getNeutralHadronPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  int result = 0;
  for (auto & p: in){
    if(p.PDG == 2112) result ++;
  }
  return result;
}

float PyInterface::getChargedHadronPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  int result = 0;
  for (auto & p: in){
    if(p.PDG == 211 || p.PDG == -211) result ++;
  }
  return result;
}

float PyInterface::getPhotonPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  int result = 0;
  for (auto & p: in){
    if(p.PDG == 22) result ++;
  }
  return result;
}

float PyInterface::getElectronPFO_number (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in){
  int result = 0;
  for (auto & p: in){
    if(p.PDG == 11 || p.PDG == -11) result ++;
  }
  return result;
}

float PyInterface::getKlongPFO_dphi (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2){
  TVector3 pfo;
  for (auto & p: in1){
    if(p.PDG!=2112) continue;
    TVector3 t3;
    t3.SetXYZ(p.momentum.x, p.momentum.y, p.momentum.z);
    pfo+=t3;
  }
  TVector3 klong;
  klong.SetXYZ(in2[1].momentum.x, in2[1].momentum.y, in2[1].momentum.z);
  return pfo.DeltaPhi(klong);
}


float PyInterface::getKlongPFO_dtheta (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2){
  TVector3 pfo;
  for (auto & p: in1){
    if(p.PDG!=2112) continue;
    TVector3 t3;
    t3.SetXYZ(p.momentum.x, p.momentum.y, p.momentum.z);
    pfo+=t3;
  }
  TVector3 klong;
  klong.SetXYZ(in2[1].momentum.x, in2[1].momentum.y, in2[1].momentum.z);
  return pfo.Theta() - klong.Theta();
}

float PyInterface::getKlongPFO_dphi1 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2){
  TVector3 pfo;
  for (auto & p: in1){
    if(p.PDG!=2112) continue;
    TVector3 t3;
    t3.SetXYZ(p.referencePoint.x, p.referencePoint.y, p.referencePoint.z);
    pfo+=t3;
  }
  TVector3 klong;
  klong.SetXYZ(in2[1].momentum.x, in2[1].momentum.y, in2[1].momentum.z);
  return pfo.DeltaPhi(klong);
}


float PyInterface::getKlongPFO_dtheta1 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2){
  TVector3 pfo;
  for (auto & p: in1){
    if(p.PDG!=2112) continue;
    TVector3 t3;
    t3.SetXYZ(p.referencePoint.x, p.referencePoint.y, p.referencePoint.z);
    pfo+=t3;
  }
  TVector3 klong;
  klong.SetXYZ(in2[1].momentum.x, in2[1].momentum.y, in2[1].momentum.z);
  return pfo.Theta() - klong.Theta();
}


/*
float PyInterface::getNeutralPFO_dphi2 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2){
  float phi = 0;
  float energy = 0;
  for (auto & p: in1){
    if(p.PDG!=2112) continue;
    TVector3 t3;
    t3.SetXYZ(p.referencePoint.x, p.referencePoint.y, p.referencePoint.z);
    phi+=(t3.Phi()*p.energy);
    energy+=p.energy;
  }
  phi/=energy;
  TVector3 klong;
  klong.SetXYZ(in2[1].momentum.x, in2[1].momentum.y, in2[1].momentum.z);
  return TVector2::Phi_mpi_pi(phi - klong.Phi());
}


float PyInterface::getNeutralPFO_dtheta2 (const ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>& in1,
                                       const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in2){
  float theta = 0;
  float energy = 0;
  for (auto & p: in1){
    if(p.PDG!=2112) continue;
    TVector3 t3;
    t3.SetXYZ(p.referencePoint.x, p.referencePoint.y, p.referencePoint.z);
    theta+=(t3.Theta()*p.energy);
    energy+=p.energy;
  }
  theta/=energy;
  TVector3 klong;
  klong.SetXYZ(in2[1].momentum.x, in2[1].momentum.y, in2[1].momentum.z);
  return theta - klong.Theta();
}
*/
//----------------------------------------------------------------

ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_x (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in){
    result.push_back(p.vertex.x);
  }
  return result;
}


ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_y (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
for (auto & p: in) {
  result.push_back(p.vertex.y);
}
return result;
}


ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_z (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
for (auto & p: in) {
  result.push_back(p.vertex.z);
}
return result;
}


ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_PDG (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
    ROOT::VecOps::RVec<float> result;
    for (auto & p: in) {
      result.push_back(p.PDG);
    }
    return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_phi (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.Phi());
  }
  return result;
}


ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_theta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.Theta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_eta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.Eta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getSimParticleSecondaries_energy (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.E());
  }
  return result;
}

// MCParticle
ROOT::VecOps::RVec<int> PyInterface::getMCParticle_PDG (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
    ROOT::VecOps::RVec<int> result;
    for (auto & p: in) {
      result.push_back(p.PDG);
    }
    return result;
}

ROOT::VecOps::RVec<int> PyInterface::getMCParticle_status (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
    ROOT::VecOps::RVec<int> result;
    for (auto & p: in) {
      result.push_back(p.generatorStatus);
    }
    return result;
}

ROOT::VecOps::RVec<float> PyInterface::getMCParticle_phi (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.Phi());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getMCParticle_theta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.Theta());
  }
  return result;
}

ROOT::VecOps::RVec<float> PyInterface::getMCParticle_energy (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  ROOT::VecOps::RVec<float> result;
  for (auto & p: in) {
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result.push_back(tlv.E());
  }
  return result;
}

float PyInterface::getQQ_cosTheta (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  float result = -1;
  for (auto & p: in) {
    if(p.generatorStatus != 23) continue;
    TLorentzVector tlv;
    tlv.SetXYZM(p.momentum.x, p.momentum.y, p.momentum.z, p.mass);
    result = cos(tlv.Theta());
    break;
  }
  return result;
}

float PyInterface::getMCParticle_vertex_z (const ROOT::VecOps::RVec<edm4hep::MCParticleData>& in){
  return in[0].vertex.z;
}


}// CaloNtupleizer
#endif
