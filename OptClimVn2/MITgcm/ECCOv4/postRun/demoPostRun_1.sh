#!/bin/bash

#
# -- This command accepts a filename as the first positional argument
# --- Otherwise it will try to use STDOUT.0000 as the filename
#

###########################################
# Script to check ECCOv4-r4 runs for eCSE #
###########################################

# if first argument empty, use default filename
if test -z "$1" 
then
    echo "Using default filename STDOUT.0000"
    filename=STDOUT.0000
else
    filename=$1
fi

# check the last line of standard output
lastline=$(tail -1 $filename)
lastline_ok='PROGRAM MAIN: Execution ended Normally'
if [[ "$lastline" == "$lastline_ok" ]]; then
    echo model_status="MITgcm (ECCOv4-r4) execution ended normally"
else
    echo "WARNING: MITgcm may not have ended normally, check STDOUT"
fi
echo " "
# min temperature values
echo "Global minimum potential temperature (deg C)" 
grep _theta_min $filename | tail -1 | cut -c 58-80

# mean temperature values
echo "-----"
echo "Global mean potential temperature (deg C)" 
grep dynstat_theta_mean $filename | tail -1 | cut -c 58-80
echo "-----" 

# max temperature values
echo "-----"
echo "Global maximum potential temperature (deg C)" 
grep _theta_max $filename | tail -1| cut -c 58-80
echo "-----" 

# min salinity values
echo "-----"
echo "Global minimum salinity (psu)" 
grep _salt_min $filename | tail -1| cut -c 58-80
echo "-----" 

# mean salinity values
echo "-----"
echo "Global mean salinity (psu)" 
grep dynstat_salt_mean $filename| tail -1 | cut -c 58-80
echo "-----" 

# max salinity values
echo "-----"
echo "Global maximum salinity (psu)" 
grep _salt_max $filename | tail -1| cut -c 58-80
echo "-----" 

# global mean sea ice area
echo "-----"
echo "Global mean sea ice area (m^2/m^2)" 
grep seaice_area_mean $filename | tail -1| cut -c 57-90
echo "-----" 

echo "--__--__--__--__--__--__--__--__--__--__--__--__--__--"
