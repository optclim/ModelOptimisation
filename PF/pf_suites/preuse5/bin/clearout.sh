# Clearout any old data left over from a previous run.

set -u

rm $DATAM/${RUNID}a*
rm $DATAM/${RUNID}.apstmp1
rm $DATAM/${RUNID}.apsum1
rm $DATAM/${RUNID}.xhist
rm $NEMO_DATA/${RUNID}o*
rm $NEMO_DATA/namelist
rm $CICE_DATA/${RUNID}i*
rm $CICE_DATA/ice.restart_file
rm -r $ROSE_SUITE_DIR/work/*/coupled
rm -r $CYLC_SUITE_SHARE_DIR/data/Nrun_Data/*

# If anything fails then that is still OK so therefore exit with code zero
exit 0
