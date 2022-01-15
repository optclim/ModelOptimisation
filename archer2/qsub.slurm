#!/usr/bin/env bash

#SBATCH --partition=serial
#SBATCH --qos=serial
#SBATCH --time=00:20:0 --nodes=1 
#SBATCH --mem=4G

# for now using serial queue. Future, maybe data analysis queue 
# if want small scale parallel... or short queue

# About to  exportign the environment of the call to sbatch
# prefer not to use this unless we have to!
# maybe pass PYTHONPATH and PATH explicitly in future....
# Fear is the context is ill defined and so not reproducible with export all.

#SBATCH --export=ALL 

# remove? # use this to test, as its passed from config.sh:
# remove? # comment out otherwise
# remove? #SBATCH --account=n02-optclim


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
