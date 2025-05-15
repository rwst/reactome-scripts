from pathlib import Path
import json
import os
import csv
import sys

# Step 1: Read JSON data from "archived.txt"
try:
    with open('archived.txt', 'r') as f:
        archived_data = json.load(f)
except FileNotFoundError:
    print("Error: 'archived.txt' not found.", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError:
    print("Error: 'archived.txt' contains invalid JSON.", file=sys.stderr)
    sys.exit(1)

# Step 2: Create a map named 'titles' from "PubMed" to "title"
titles = {}
for item in archived_data:
    if 'details' in item and 'title' in item['details'] and 'externalIds' in item['details'] and 'PubMed' in item['details']['externalIds'] :
        titles[item['details']['externalIds']['PubMed']] = item['details']['title']

# Step 3: Get all files in the directory ending with ".json"
json_files = Path('.').glob('*.json')

# Prepare CSV writer to write to stdout
writer = csv.writer(sys.stdout)

# Step 5: Process each JSON file and write to CSV
for file in json_files:
    # Read the JSON data named "pdfdata"
    try:
        with open(file, 'r') as f:
            pdfdata = json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Skipping {file} due to invalid JSON.", file=sys.stderr)
        continue

    # Get the basename of the file
    PMID = file.stem

    # Step 4: Get the title from the 'titles' map using the "DOI" field
    title = titles.get(PMID, 'Unknown') if PMID else 'Unknown'

    # Join all strings from "CellLines" and "ViralStrains" with \n
    cell_lines = '\n'.join(pdfdata.get('CellLines', []))
    viral_strains = '\n'.join(pdfdata.get('ViralStrains', []))

    # Write the CSV row to stdout
    writer.writerow([PMID, title, cell_lines, viral_strains])
