#! /bin/bash
set -eu

# Globals

datadir=data
outputdir=output

cd ../

# The S1A serine proteases
echo "Calcium-sensing receptor calculations:" | tee ${outputdir}/CaSR_orthologs.log
echo "Begin scaProcessMSA:"
scaProcessMSA \
  -a ${datadir}/CaSR_orthologs.an \
  -b ${datadir} \
  -i 0 \
  -d ${outputdir} \
  -f 'Homo sapiens' \
  -p 0.5 0.5 0.5 0.8 \
  -t -n 2>&1 | tee -a ${outputdir}/CaSR_orthologs.log
 echo "Begin scaCore:"
scaCore -i ${outputdir}/CaSR_orthologs.db 2>&1 | \
  tee -a ${outputdir}/CaSR_orthologs.log
#scaSectorID -i ${outputdir}/CaSR_orthologs.db 2>&1 | \
#  tee -a ${outputdir}/CaSR_orthologs.log
#echo
