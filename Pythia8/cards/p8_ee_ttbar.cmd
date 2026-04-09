! p8_ee_ttbar.cmd
! ttbar production at e+e- collider, W decays to electron channel only
! Covers: fully hadronic, semileptonic-e, dileptonic-ee
! (tau and muon W decay channels are excluded)
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

! --- Process: ttbar via Z/gamma* ---
WeakSingleBoson:ffbar2gmZ = on
23:onMode = off
23:onIfAny = 6        ! Z/gamma* -> ttbar only

! --- Top decay: t -> W b ---
6:onMode = off
6:onIfAny = 24
-6:onMode = off
-6:onIfAny = -24

! --- W decays: electron channel only (covers hadronic, semileptonic-e, dileptonic-ee) ---
! PDG 1=d, 2=u, 3=s, 11=e-, 12=nu_e (onIfAny matches by |PDG|, covers antiparticles)
24:onMode = off
24:onIfAny = 1 2 3 11 12
-24:onMode = off
-24:onIfAny = 1 2 3 11 12
