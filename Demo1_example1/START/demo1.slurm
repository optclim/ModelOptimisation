#!/bin/bash

#SBATCH --account=ecsead07

    # SHORT RUN under 20 mins
#SBATCH --partition=standard
#SBATCH --qos=short
#SBATCH --reservation=shortqos

#SBATCH --export=none

#SBATCH  --time=0:02:0 
#SBATCH --nodes=1 
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1

sleep 5
/bin/env 
