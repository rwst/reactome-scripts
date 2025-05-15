import xml.etree.ElementTree as ET
import csv
import sys

def extract_reactome_data(xml_filepath, csv_filepath):
    """
    Extracts pathway and reaction data from a Reactome XML file and writes it to a CSV.
    Reads DB_ID, text, and pubMedIdentifier from child <attribute> tags where appropriate.

    Args:
        xml_filepath (str): Path to the input XML file.
        csv_filepath (str): Path to the output CSV file.
    """
    try:
        tree = ET.parse(xml_filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return
    except FileNotFoundError:
        print(f"Error: XML file not found at {xml_filepath}")
        return

    reactome_node = root.find('reactome')
    if reactome_node is None:
        print("Error: <reactome> tag not found in XML.")
        return

    # Pre-cache Summation and LiteratureReference instances by DB_ID for quick lookup
    summations_by_id = {}
    summation_parent_node = reactome_node.find('Summation')
    if summation_parent_node is not None:
        for inst in summation_parent_node.findall('instance'):
            db_id_val = None
            text_val = None
            for child_attr in inst.findall('attribute'):
                if child_attr.get('name') == 'DB_ID':
                    db_id_val = child_attr.get('value')
                elif child_attr.get('name') == 'text':
                    text_val = child_attr.get('value')
            
            # If DB_ID wasn't found as a child attribute, try the instance attribute itself
            # (as it appears on <instance DB_ID="..."> for Summation/LiteratureRef)
            if not db_id_val:
                db_id_val = inst.get('DB_ID')

            if db_id_val:
                summations_by_id[db_id_val] = text_val if text_val is not None else ''

    literature_refs_by_id = {}
    literature_parent_node = reactome_node.find('LiteratureReference')
    if literature_parent_node is not None:
        for inst in literature_parent_node.findall('instance'):
            db_id_val = None
            pubmed_val = None
            for child_attr in inst.findall('attribute'):
                if child_attr.get('name') == 'DB_ID':
                    db_id_val = child_attr.get('value')
                elif child_attr.get('name') == 'pubMedIdentifier':
                    pubmed_val = child_attr.get('value')

            if not db_id_val:
                db_id_val = inst.get('DB_ID')
            
            if db_id_val:
                literature_refs_by_id[db_id_val] = pubmed_val if pubmed_val is not None else ''

    extracted_data = []

    # Process Pathways and Reactions
    for item_type_tag in ['Pathway', 'Reaction']:
        item_parent_node = reactome_node.find(item_type_tag)
        if item_parent_node is None:
            continue

        for instance_node in item_parent_node.findall('instance'):
            # For Pathway/Reaction, displayName is a direct attribute of the <instance> tag
            name = instance_node.get('displayName', '')
            
            summary_text = ""
            summation_ref_id = None
            # Find summation reference from child <attribute name="summation" referTo="...">
            for attr in instance_node.findall('attribute'):
                if attr.get('name') == 'summation':
                    summation_ref_id = attr.get('referTo')
                    break
            if summation_ref_id and summation_ref_id in summations_by_id:
                summary_text = summations_by_id[summation_ref_id]

            pubmed_ids = []
            # Find literature references from child <attribute name="literatureReference" referTo="...">
            for attr in instance_node.findall('attribute'):
                if attr.get('name') == 'literatureReference':
                    lit_ref_id = attr.get('referTo')
                    if lit_ref_id and lit_ref_id in literature_refs_by_id:
                        pmid = literature_refs_by_id[lit_ref_id]
                        if pmid:
                            pubmed_ids.append("https://pubmed.ncbi.nlm.nih.gov/{}/".format(pmid))
            
            current_row_pubmed_ids = pubmed_ids[:10]
            current_row_pubmed_ids.extend([''] * (10 - len(current_row_pubmed_ids)))
            
            extracted_data.append([name, summary_text] + current_row_pubmed_ids)

    # Write to CSV
    header = ['name', 'summaryText'] + [f'literaturePubmedIdentifier_{i+1}' for i in range(10)]
    
    try:
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(extracted_data)
        print(f"Data successfully extracted to {csv_filepath}")
    except IOError:
        print(f"Error: Could not write to CSV file at {csv_filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script_name.py <input_xml_file> <output_csv_file>")
        sys.exit(1)
    
    input_xml = sys.argv[1]
    output_csv = sys.argv[2]
    
    extract_reactome_data(input_xml, output_csv)
