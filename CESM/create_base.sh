if [[ ${CIMEROOT}"x" == "x" ]]
then
	. ~/.cime/lite_setup_for_cesm
fi

if [ "$#" == "0" ]; then
	echo give name of case -will be  in your cwd
	exit 1
else
	${CIMEROOT}/scripts/create_newcase \
	       	--case $1 --compset F2000climo --res f19_f19_mg17  \
		--output-root $PWD --queue=short \
                 --workflow optclim1 --walltime 00:20:00 --project n02-optclim
fi

# ./case.setup --reset # reset is not essential for first run of this.

# ./case.build   # takes 2-3 minutes and should conclude with something like 

               # MODEL BUILD HAS FINISHED SUCCESSFULLY
#./case.submit

cd $1

./xmlchange STOP_N=2
./xmlchange RESUBMIT=3
./xmlchange DOUT_S=FALSE

./xmlquery CONTINUE_RUN

./case.setup # --reset

./preview_run
./case.build
