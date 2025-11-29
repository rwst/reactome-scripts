# Source - https://stackoverflow.com/a/77657583
# Posted by user16769489, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-29, License - CC BY-SA 4.0

import pubchempy

name = ["C[C@H]([NH2+][C@@H](CCc1ccccc1)C(=O)[O-])C(=O)N1CCC[C@H]1C(=O)[O-]"]

for i in name:
  compounds = pubchempy.get_compounds(i, namespace='smiles')
  match = compounds[0]
  print(match.iupac_name)

