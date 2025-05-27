from google import genai
from google.genai import types
from pydantic import BaseModel
import pathlib
import httpx
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Script with a mandatory model argument")
    parser.add_argument(
        "-m", "--model",
        type=str,
        required=True,
        help="Name of the model to use"
    )
    return parser.parse_args()

args = parse_args()
    

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

class Result(BaseModel):
    SummaryOfCritique: str
    ImprovedShortText: str

# Retrieve and encode the PDF byte
filepathSum = pathlib.Path("short.txt")
filepathPapers = pathlib.Path("papers.txt")

prompt = """
You are given the concatenated text of one or more scientific articles, and in a second file a short text file with statements, backed up by references. First, check if all references in the short text also correspond to their full text as part of the papers file. Use the delimiter ---END OF PAPER--- to split papers.txt into individual papers. Then, for every part of the short text that ends with references, check: 1. all statements must be directly supported by experimental evidence in experimental papers or statements in review papers; 2. all statements must not misrepresent or exaggerate findings from the article(s); 3. If quantitative data (numbers, percentages, p-values) is mentioned, it must match the article(s) precisely. 4. all statements must not introduce information or conclusions not present in the cited article(s). 5. either all results were obtained using human cell lines, or the cell lines used, with their species, are mentioned explicitly in the statements; 6. either all results were obtained using the Dengue strain 16681, or the viral strain used is mentioned explicitly. After judging all statements with references, if some rules were broken, write out your critique and an improved short text that only changes those statements that you criticized.
"""
response = client.models.generate_content(
        model=args.model,
  contents=[
      types.Part.from_bytes(
        data=filepathSum.read_bytes(),
        mime_type='text/plain',
      ),
      types.Part.from_bytes(
        data=filepathPapers.read_bytes(),
        mime_type='text/plain',
      ),
      prompt],
  config={
        "response_mime_type": "application/json",
        "response_schema": Result
    })
print(response.text)
