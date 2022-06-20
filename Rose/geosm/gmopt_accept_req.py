#!/usr/bin/env python
#
# Copyright (c) The University of Edinburgh, 2014.
#
from geosmeta import GeosMETA
from geosmeta import util
import argparse
import json
import sys
import os
import subprocess

def get_requests(args):

    projectName = args.projectName
    study = args.study
      
    query = '"gmdata.optclim_rose_type":"suiteRequest","gmdata.optclim_status":"NEW","gmdata.study":"%s"'%study
   
    gm = GeosMETA(configFilePath=args.config_file)
 
    resultJSON = gm.findActivities("A",projectName, query, None)

#    print((json.dumps(resultJSON,
                                #indent=2,
                                #sort_keys=True)))

    #print("\n no. docs: %d\n"%(len(resultJSON['_items'])))

     # to do maybe should return tuples, if we think of pumatest as a server of model clones.
     # need a quick test for now!
    runlist = []
    for itm in resultJSON['_items']:
        #print(itm['_id'])
        runlist.append((itm['gmdata']['studydir'],
                       itm['gmdata']['basesuite'], itm['gmdata']['runname'] ))
        activityEtag = itm['_etag']
        result = gm.updateActivity(itm['_id'],activityEtag,"gmdata.optclim_status", "CLONING")
    return (runlist)

if __name__ == '__main__':
        # Get command line arguments
    parser = argparse.ArgumentParser(description="Find gmDocs given a user's query")
    parser.add_argument('--projectName',
                        '-p',
                        required=False,
                        help='Name of the project (required if not in cfg file)')
    parser.add_argument('--config-file','-C',metavar='FILE',help="read configuration from FILE: default:~/.geosmeta/geosmeta.cfg")
    parser.add_argument('--nDryrun','-n', default=False, action=argparse.BooleanOptionalAction, help="set to make no change to datasbase")
    parser.add_argument('--study',
                        '-s',
                        required=True,
                        default=None,
                        help='study name')

    args = parser.parse_args()

    runlist = get_requests(args)

    myscript="/home/mjm/dev/ModelOptimisation/Rose/onPUMA/launchRuns.sh "
    for (req_sd, req_bs, req_run) in runlist:
    
        cmd = "%s %s %s %s"%(myscript, req_sd, req_bs, req_run)
        if args.nDryrun:
              print ("dryrun for %s"%cmd)
        else:
           print("running: %s\n"%cmd)
           rtn=subprocess.check_output(cmd, shell=True)
           print (rtn)

    if len(runlist)==0:
       print ("no runs to clone")
    

