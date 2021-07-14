#! /bin/bash
set -eu

# Globals

datadir=data
outputdir=output





cd ../



# The S1A serine proteases
echo "ANF Receptor calculations:" | tee ${outputdir}/PF01094_full.log
scaProcessMSA \
  -a ${datadir}/PF01094_full.an \
  -b ${datadir} \
  -r ${datadir}/CaSR_reference.an \
  -i 0 \
  -d ${outputdir} \
  -t -n 2>&1 | tee -a ${outputdir}/PF01094_full.log
scaCore -i ${outputdir}/PF01094_full.db 2>&1 | \
  tee -a ${outputdir}/PF01094_full.log
scaSectorID -i ${outputdir}/PF01094_full.db 2>&1 | \
  tee -a ${outputdir}/PF01094_full.log
echo
