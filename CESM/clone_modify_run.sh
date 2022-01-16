#!/bin/bash

# maybe use serial queue, but its fast enough to be on login I think...?

if [[ ${CIMEROOT}"x" == "x" ]]
then
	. ~/.cime/lite_setup_for_cesm
fi

. ~/.cime/setup_for_cesm

OLDCASEDIR=$1
NEWCASEDIR=$2

casename=$(basename $NEWCASEDIR)

echo casename $casename

$CIMEROOT/scripts/create_clone --case ${casename} --clone ${OLDCASEDIR} \
         	--keepexe --cime-output-root ${PWD}

# include a dummy namelist amendments

cd $casename

echo HERE append to the user_nl files

cat << EOT >> user_nl_cam
dust_emis_fact         = 0.60D0
EOT

# add checks: some CIME  options bundle these below
./case.setup --reset
./preview_run 

./case.build  # quick in view of the clone.
./case.submit 


