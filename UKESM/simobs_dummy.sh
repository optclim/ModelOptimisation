#!/bin/bash
echo "------------------------------------------------------"
echo in simobs_dummy.sh for crude initial test of UKESM-OptClim workflow
echo workign directory is now:
pwd

# just rename the run's paramters to be simulated observables

cp runParams.json observations.json
sed -i -e "s/iau_nontrop_max_p/iau_nontrop_max_p_tst/" observations.json
sed -i -e "s/diagcloud_qn_compregimelimit/diagcloud_qn_compregimelimit_tst/" observations.json

