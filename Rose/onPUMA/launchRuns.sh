#!/bin/bash
# launch new suites
# called in short term from pumatest cylc that gets requests for new OPtCLim runs.
# will then become with new PUMA, an ssh call

# OPTCLIM_STUDY_DIR=$1
# shift
# OPTCLIM_BASE_SUITE=$1
while (($#)) ; do

   #...
     ARUN = $1
     shift

     cd /home/$USER/roses

     new_suite=${ARUN}_${OPTCLIM_BASE_SUITE}

     if [[ -d $new_suite ]]
     then
          # force uniqueness - might be unnecessary - consider later!
          # $$ is hte process number of this process. Could use _1,_2 etc

             new_suite=${new_suite}_$$
     fi

     echo  cp -r $OPTCLIM_BASE_SUITE  $new_suite

     cd $new_suite

          # remove lines beginning with OPTCLIM from rose-suite.conf
     mv rose-suite.conf orig-rose-suite.conf
     sed '/^OPTCLIM/d' orig-rose-suite.conf > rose-suite.conf

          # then add the ones we want.
     echo OPTCLIM_STUDY_DIR=${OPTCLIM_STUDY_DIR}  >> rose-suite.conf
     echo OPTCLIM_RUNDIR=${OPTCLIM_STUDYDIR}/${OPTCLIM_RUN}  >> rose-suite.conf
     echo OPTCLIM_RUN=${OPTCLIM_RUN}  >> rose-suite.conf

     echo in new suite $new_suite made following differences:
     diff orig-rose-suite.conf rose-suite.conf 

     echo rose suite-run --no-gcontrol

     cd /home/$USER/roses
done
