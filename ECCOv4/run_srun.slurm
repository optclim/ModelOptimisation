#!/bin/bash
# Slurm job options (job-name, compute nodes, job time)
# are set outside this script to allow easy changes and testing.


#SBATCH --cpus-per-task=1

# Replace [budget code] below with your project code (e.g. t01)

# SBATCH --account=ecseab06-guest 

    # SHORT RUN under 20 mins
#SBATCH --partition=standard
#SBATCH --qos=short
#SBATCH --account=n02-optclim --time=00:20:0 --nodes=1 --tasks-per-node=96 

#SBATCH --export=none

    # remove space to uncomment long run options
# SBATCH --qos=standard


# Setup the job environment (this module needs to be loaded before any other modules)

OPTCLIM_ECCO=/work/n02/shared/mjmn02/OptClim/optclim3/ModelOptimisation/ECCOv4
. ./case_setup
#. $OPTCLIM_ECCO/case_setup
module list
ftn --version

# Set the number of threads to 1

#   This prevents any threaded system libraries from automatically 
#   using threading.

export OMP_NUM_THREADS=1



# Launch the parallel job

#   srun picks up the distribution from the sbatch options

srun --distribution=block:block --hint=nomultithread ./mitgcmuv

# check if job completed ok....
# not including continuation here - trap timeout or need for another run as in PAS??
# for ECCO, simple one job per  run is enough.


$OPTCLIM_ECCO/complete_ok.sh 
 retVal=$?
 if [  $retVal -eq 0 ]; then
	 bash ./optclim_finished   # releases the array job corresponding to this run.
	else
    echo test complete_ok is indeed ok
fi

