from google import genai
from google.genai import types
from pydantic import BaseModel
import pathlib
import httpx
import argparse, os


parser = argparse.ArgumentParser(description='Process a string input.')
parser.add_argument('input_string', type=str, help='A string argument')
args = parser.parse_args()

arg = args.input_string

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Retrieve and encode the PDF byte
filepath = pathlib.Path(arg)
if filepath.stat().st_size < 10000:
    exit(0)

class FundingOrganization(BaseModel):
    FundingOrganizationName: str
    FundingOrganizationPlace: str
    FundingOrganizationCountry: str

class Result(BaseModel):
    Review: bool
    CellLines: list[str]
    ViralStrains: list[str]
    LabTechniques: list[str]
    StatisticalMethods: list[str]
    FundingOrganizations: list[FundingOrganization]
    DOI: str

prompt = """
Only using the methods setion, list all cell lines, virus strains, laboratory experimental techniques, statistical techniques used in this scientific article. Do not do this if this is a review article. Ignore any information where the text describes that other authors were using cell lines, virus strains, techniques. Ignore the reference section. In all cases, extract the funding organizations and the article DOI if possible. For every funding organization, record its name, place, and country. If the article has a funding section, use this information exclusively for funding.
"""
response = client.models.generate_content(
  model="gemini-2.0-flash",
  contents=[
      types.Part.from_bytes(
        data=filepath.read_bytes(),
        mime_type='text/plain',
      ),
      prompt],
  config={
        "response_mime_type": "application/json",
        "response_schema": Result
    })
print(response.text)
