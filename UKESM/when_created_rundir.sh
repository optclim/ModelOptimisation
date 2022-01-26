#!/bin/bash

# IF any such exist, copy scripts that need to be in the rundir.
# maybe none.... 

if [[ ${OPTCLIMTOP}"x" == "x" ]]
then
	. ~/setup_optclim2.sh
fi

   # check if there is anything to copy

COPYING="$OPTCLIMTOP/UKESM/optclim_submit_cesm.sh"
if [[ -f $COPYING ]]
then
  cp $COPYING .
else
	echo not found $COPYING to be copied
	exit 1
fi





