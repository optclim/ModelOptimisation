#. ./case_setup
echo "in $0" 
echo " "
scriptdir=$(dirname $0)
myrun=$(basename $scriptdir)
echo sbatch --job-name=M_$myrun   --chdir=${scriptdir} $scriptdir/run_srun.slurm
sbatch --job-name=M_$myrun   --chdir=${scriptdir} ${scriptdir}/run_srun.slurm
