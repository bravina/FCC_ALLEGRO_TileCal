! p8_ee_ttbar.cmd
! ttbar production at e+e- collider via gamma*/Z (s-channel)
! W decays restricted to electron channel only:
!   covers fully hadronic, semileptonic-e, and dileptonic-ee
!   (tau and muon W decay channels excluded)
!
! CoM energy and seed can be overridden on the command line:
!   pythia --card p8_ee_ttbar.cmd --ecm 365 --seed 42 --nevents 1000
!
! Default: 365 GeV (just above ttbar threshold ~346 GeV)

! --- Output verbosity ---
Init:showChangedSettings = on
Init:showChangedParticleData = off
Next:numberCount = 1000
Next:numberShowInfo = 1
Next:numberShowProcess = 1
Next:numberShowEvent = 0
Main:timesAllowErrors = 1000

! --- Beams ---
Beams:idA = 11
Beams:idB = -11
Beams:eCM = 365.0     ! default; override with --ecm

! --- Process: e+e- -> ttbar via gamma*/Z (s-channel) ---
Top:ffbar2ttbar(s:gmZ) = on

! --- Top decay: t -> W b only ---
6:onMode = off
6:onIfAny = 24
-6:onMode = off
-6:onIfAny = -24

! --- W decays: electron channel only ---
! PDG 1=d, 2=u, 3=s, 11=e-, 12=nu_e
! onIfAny matches by |PDG|, so covers both W+ and W- automatically
24:onMode = off
24:onIfAny = 1 2 3 11 12
-24:onMode = off
-24:onIfAny = 1 2 3 11 12
