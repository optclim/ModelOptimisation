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

def get_requests(args):

    projectName = args.projectName
    study = os.environ("OPTCLIM_STUDY")
    studyDir = os.environ("OPTCLIM_STUDY_DIR")
      
    query = '{"gmdata.study":study,"gmdata.optclim_rose_type":"suiteRequest","gmdata.optclim_status":"NEW"}'
   
    gm = GeosMETA(configFilePath=args.config_file)
 
    resultJSON = gm.findActivities("A",projectName, query, adict)

    print((json.dumps(resultJSON,
                                indent=2,
                                sort_keys=True)))

    print("\n no. docs: %d\n"%(len(resultJSON['_items'])))
                for itm in resultJSON['_items']:
                   print(itm['_id'])

if __name__ == '__main__':
        # Get command line arguments
    parser = argparse.ArgumentParser(description="Find gmDocs given a user's query")
    parser.add_argument('--projectName',
                        '-p',
                        required=False,
                        help='Name of the project (required if not in cfg file)')
    parser.add_argument('--config-file','-C',metavar='FILE',help="read configuration from FILE: default:~/.geosmeta/geosmeta.cfg")
    #parser.add_argument('--study',
                        #'-s',
                        #required=True,
                        #default=None,
                        #help='study name')

    args = parser.parse_args()

    res = get_requests(args)
    print (res)

