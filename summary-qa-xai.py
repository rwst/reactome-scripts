import os
from openai import OpenAI
from datetime import datetime
import markdown

# Configuration
API_KEY = os.getenv("XAI_API_KEY")
BASE_URL = "https://api.x.ai/v1"  

MODEL = "grok-3-mini"  # Assuming grok3 is available; adjust if needed
INPUT_FILES = ["papers.txt", "short.txt"]
MAX_TOKENS = None  # No output restriction

def read_input_files(file_paths):
    """Read content from input files."""
    content = ""
    for file_path in file_paths:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content += f"\n\n--- File: {file_path} ---\n\n"
                content += f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            raise
    return content

def prepare_messages(prompt, file_content):
    """Prepare the messages for the API request."""
    return [
        {
            "role": "system",
            "content": "You are Grok, created by xAI. Provide detailed reasoning and accurate responses."
        },
        {
            "role": "user",
            "content": f"{prompt}\n\n--- Input Files ---\n{file_content}"
        }
    ]

def format_output(completion):
    """Format the reasoning process and final answer as markdown."""
    answer = completion.choices[0].message.content or "No answer provided."
    
    answer_md = f"## Final Answer\n\n{answer}"
    
    return answer_md

def main():
    if not API_KEY:
        raise ValueError("XAI_API_KEY environment variable not set")

    # Initialize OpenAI client
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY
    )

    # Get prompt from user
    prompt = """
    You are given the concatenated text of one or more scientific articles, and in a second file a short text file with statements, backed up by references. First, check if all references in the short text also correspond to their full text as part of the papers file. Use the delimiter ---END OF PAPER--- to split papers.txt into individual papers. Then, for every part of the short text that ends with references, check: 1. all statements must be directly supported by experimental evidence in experimental papers or statements in review papers; 2. all statements must not misrepresent or exaggerate findings from the article(s); 3. If quantitative data (numbers, percentages, p-values) is mentioned, it must match the article(s) precisely. 4. all statements must not introduce information or conclusions not present in the cited article(s). 5. either all results were obtained using human cell lines, or the cell lines used, with their species, are mentioned explicitly in the statements; 6. either all results were obtained using the Dengue strain 16681, or the viral strain used is mentioned explicitly. After judging all statements with references, if some rules were broken, write out your critique and an improved short text that only changes those statements that you criticized.
    """

    # Read input files
    print("Reading input files...")
    file_content = read_input_files(INPUT_FILES)

    # Prepare messages
    print("Preparing messages...")
    messages = prepare_messages(prompt, file_content)

    # Call API
    print("Sending request to xAI API...")
    try:
        completion = client.chat.completions.create(
            model=MODEL,
#            reasoning_effort="high",  # Enable detailed reasoning (think_mode)
            messages=messages,
            temperature=0.7,
            max_tokens=MAX_TOKENS
        )
    except Exception as e:
        if "404" in str(e):
            print(f"API request failed: 404 Client Error. Endpoint not found.")
            print("Possible causes: Incorrect base URL, unavailable model, or deprecated endpoint.")
            print("Suggested action: Verify the endpoint and model at https://docs.x.ai or contact xAI support.")
        else:
            print(f"API request failed: {e}")
        raise

    # Format output
    print("Formatting output...")
    answer_md = format_output(completion)

    # Print token usage
    print("\nNumber of completion tokens (input):")
    print(completion.usage.completion_tokens)

    # Save output to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"grok3_output_{timestamp}.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"{answer_md}")

    print(f"Output saved to {output_file}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
