#!/bin/bash

# maybe user serial queue, but its fast enough to be on login I think...?

echo include serial queue prefereably

. ~/.cime/setup_for_cesm

NEWCASEDIR=$1
OLDCASEDIR=$2

casename=$(basename $NEWCASEDIR)

echo casename $casename

$CIMEROOT/scripts/create_clone --case ${casename} --clone ${OLDCASEDIR} --keepexe

# include a dummy namelist amendments

cd $casename

echo HERE append to the user_nl files

#cat << EOT >> user_nl_cam
#dust_emis_fact         = 0.60D0
#EOT
# and dummy run control?

./case.setup --reset
./preview_run 

./case.build  # quick in view of the clone.
./case.submit 


