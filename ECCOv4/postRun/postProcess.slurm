#!/bin/bash
# this is a "post-run" job to extract simulated obs for one run.

#   SLURM directives assume short queue

    # 4 node system: SHORT RUN under 20 mins
#SBATCH --partition=standard
#SBATCH --qos=short
#SBATCH --reservation=shortqos
#SBATCH --time=00:20:0 --nodes=1 --tasks-per-node=128

     #full archer2
     # want serial queue or maybe data analysis queue if want small scale parallel... or short queue

# prefer not to use this unless we have to!
#SBATCH --export=ALL 

# use this to test, as its passed from config.sh

#SBATCH --account=n02-optclim

module list

# takes 2 arguments
# dirListFile -- file containing the directories to process
# jsonFile -- the filename of the JSON configuration file.
echo "Args are $*"
for var in "$@" ; do
    echo ">>>$var<<<"
done
DirListFile=$1  # file containing list of directories.
JsonFile=$2  # json file
echo "DirListFile is $DirListFile"
echo "JsonFile is $JsonFile"
JsonFile=$(realpath $JsonFile)
echo "going to post process using  $JsonFile in $PWD"
echo pwd=$PWD

# its one of an array of jobs.... find which one... allow for Eddie or Archer2 in this bit!
# but note the #SBATCH is comment on Eddie.
# Portability is secondary for models that run on Archer2!

if [[ ${SGE_TASK_ID}"x" != "x" ]]
then
	mytask=$SGE_TASK_ID
elif [[ ${SLURM_ARRAY_TASK_ID}"x" != "x" ]]
then
	mytask=$SLURM_ARRAY_TASK_ID

else
	echo cant find task id
	exit 1
fi

echo "Array ID "$mytask
if [ $mytask > 0 ] ; then
    if [  ! -f $dirListFile ] ;  then
       pwd
       echo in wrong place?
       echo not found $dirListFile
       exit 1
    else # extract directory and name of output file.
       line=$(awk "NR==$mytask" $DirListFile)
       # now split line on , into dir, ppScript and PostProcessOutput
       dir=$(echo $line | cut -f1 -d",")
       PostProcessScript=$(echo $line | cut -f2 -d",")
       PostProcessOutput=$(echo $line | cut -f3 -d",")
       echo $line
       cd $dir
       echo "going to run $PostProcessScript $JsonFile $PostProcessOutput in $PWD"
       $PostProcessScript $JsonFile $PostProcessOutput
  fi
fi


