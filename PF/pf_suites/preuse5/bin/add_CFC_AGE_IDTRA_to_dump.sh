# *****************************COPYRIGHT******************************
#
# Description: This is a script to add and/or set all CFC dump variables to zero.
#              Should be needed for CMIP runs and should make things much easier 
#              than doing all this by hand.
#
#              Includes validation to ensure that all necessary input env vars 
#              are defined and that input files actually exist.
#              Also check return codes from ncks and other operations with 
#              a potential risk of failure. 
#
# Required environment:
#    INIT_SRC - Source file for fields to be initialised
# 
#===============================================

## file to modify caract:
in_file=$(eval echo $(grep "TOP_TO_INIT" $CYLC_SUITE_RUN_DIR/app/ocean_passive_tracers/rose-app.conf | cut -d= -f2))
out_file=$(eval echo $(grep "TOP_START" $CYLC_SUITE_RUN_DIR/app/ocean_passive_tracers/rose-app.conf | cut -d= -f2))

#
# Check all the necessary input and output file names are actually set
#
if [ -z $in_file ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: in_file is not set." 1>&2
   exit 1
fi

if [ -z $INIT_SRC ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: INIT_SRC is not set." 1>&2
   exit 1
fi

if [ -z $out_file ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: out_file is not set." 1>&2
   exit 1
fi

#
# Check all the necessary input files exist!
#
if [ ! -f $in_file ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: in_file: $in_file not found." 1>&2
   exit 1
fi

if [ ! -f $INIT_SRC ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: INIT_SRC: $INIT_SRC not found." 1>&2
   exit 1
fi

if [ -f $out_file ] ; then
   # Remove any tmp files left
   rm -rf ${out_file}*.ncks.tmp

   # Save any existing out_file
   save_file=${out_file}_SAVE

   if [ ! -f $save_file ] ; then
       mv $out_file $save_file
   else
       rm -rf $out_file
   fi
fi

#
# Copy input to output file before attempting to append extra fields.
#
cp $in_file $out_file
rc=$?
if [ $rc -gt 0 ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: Copy of input dump failed." 1>&2
   exit $rc
fi

chmod +w $out_file

# Modify output file.
#
# Add CFC fields
ncks -v  sbc_CFC11_b,sbc_CFC12_b,sbc_SF6_b,TRNCFC11,TRNCFC12,TRNSF6,TRBCFC11,TRBCFC12,TRBSF6,qint_CFC11,qint_CFC12,qint_SF6 -A $INIT_SRC $out_file
rc=$?
if [ $rc -gt 0 ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: nkcs failed to add CFC fields." 1>&2
   exit $rc
fi

# Add AGE fields
ncks -v sbc_Age_b,TRNAge,TRBAge -A $INIT_SRC $out_file
rc=$?
if [ $rc -gt 0 ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: nkcs failed to add AGE fields." 1>&2
   exit $rc
fi

# Add IDTRA fields
ncks -v sbc_IDTRA_b,TRNIDTRA,TRBIDTRA,qint_IDTRA -A $INIT_SRC $out_file
rc=$?
if [ $rc -gt 0 ]; then
   echo "[FAIL] add_CFC_AGE_IDTRA_to_dump: nkcs failed to add IDTRA fields." 1>&2
   exit $rc
fi
