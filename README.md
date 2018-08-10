# sims_movingObjects

#sample usage

makeB612obs.py --orbitFile veres_impactors_from_mike_26_run_1_to_75.des --outDir run --obsFile sims_movingObjects_veres_impactors_from_mike_26_run_1_to_75.txt --rFov 5.0 --interpolation linear --tStep 0.0416667 --ephMode nbody lsst_171year_test.db


#inputs and switches
--orbitFile
#orbit file
#example: --orbitFile veres_impactors_from_mike_26_run_1_to_75.des
#a des formatted list of orbits. Must have the following header files as the first line:
#the B612 version, makeB612obs.py, should not have any hardcoded cuts for MJD of orbit epochs
#keplerian:
!!OID FORMAT a e i node argperi M H t_0 INDEX N_PAR MOID COMPCODE
#cometary:
!!OID FORMAT q e i node argperi t_p H t_0 INDEX N_PAR MOID COMPCODE
#cartesian:
!!OID FORMAT x y z dx/dt dy/dt dz/dt H t_0 INDEX N_PAR MOID COMPCODE

--outDir
#directory for your outputs to go into
#example: --outDir run

--obsFile
#output observation file that will go into the out directory
#example: --obsFile sims_movingObjects_veres_impactors_from_mike_26_run_1_to_75.txt

--rFov
#radius of field of view in degrees #BB: IS THERE AN OPTION FOR A RECTANGULAR FIELD OF VIEW?
#example: --rFov 5.0
#NOTE THAT BY DEFAULT A PLAIN CIRCLE IS USED AS THE FOV AND NOT THE ACTUAL LSST FOOTPRINT. TO USE ACTUAL LSST FOOTPRINT USE --useCamera AS AN ADDITIONAL ARGUMENT

--interpolation
#type of interpolation between timesteps in ephemeris generation
#example --interpolation linear

--tStep
#time step size in the resultant per object ephemeris
example--tStep 0.0416667

--ephMode
#2 body or n-body mode in ephemeris generation
#example: --ephMode nbody 

--outDir
#ouput directory
#example:--outDir run

#The database
#does not have a switch, just has to be the last argument in the command #BB IS THIS CORRECT?
lsst_171year_test.db
#I used a sqlite3 database with a table called SummaryAllProps
The table has columns of:
index  observationId  fieldId     fieldRA  fieldDec   altitude     azimuth filter  night  observationStartTime  observationStartMJD  visitTime  visitExposureTime  seeingFwhmGeom  seeingFwhmEff  fiveSigmaDepth

index: index of table entry, starts with 0 for the first night
observationId: ID for that particular exposure
fieldId: ID for that particular footprint
fieldRA: field RA in degreees, 0 to 360 degrees.
fieldDec: field dec in degrees, -90 to 90 degrees.
altitude:altitude 0 to 90 degrees
azimuth: azimuth 0 to 360 degrees
filter:  filters, e.g., ugrizy
night:  number of the night in the survey
observationStartTime:  time in seconds since the start of the survey.
observationStartMJD:  TAI MJD of the exposure.
visitTime:  time spent at the observating footprint in seconds
visitExposureTime:  total exposure time in seconds
seeingFwhmGeom:  geometric seeing in arcseconds
seeingFwhmEff:  effective seeing in arcseconds
fiveSigmaDepth: five sigma depth in magnitudes

#output:
#The output has a similar format as the input database
objId: internal id given to asteroid, e.g.,8700
delta: toppocentric distance in au e.g., 0.798522614695 #BB: CONFIRM IF IN AU?
ra: actual RA of object, e.g., 311.556828631
dec: actual dec of object, e.g., -19.9310163181
magV: V magnitude of object, e.g., 21.9358327598
dradt: ra motion of object in degrees per day e.g., 0.811177888229 #BB: CONFIRM IF IN DEG/DAY?
ddecdt: dec motion of object in degrees per day e.g., -0.14056953306 #BB: CONFIRM IF IN DEG/DAY?
phase: phase angle in degrees, e.g., 57.2100094821
solarelon: solar elongation in degrees e.g., 80.854341462
velocity: total apparent angular veolcity in deg/day, e.g., 0.823267705075 #BB: PLEASE CONFIRM, DOES IT INCLUDE COS DEC FOR DRA COMPONENT?
time: e.g., 30833.5998059 #BB: WHY TWO COLUMNS FOR IDENTICAL OUTPUT AS observationStartMJD?
observationStartMJD: e.g., 30833.5998059 #BB: WHY TWO COLUMNS FOR IDENTICAL OUTPUT AS time?
fieldRA: field RA in degrees e.g., 311.140148 
fieldDec: field dec in degrees e.g., -23.881413
filter: filter e.g., z
visitExposureTime: eposure time in seconds e.g., 30.0
seeingFwhmEff: effective seeing in arcsec e.g., 1.00810070122
seeingFwhmGeom: geometric seeing in arcsec, USE THIS!e.g., 0.880658776406
fiveSigmaDepth: magtnidue for five sigma detection e.g., 22.0569556553
ra: field RA? e.g., 311.140148  #BB: WHY TWO COLUMNS FOR IDENTICAL OUTPUT AS fieldRA?
dec: field dec? e.g., -23.881413 #BB: WHY TWO COLUMNS FOR IDENTICAL OUTPUT AS fieldDec?
magFilter: magnitude after color correction e.g., 21.535972442 #BB: WHAT COLOR ARE YOU ASSUMING FOR ASTEROIDS IN YOUR CODE?
dmagColor: magnitude correction for aseroid color e.g., -0.399860317752  #BB: WHAT COLOR ARE YOU ASSUMING FOR ASTEROIDS IN YOUR CODE?
dmagTrail: magnitude correction fro trailing loss e.g., 0.198222135923 #BB: WHICH SEEING, EFFECTIVE OR GEOMETRIC ARE YOU USING FOR THIS CALCULATION? WHAT EQUATIONS ARE YOU USING?
dmagDetect: deltamagnitude for detection e.g., 0.245393025733 #BB WHAT IS THIS?
