#include "Pythia8/Pythia.h"
#include "Pythia8Plugins/HepMC3.h"
using namespace Pythia8;


int main (int argc, char *argv[])
{
    std::string cardName = "cards/p8_ee_Zuds_ecm91.cmd";
    std::string outputName = "events";
    std::string seed = "12345";
    size_t nevents = 100;
    for(int i=1;i<argc;i++)
    {
      if(strcmp(argv[i],"--card")==0) {
        cardName = std::string(argv[i+1]);
        cout << "INFO::pythia interface card: "<< cardName << endl;
      }
      else if(strcmp(argv[i],"--nevents")==0) {
        nevents = atoi(argv[i+1]);
        cout << "INFO::generating " << nevents << " events..." << endl;
      }
      else if(strcmp(argv[i],"--output")==0) {
         outputName = std::string(argv[i+1]);
         cout << "INFO::events will be written in " << outputName << endl;
      }
      else if(strcmp(argv[i],"--seed")==0) {
        seed = std::string(argv[i+1]);
        cout << "INFO::pythia random seed: "<< seed << endl;
      }
    }
    if ( !outputName.ends_with(".hepmc") ) outputName += ".hepmc";


    Pythia pythia;
    pythia.readString("Random:setSeed = on");
    pythia.readString("Random:seed = " + seed);  // any integer seed
    pythia.readFile(cardName);
    //int nEvent = pythia.mode("Main:numberOfEvents");

    pythia.init();

    HepMC3::Pythia8ToHepMC3 toHepMC;
    HepMC3::WriterAscii ascii_io(outputName);

    for (int iEvent = 0; iEvent < nevents; ++iEvent) {
        if (!pythia.next()) continue;
        HepMC3::GenEvent hepmcevt;
        toHepMC.fill_next_event(pythia, &hepmcevt);
        ascii_io.write_event(hepmcevt);
    }

    ascii_io.close();
    pythia.stat();

    return 0;
}
