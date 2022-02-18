#!/usr/bin/env python
#
# Copyright (c) The University of Edinburgh, 2014.
#
from geosmeta import GeosMETA
import argparse
import sys
import json


def addTheDoc(project_id,configFile, metaFields):
    """
    Function to add either a jsonfile or a python dictionary as 
    a new gmDoc
    :param project_id: Can be None unless passed in from command line argument
    :param configFile: can be None unless passed in
    :param metaFields: either a python dictionary or a jsonfile
    """

    gm = GeosMETA(configFilePath=configFile)
    try:
            result = gm.addDoc(project_id, metaFields)
    except Exception as err:
            sys.stderr.write('Error creating gmDoc:\n')
            sys.stderr.write('%s\n' % str(err))
            raise #        sys.exit(1)

    else:
          return result
    



def do_create(args):
   adict = {}
   adict['optclim_rose_type'] = 'suiteRequest'
   adict['study'] = args.study
   adict['studydir'] = args.Dirstudy
   adict['basesuite'] = args.basesuite
   adict['optclim_status'] = 'NEW'
   project_id = None # usually from ~/geosmeta.cfg
   configFile = None # usually from ~/geosmeta.cfg
   if args.project:
      project_id = args.project 
   if args.configfile:
      configFile = args.configfile 

   for arun in args.runlist.split(' '):
      adict['runname'] = arun
      addTheDoc(project_id,configFile, adict)
    

if __name__ == '__main__':
    # Get command line arguments
    desc="""Uploads a gmDoc using the GeosMeta system - 
            """
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('--project',
                        '-p',
                        default=None,
                        required=False,
                        help='Name of the project (can be in cfg file)')

    parser.add_argument('--study',
                        '-s',
                        required=True,
                        default=None,
                        help='study name')

    parser.add_argument('--Dirstudy',
                        '-D',
                        required=True,
                        default=None,
                        help='study directory')

    parser.add_argument('--runlist',
                        '-r',
                        required=True,
                        default=None,
                        help='run name')

    parser.add_argument('--basesuite',
                        '-b',
                        required=True,
                        default=None,
                        help='suite to be cloned')

    parser.add_argument('--configfile',
                       '-C',
                       metavar='FILE',
         help="read configuration from FILE: default:~/.geosmeta/geosmeta.cfg")

    args = parser.parse_args()

    do_create(args)
