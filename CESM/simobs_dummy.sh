#!/bin/bash
echo "--"
echo dummy  for crude initial test of CESM-OptClim.
echo workign directory is now:
pwd

if [[ -f user_nl_cam.tst && -f user_nl_docn.tst ]]
then
 cat user_nl_cam.tst user_nl_docn.tst >observations.csv
 else
	 echo not seeingn expected files
	 exit 1
 fi
