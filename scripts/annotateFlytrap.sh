#! /bin/bash
set -eu

# Globals

datadir=data
outputdir=output





cd ../



# The S1A serine proteases
echo "ANF Receptor calculations:" | tee ${outputdir}/PF01094_annotate.log
annotateMSA \
  -i ${datadir}/PF01094.an \
  -o ${datadir}/PF01094_full.an \
  -p C:/Users/twili/Desktop/pfamseq.txt 2>&1 | tee -a ${outputdir}/PF01094_annotate.log
