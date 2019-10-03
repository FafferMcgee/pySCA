#! /usr/bin/env python3
"""
The annotateMSA script provides utilities to automatically annotate sequence
headers (for a fasta file) with taxonomic information. Currently this can be
done in one of two ways:

    1) For PFAM alignments, annotations can be extracted from the file
       pfamseq.txt (please download from:
       ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/database_files/pfamseq.txt.gz)

    2) For Blast alignments, annotations can be added using the NCBI Entrez
       utilities provided by BioPython. In this case, an additional command
       line argument (--giList, see below) should specify a list of gi numbers.
       These numbers are then used to query NCBI for taxonomy information (note
       that this approach requires a network connection).

To quickly extract gi numbers from a list of headers (variable name 'hd') with
typical Blast alignment formatting, the following line of python code is
useful:

>>> gis = [h.split('_')[1] for h in hd]

Alternatively, the script alnParseGI.py will accomplish this. For both the PFAM
and NCBI utilities, the process of sequence annotation *can be slow* (on the
order of hours, particularly for NCBI entrez with larger alignments). However,
the annotation process only needs to be run once per alignment.

**Arguments**
    Input_MSA.fasta (some input sequence alignment)

**Keyword Arguments**
    -o, --output        Specify an output file, Output_MSA.an
    -a, --annot         Annotation method. Options are 'pfam' or 'ncbi'.
                        Default: 'pfam'
    -g, --giList        This argument is necessary for the 'ncbi' method.
                        Specifies a file containing a list of gi numbers
                        corresponding to the sequence order in the alignment; a
                        gi number of "0" indicates that a gi number wasn't
                        assigned for a particular sequence.
    -p, --pfam_seq      Location of the pfamseq.txt file. Defaults to
                        path2pfamseq (specified at the top of scaTools.py)

**Examples**::

  ./annotateMSA.py ../data/PF00186_full.txt -o ../output/PF00186_full.an -a 'pfam'
  ./annotateMSA.py ../data/DHFR_PEPM3.fasta -o ../output/DHFR_PEPM3.an -a 'ncbi' -g ../data/DHFR_PEPM3.gis

:By: Rama Ranganathan, Kim Reynolds
:On: 9.22.2014

Copyright (C) 2015 Olivier Rivoire, Rama Ranganathan, Kimberly Reynolds

This program is free software distributed under the BSD 3-clause license,
please see the file LICENSE for details.
"""

import time
import sys
import argparse
import os
from Bio import Entrez
import scaTools as sca

import settings

Entrez.email = settings.entrezemail  # PLEASE use your email! (see settings.py)

if __name__ == '__main__':
    # parse inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("Input_MSA", help='input sequence alignment')
    parser.add_argument("-o", "--output", dest="output", default='sys.stdout',
                        help="Outputfile name. Default: sys.stdout")
    parser.add_argument("-a", "--annot", dest="annot", default='pfam',
                        help="Annotation method. Options are 'pfam' or 'ncbi'."
                             " Default: 'pfam'")
    parser.add_argument("-g", "--giList", dest="giList", default=None,
                        help="This argument is necessary for the 'ncbi' "
                             "method. Specifies a file containing a list of "
                             "gi numbers corresponding to the sequence order "
                             "in the alignment; a gi number of 0 indicates "
                             "that a gi number wasn't assigned for a "
                             "particular sequence.")
    parser.add_argument("-p", "--pfam_seq", dest="pfamseq", default=None,
                        help="Location of the pfamseq.txt file. Defaults to "
                             "path2pfamseq (specified in settings.py)")
    parser.add_argument("-d", "--pfam_db", dest="pfamdb", default=None,
                        help="Location of the pfamseq.db file. Priority over "
                             "pfamseq.txt file. Defaults to path2pfamseqdb "
                             "(specified in settings.py)")
    options = parser.parse_args()

    if (options.annot != 'pfam') & (options.annot != 'ncbi'):
        sys.exit("The option -a must be set to 'pfam' or 'ncbi' - other"
                 " keywords are not allowed.")

    if (options.annot == 'ncbi') & (options.giList is None):
        sys.exit("To use NCBI entrez annotation, you must specify a file "
                 "containing a list of gi numbers (see the --giList argument)")

    if options.annot == 'pfam':
        # Annotate a Pfam alignment
        if options.pfamdb is not None:  # default to db query over txt search
            sca.AnnotPfamDB(options.Input_MSA, options.output, options.pfamdb)
        elif options.pfamseq is not None:
            sca.AnnotPfam(options.Input_MSA, options.output, options.pfamseq)
        else:
            # If no database or text file supplied to annotateMSA, then default
            # to the files defined in settings.py.
            if os.path.exists(settings.path2pfamseqdb):
                sca.AnnotPfamDB(options.Input_MSA, options.output)
            elif os.path.exists(settings.path2pfamseq):
                sca.AnnotPfam(options.Input_MSA, options.output)
    else:
        # Annotate using GI numbers/NCBI entrez
        gi_lines = open(options.giList, 'r').readlines()
        gi = [int(k) for k in gi_lines]
        gi_blocks = [gi[x:x + 200] for x in range(0, len(gi), 200)]

        taxID = list()
        start = time.process_time()
        for i, k in enumerate(gi_blocks):
            taxonList = Entrez.read(Entrez.elink(dbfrom="protein",
                                                 db="taxonomy", id=k))
            for x, y in enumerate(taxonList):
                try:
                    taxID.append(taxonList[x]["LinkSetDb"][0]["Link"][0]["Id"])
                except BaseException as e:
                    print('Error: ' + str(e))
                    taxID.append('')
        end = time.process_time()
        print("Look up for Tax IDs complete. Time: %f" % (end - start))

        # Collect records with lineage information
        print("Collecting taxonomy information...")
        start = time.process_time()
        records = list()
        for i, k in enumerate(taxID):
            try:
                handle = Entrez.efetch(db="taxonomy", id=k, retmode="xml")
                temp_rec = Entrez.read(handle)
                handle.close()
                records.append(temp_rec[0])
                print("%s" % (temp_rec[0]['Lineage']))
                print("%s" % (temp_rec[0]['ScientificName']))
            except BaseException as e:
                print('Error: ' + str(e))
                records.append('')
        end = time.process_time()
        print("Look up for taxonomy information complete. Time: %f"
              % (end - start))

        # Write to the output fasta file.
        s_records = list()
        [hd, seqs] = sca.readAlg(options.Input_MSA)
        f = open(options.output, 'w')
        for i, k in enumerate(seqs):
            try:
                hdnew = hd[i] + '|' + records[i]['ScientificName'] + '|' + \
                    ','.join(records[i]['Lineage'].split(';'))
            except BaseException as e:
                print('Error: ' + str(e))
                hdnew = hd[i] + '| unknown '
                print("Unable to add taxonomy information for seq: %s" % hd[i])
            f.write('>%s\n' % hdnew)
            f.write('%s\n' % k)
        f.close()
