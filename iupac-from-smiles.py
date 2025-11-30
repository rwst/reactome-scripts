# Source - https://stackoverflow.com/a/77657583
# Posted by user16769489, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-29, License - CC BY-SA 4.0

import argparse
import pubchempy

def main():
  parser = argparse.ArgumentParser(description='Convert SMILES string to IUPAC name.')
  parser.add_argument('smiles', type=str, help='The SMILES string to convert.')
  args = parser.parse_args()

  compounds = pubchempy.get_compounds(args.smiles, namespace='smiles')
  match = compounds[0]
  print(match.iupac_name)

if __name__ == "__main__":
  main()

