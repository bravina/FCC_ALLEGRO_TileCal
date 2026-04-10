! p8_ee_ZZ.cmd
! Z-pair production at e+e- collider
! Z decays restricted to light quarks, b-quarks, and electron channel only:
!   covers fully hadronic (uds+b), semileptonic-e, and dileptonic-ee
!   (tau and muon Z decay channels excluded; Z->tt kinematically forbidden)
!
! CoM energy and seed can be overridden on the command line:
!   pythia --card p8_ee_ZZ.cmd --ecm 240 --seed 42 --nevents 1000
!
! Default: 240 GeV

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
Beams:eCM = 240.0     ! default; override with --ecm

! --- Process: e+e- -> ZZ ---
WeakDoubleBoson:ffbar2gmZgmZ = on

! --- Z decays: uds + b quarks and electron channel only ---
! PDG 1=d, 2=u, 3=s, 5=b, 11=e-, 12=nu_e
! onIfAny matches by |PDG|, covers both Z and gamma* contributions
23:onMode = off
23:onIfAny = 1 2 3 5 11 12
22:onMode = off
22:onIfAny = 1 2 3 5 11 12
