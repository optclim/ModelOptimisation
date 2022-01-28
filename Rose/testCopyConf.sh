
# a script I want to invoke from Cylc/Rose task

echo found target script
echo study dir $OPTCLIM_STUDY_DIR
echo rundir $OPTCLIM_RUNDIR
echo run $OPTCLIM_RUN

echo cp $OPTCLIM_STUDY_DIR/$OPTCLIM_RUN/rose-app.conf $ROSE_SUITE_DIR/app/um
cp $OPTCLIM_STUDY_DIR/$OPTCLIM_RUN/conf/app/um/rose-app.conf $ROSE_SUITE_DIR/app/um

grep compregime $ROSE_SUITE_DIR/app/um/rose-app.conf

# change state 
echo needs fix? /work/n02/shared/mjmn02/OptClim/optclim3/ModelOptimisation/Rose/getOptClimRun.py  $OPTCLIM_STUDY_DIR/$OPTCLIM_RUN -c RUNNING

