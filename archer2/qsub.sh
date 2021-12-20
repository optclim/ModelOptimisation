#!/usr/bin/env bash

    # 4 node system: SHORT RUN under 20 mins
#SBATCH --partition=serial
#SBATCH --qos=serial
#SBATCH --time=00:20:0 --nodes=1 
#SBATCH --mem=4G

     #full archer2
     # want serial queue or maybe data analysis queue if want small scale parallel... or short queue

# prefer not to use this unless we have to!
#SBATCH --export=ALL 

# use this to test, as its passed from config.sh

#SBATCH --account=n02-optclim


# script to be run by qsub to run next iteration.
# args are command and its arguments
# this only necessary as environment needs to be setup..
echo "I am qsub called with $*"
cmd=$1; shift
cmdargs=$*
echo "Current Dir  is $PWD"
echo "PythonPath is $PYTHONPATH"
echo "Path is $PATH"
echo "Command is $cmd with $cmdargs"
echo "========================"
stat=$($cmd $cmdargs)
echo "stat is $stat"
