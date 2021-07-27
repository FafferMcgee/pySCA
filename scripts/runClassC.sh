#! /bin/bash
set -eu

# Globals

datadir=data
outputdir=output

cd ../

# The S1A serine proteases
echo "Class C GPCR calculations:" | tee ${outputdir}/ClassC_refseq_clustal.log
echo "Begin scaProcessMSA:"
scaProcessMSA \
  -a ${datadir}/ClassC_refseq_clustal.an \
  -b ${datadir} \
  -s 7DTV \
  -c A \
  -f 'Homo sapiens' \
  -d ${outputdir} \
  -p 0.8 0.5 0.2 0.8 \
  -t -n 2>&1 | tee -a ${outputdir}/ClassC_refseq_clustal.log
 echo "Begin scaCore:"
scaCore -i ${outputdir}/ClassC_refseq_clustal.db 2>&1 | \
  tee -a ${outputdir}/ClassC_refseq_clustal.log
scaSectorID -i ${outputdir}/ClassC_refseq_clustal.db 2>&1 | \
  tee -a ${outputdir}/ClassC_refseq_clustal.log
echo
