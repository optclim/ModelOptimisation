#!/bin/bash
# launch new suites
# called in short term from pumatest cylc that gets requests for new OPtCLim runs.
# will then become with new PUMA, an ssh call

 OPTCLIM_STUDY_DIR=$1
 shift
 OPTCLIM_BASE_SUITE=$1
 shift

 optclim_study=$(basename ${OPTCLIM_STUDY_DIR})
 echo $0: $OPTCLIM_STUDY_DIR  $OPTCLIM_BASE_SUITE
while (($#)) ; do

   #...
     ARUN=$1
     shift
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
     sed -i -e "s/yyyy/${ARUN}/g" rose-suite.conf
     sed -i  -e "s/wwww/${optclim_study}/g"  rose-suite.conf

     echo in new suite $new_suite made following differences:
     diff orig-rose-suite.conf rose-suite.conf 

     rose suite-run --no-gcontrol

     cd /home/$USER/roses
done
