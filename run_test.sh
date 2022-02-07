#!/usr/bin/bash

export OPTCLIMTOP=$(realpath $(dirname $0))
export PYTHONPATH=$OPTCLIMTOP/:$OPTCLIMTOP/OptClimVn2:$OPTCLIMTOP/tools/optFunctions

WORK_DIR=$(mktemp -p /tmp -d optclim_XXXX)

python tools/runAlgorithm.py --restart  --test -d $WORK_DIR Configurations/dfols14param.json

echo workdir $WORK_DIR
