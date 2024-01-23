from neo4j import GraphDatabase
import logging
import sys
import csv

#handler = logging.StreamHandler(sys.stdout)
#handler.setLevel(logging.DEBUG)
#logging.getLogger("neo4j").addHandler(handler)
#logging.getLogger("neo4j").setLevel(logging.DEBUG)

uri = "bolt://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "yvXgS9fArLPS8ym"))
driver.verify_connectivity()

with driver.session() as session:
    result = session.run("""
MATCH (p:Pathway{stId:"R-HSA-70268"})-[:hasEvent*]->(rle:ReactionLikeEvent)-[:summation]->(sum:Summation)
MATCH (rle)-[:literatureReference*]->(lit:LiteratureReference)
RETURN rle.stId AS Reaction, rle.displayName AS ReactionName, collect(lit.pubMedIdentifier) as PMID, sum.text as Summation       """)
    data = [(record["Reaction"], record["ReactionName"], record["Summation"], record["PMID"]) for record in result]
    flat = []
    for r, n, s, pmids in data:
        l = ["https://pubmed.ncbi.nlm.nih.gov/" + str(p) for p in pmids]
        flat.append((r, n, s, *l))

    with open('output.tsv', 'w', newline='') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        for row in flat:
            writer.writerow(row)

