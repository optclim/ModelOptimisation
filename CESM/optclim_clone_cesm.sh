#!/bin/bash

# maybe use serial queue, but its fast enough to be on login I think...?

if [[ ${CIMEROOT}"x" == "x" ]]
then
	. ~/.cime/lite_setup_for_cesm
fi

#. ~/.cime/setup_for_cesm

OLDCASEDIR=$1
NEWCASEDIR=$2

casename=$(basename $NEWCASEDIR)
outroot=$(dirname $NEWCASEDIR)
echo casename $casename

cd $outroot

# https://www.cesm.ucar.edu/models/cesm1.0/cesm/cesm_doc_1_0_4/x747.html
# useful but is htere a later version?

#not sure I have to do the reset and build  - or if namelist stuff
# should be set up first.
# https://www.cesm.ucar.edu/events/tutorials/2017/practical4-hannay.pdf
# slide 11

$CIMEROOT/scripts/create_clone --silent \
	--case ${casename} --clone ${OLDCASEDIR} \
         	--keepexe --cime-output-root ${NEWCASEDIR}

cd ${NEWCASEDIR}
# check documentation for whant namelists get built - in submit or here.
##?./case.setup --reset # ? superfluous:
# after made edits: ./case.build



