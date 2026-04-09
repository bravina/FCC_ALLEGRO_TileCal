! p8_ee_Zuds.cmd
! Z/gamma* -> uds dijets at e+e- collider
! CoM energy and seed can be overridden on the command line:
!   pythia --card p8_ee_Zuds.cmd --ecm 365 --seed 42 --nevents 1000
!
! Default: Z pole (91.188 GeV)

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
Beams:eCM = 91.188    ! default; override with --ecm

! --- Process: Z/gamma* -> qqbar (u, d, s only) ---
WeakSingleBoson:ffbar2gmZ = on
23:onMode = off
23:onIfAny = 1 2 3
22:onMode = off
22:onIfAny = 1 2 3
