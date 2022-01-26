#!/bin/bash

# dummy for the task that is invoked from CYlc polling
# finds the directory of runs that need to be started. 
STUDY_DIR=$1

find $STUDYDIR  -name "Q" -maxdepth 2 | head -1
