#!/bin/bash

###########################################
# Run at end of a model to extract 3 simulated observables from STDOUT.0000
# A very artificial example - usually an analysis of data woul dbe done - this
# is just a simple way to generate numbers
# config.py sets up an array of jobs one per model instance.
# $OPTCLIMTOP/archer2/postProcess.slurm is the slurm script for that array.
# within it the arguments for the script in this file are picked out:
# arg1: the json file for the study - not used in this example.
# arg2: the output file into which simulated observations are to be written.
###########################################

filename=STDOUT.0000

if test -z "$1" 
then
	echo "not got arg1 in $0"
    exit  1
else
    echo "For this test, ignoring JSON  filename " $1
fi

if test -z "$2" 
then
	echo "not got arg2 in $0"
    exit  1
else
    fileout=$2
fi

echo "{" > $fileout
#echo "    \"simobs\": {" >> $fileout

# check the last line of standard output
lastline=$(tail -1 $filename)
lastline_ok='PROGRAM MAIN: Execution ended Normally'
if [[ "$lastline" == "$lastline_ok" ]]; then
    echo model_status="MITgcm (ECCOv4-r4) execution ended normally"
else
    echo "WARNING: MITgcm may not have ended normally, check STDOUT"
fi
echo " "

# mean temperature values
echo "-----"
echo "Global mean potential temperature (deg C)" 
d_t_m=$(grep dynstat_theta_mean $filename | tail -1 | cut -c 58-80)
echo "        \"dynstat_theta_mean\": $d_t_m," >>$fileout
echo "-----" 

# mean salinity values
echo "-----"
echo "Global mean salinity (psu)" 
d_sm=$(grep dynstat_salt_mean $filename| tail -1 | cut -c 58-80)
echo "        \"dynstat_salt_mean\": $d_sm," >>$fileout
echo "-----" 

# global mean sea ice area
echo "-----"
echo "Global mean sea ice area (m^2/m^2)" 
d_im=$(grep seaice_area_mean $filename | tail -1| cut -c 57-90)
echo "        \"seaice_area_mean\": $d_im" >>$fileout

#echo "    } " >> $fileout
echo "}" >> $fileout
echo "--__--__--__--__--__--__--__--__--__--__--__--__--__--"
