#!/usr/bin/env ksh
#
# Description: This script is used to extract any lines featuring a   
#              key phrase from a suite cycle's standard output log 
#              file and email the suite owner with details of the 
#              relevant lines IFF any are selected. 
#
#              Its purpose is to highlight any anomalies produced by NEMO 
#              during a run. Detection of these anomalous conditions will 
#              not result in the run being terminated or otherwise 
#              interfered with (although other internal mechanisms
#              within the model components may do so, depending on the 
#              perceived severity of the anomaly). 
#
#              Key to the operation of this script is that all relevant 
#              NEMO anomaly messages must feature the text contained in 
#              the variable search_string1 AND that one line associated with 
#              each highlighted condition should feature the text contained 
#              in search_string2.
#              ("kt" is initially chosen on the basis that this is
#              the NEMO timestep counter and therefore likely to be
#              output in all conditions of interest. i.e. there's little
#              point identifying an anomlay without knowing when it occurred.)  
#
#              Although aimed at coupled models, we cater for the possibility 
#              of standalone nemo and nemo_cice models too. 
#
#              One of the biggest issues is that the log files do not return 
#              to the desktop instantly after a model run so we have 
#              contrived a method to try to ensure that we do not interrogate 
#              a log file until it is wholly available. 
#
#              If the log file does not appear after 20 attempts to read it
#              (currently allowing a total of 3.5 minutes) then the process will
#              move on. i.e. it will not wait indefinitely.  
#
# Modification History:
#              Updated description and in-line comments to improve clarity
#              of purpose, method and limitations. R. Hill 14/06/2018. 
######################################################################################
export search_string1=':tracer anomaly:'
export search_string2='kt'
typeset -i anom_count=0
export anom_file="anom_message_$CYLC_TASK_CYCLE_POINT"

# Set up a list of possible model types to see where we may need 
# to interrogate our job output file. 
typeset -A subdir 
subdir[0]="nemo_cice" 
subdir[1]="nemo" 
subdir[2]="coupled" 

typeset -i subarr_size=3
 
# See which one of these locations actually exists
for((i=0;i<$subarr_size;i++)); do
   export subfile=$CYLC_SUITE_LOG_DIR/../job/$CYLC_TASK_CYCLE_POINT/"${subdir[$i]}"

   if [[ -d "$subfile" ]] ; then
      # If this directory exists
      export logfile=$subfile/NN/job.out
      break
   fi
done

# We need to do a grep on the log file, but we don't know if it's 
# available yet! There's no point trying if the file has not been
# completely written. (Just applying an arbitrary wait time
# and hoping for the best is too slack.) 
# So we loop until a file exists then carry on looping until its 
# size appears to be stable at which point we conclude that it
# has been completely written.  

typeset -i filesize_prev=0
typeset -i filesize=1
# Only test 20 times then give up. 
for((i=1;i<=20;i++)); do

   # Increase sleep time the longer it takes. 
   if [[ -e "$logfile" ]] ; then
       filesize=$(stat -c %s $logfile)
       echo "file size is $filesize v $filesize_prev"
       if (($filesize == $filesize_prev)); then
           echo "file OK, exit"
           break
       else 
           echo "file still building"
           filesize_prev=$filesize
           sleep $i
       fi
   else
       sleep $i
   fi

done   

grep -i "$search_string1" $logfile > $anom_file
anom_count=$(grep -i "$search_string1" $anom_file | grep -c "$search_string2" )

if (( $anom_count > 0 )) ; then
       echo "A total of $anom_count tracer anomalies were found" >> $anom_file
       echo "in cycle $CYLC_TASK_CYCLE_POINT of suite $CYLC_SUITE_NAME " >> $anom_file
       mail -s "Tracer anomalies detected in cycle $CYLC_TASK_CYCLE_POINT of $CYLC_SUITE_NAME" $USER <$anom_file
fi
return
