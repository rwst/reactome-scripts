from neo4j import GraphDatabase
import logging
import sys
import csv
import argparse

# Initiate the parser
parser = argparse.ArgumentParser()
parser.add_argument("-P", "--pathway", nargs=1, help="reactome ID no of pathway")
parser.add_argument("-l", "--login", nargs=1, help="neo4j login credential")
parser.add_argument("-p", "--password", nargs=1, help="no4j passwd credential")

# Read arguments from the command line
args = parser.parse_args()



#handler = logging.StreamHandler(sys.stdout)
#handler.setLevel(logging.DEBUG)
#logging.getLogger("neo4j").addHandler(handler)
#logging.getLogger("neo4j").setLevel(logging.DEBUG)

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=(args.login, args.password))
driver.verify_connectivity()

with driver.session() as session:
    result = session.run("""
MATCH (p:Pathway{stId:"R-HSA-{}"})-[:hasEvent*]->(rle:ReactionLikeEvent)-[:summation]->(sum:Summation)
MATCH (rle)-[:literatureReference*]->(lit:LiteratureReference)
RETURN rle.stId AS Reaction, rle.displayName AS ReactionName, collect(lit.pubMedIdentifier) as PMID, sum.text as Summation       """.format(args.pathway))
    data = [(record["Reaction"], record["ReactionName"], record["Summation"], record["PMID"]) for record in result]
    flat = []
    for r, n, s, pmids in data:
        l = ["https://pubmed.ncbi.nlm.nih.gov/" + str(p) for p in pmids]
        flat.append((r, n, s, *l))

    with open('output.tsv', 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        for row in flat:
            writer.writerow(row)

