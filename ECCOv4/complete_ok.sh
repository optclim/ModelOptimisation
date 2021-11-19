#!/bin/bash

# Script to check ECCOv4-r4 runs for eCSE #
###########################################
filename=STDOUT.0000

# check the last line of standard output
lastline=$(tail -1 $filename)
lastline_ok='PROGRAM MAIN: Execution ended Normally'
if [[ "$lastline" == "$lastline_ok" ]]; then
    echo model_status="MITgcm (ECCOv4-r4) execution ended normally"
    exit 0
else
    echo "WARNING: MITgcm may not have ended normally, check STDOUT"
    exit 1
fi
