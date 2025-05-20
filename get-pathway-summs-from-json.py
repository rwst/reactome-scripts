import sys
import csv
import argparse
import json
import codecs

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--datafile", nargs=1, help="")

# Read arguments from the command line
args = parser.parse_args()


jol = json.load(codecs.open(args.datafile[0], 'r', 'utf-8-sig'))
data = [(record["Reaction"], record["ReactionName"], record["Summation"], record["PMID"]) for record in jol]
flat = []
for r, n, s, pmids in data:
    l = ["https://pubmed.ncbi.nlm.nih.gov/" + str(p) for p in pmids]
    flat.append((r, n, s, *l))

with open('output.tsv', 'w', newline='') as tsvfile:
    writer = csv.writer(tsvfile, delimiter='\t')
    for row in flat:
        writer.writerow(row)

