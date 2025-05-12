from pathlib import Path
import subprocess
import sys

# Get all PDF files in the current directory
pdf_files = Path('.').glob('*.pdf')

for pdf_file in pdf_files:
    # Get the basename (filename without extension)
    stem = pdf_file.stem
    
    # Define the corresponding .txt file path
    txt_path = Path(stem + '.txt')
    
    # If the .txt file does not exist, run pdftotext to generate it
    if not txt_path.exists():
        subprocess.run(['pdftotext', str(pdf_file)])
        print("pdftotext {}".format(stem))
    
    # Define the corresponding .json file path
    json_path = Path(stem + '.json')
    
    # If the .json file does not exist, run X.py and capture its output
    if not json_path.exists():
        result = subprocess.run([sys.executable, 'getdata.py', str(txt_path)], 
                              capture_output=True, 
                              text=True)
        # Write the output of X.py to the .json file
        with open(json_path, 'w') as f:
            f.write(result.stdout)
        print("getdata {}".format(stem))
