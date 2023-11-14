#!/bin/bash --login
# note the --login is needed to get the rose environment
#
# Inputs:
# OPTCLIM run directory on Archer2 associated withn a new model instance
# Base suite to be cloned, noting that it has to be adapted to work with OPTCLIM

# Processing:
# create a new rose suite for this new run

# Called from:
# runAlgorithm.py, which sets up models and  paramaters; that calls UKESM.py
# which runs ssh puma2 ..... to call this.
# 

 OPTCLIM_RUN_DIR=$1
 OPTCLIM_BASE_SUITE=$2

 optclim_study=$(basename $(dirname $OPTCLIM_RUN_DIR))
 echo $0: $OPTCLIM_STUDY_DIR  $OPTCLIM_BASE_SUITE

 ARUN=$(basename $OPTCLIM_RUN_DIR)
 echo ARUN $ARUN
 cd /home/n02/n02/$USER/roses

 new_suite=${ARUN}_${OPTCLIM_BASE_SUITE}

 if [[ -d $new_suite ]]
 then
          # force uniqueness - might be unnecessary - consider later!
          # $$ is hte process number of this process. Could use _1,_2 etc

             new_suite=${new_suite}_$$
 fi
 echo copying rsync -rvL $OPTCLIM_BASE_SUITE/*  $new_suite
 rsync -rvL $OPTCLIM_BASE_SUITE/*  $new_suite

 cd $new_suite

 cp rose-suite.conf orig-rose-suite.conf
 sed -i -e "s/xxxx/${OPTCLIM_RUN_DIR}/g" rose-suite.conf

 echo in new suite $new_suite made following differences:
 diff orig-rose-suite.conf rose-suite.conf 

 rose suite-run --no-gcontrol

