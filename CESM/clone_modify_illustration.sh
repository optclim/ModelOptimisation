#!/bin/bash
#$ -l h_vmem=8G
#$ -l h_rt=00:60:00
#$ -cwd

# do need to rerun the build so best to be in a worker node
# for Eddie as more memory is needed and its heavy for a login node on Eddie
# if Eddie . /etc/profile.d/modules.sh

#if archer, on login node?
# need to move setup script or do ssh... so ~/.cime is visible
# or find way to have hte config files eslewhere.

. ~/.cime/setup_for_cesm

NEWCASEDIR=$1
OLDCASEDIR=$2

casename=$(basename $NEWCASEDIR)

$CIMEROOT/scripts/create_clone --case ${casename} --clone ${OLDCASEDIR} --keepexe

# include a dummy namelist amendments

cd $casename

cat << EOT >> user_nl_cam
dust_emis_fact         = 0.60D0
EOT
# and dummy run control?

./case.setup --reset
./preview_run 

./case.build  # quick in view of the clone.
./case.submit 


