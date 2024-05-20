import os
import json
import re
import requests
import anthropic
import time
from dotenv import load_dotenv

load_dotenv()

def extract_prompt(code):
    """
    Extracts the prompt from the code comments.
    Looks for a comment in the format '/// @prompt ...' and returns the text after '@prompt'.
    If no such comment is found, returns None.
    """
    pattern = r"///\s*@prompt\s*(.*)"
    match = re.search(pattern, code, re.MULTILINE)
    if match:
        return match.group(1).strip()
    else:
        return None

def generate_prompt(code):
    """
    Uses the Claude API to generate a prompt based on the given code.

    Args:
        code (str): The Move code to be summarized and used as the basis for generating a prompt.

    Returns:
        str: The generated prompt in English.

    Raises:
        None

    Notes:
        - Sends the code to Claude and asks it to summarize the code and generate a prompt in English.
        - If Claude's response doesn't contain a '<prompt>' tag, the entire response is used as the prompt.
        - Uses the Anthropic API to communicate with Claude.
        - Waits for 1 second before each request to avoid exceeding the rate limit.
    """
    time.sleep(1)  # Wait for 1 second before each request to avoid exceeding the rate limit
    api_env = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_env)
    prompt = f"""Please summarize the following Move code and generate a concise prompt in English that describes what the code does:

<code>
{code}
</code>

Provide your summary and prompt in English, and enclose the prompt inside <prompt> tags."""

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    )

    print(f"Claude's raw response: {message.content}")

    response_text = message.content
    if isinstance(response_text, list) and len(response_text) > 0:
        response_text = response_text[0]
    if isinstance(response_text, dict) and 'text' in response_text:
        response_text = response_text['text']
    if hasattr(response_text, 'text'):
        response_text = response_text.text

    print(f"Processed response text: {response_text}")

    prompt_match = re.search(r"<prompt>(.*?)</prompt>", response_text, re.DOTALL)
    if prompt_match:
        return prompt_match.group(1).strip()
    else:
        print("No <prompt> tag found in Claude's response. Using the entire response as the prompt.")
        return response_text

def remove_license(code):
    """
    Removes the Apache license text from the code.
    Looks for the 'module' keyword and returns all lines from there onwards.
    If 'module' is not found, returns the original code.
    """
    lines = code.split("\n")
    module_index = None
    for i, line in enumerate(lines):
        if line.startswith("module"):
            module_index = i
            break
    if module_index is not None:
        return "\n".join(lines[module_index:]).strip()
    else:
        return code.strip()

def get_move_files(repo_url):
    """
    Retrieves all Move files from a GitHub repository.
    Calls the GitHub API to get the repository tree and filters for files with a '.move' extension.
    Returns a list of file paths.
    """
    api_url = f"https://api.github.com/repos/{repo_url}/git/trees/main?recursive=1"
    response = requests.get(api_url)
    if response.status_code == 200:
        tree = response.json()["tree"]
        move_files = [file["path"] for file in tree if file["path"].endswith(".move")]
        return move_files
    else:
        print(f"Failed to fetch repository tree: {response.status_code}")
        return []

def get_move_code(repo_url, file_path):
    """
    Retrieves the content of a specific Move file from a GitHub repository.
    Calls the GitHub API to get the raw content of the file.
    Returns the file content as a string.
    """
    url = f"https://raw.githubusercontent.com/{repo_url}/main/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch file content: {response.status_code}")
        return None

def create_jsonl_dataset(repo_url, output_file):
    """
    Creates a JSONL dataset file from a GitHub repository.

    Parameters:
        repo_url (str): The URL of the GitHub repository.
        output_file (str): The path to the output file where the JSONL dataset will be written.

    Returns:
        None

    This function retrieves all Move files from the repository, extracts prompts, and generates prompts using Claude API.
    It writes each prompt-completion pair as a JSON object to the output file.
    """
    move_files = get_move_files(repo_url)
    with open(output_file, "w") as f:
        for file_path in move_files:
            code = get_move_code(repo_url, file_path)
            if code:
                prompt = extract_prompt(code)
                if prompt is None:
                    completion = remove_license(code)
                    retry_count = 0
                    while retry_count < 3:  # Retry up to 3 times
                        try:
                            prompt = generate_prompt(completion)  # Pass the completion to generate_prompt
                            break
                        except anthropic.RateLimitError:
                            retry_count += 1
                            print(f"Rate limit exceeded. Retrying in {retry_count * 5} seconds...")
                            time.sleep(retry_count * 5)  # Wait for an increasing amount of time before retrying
                    else:
                        print("Failed to generate prompt after 3 retries. Skipping this file.")
                        continue
                else:
                    completion = remove_license(code)
                json_line = json.dumps({"prompt": prompt, "completion": completion})
                f.write(json_line + "\n")

    print(f"JSONL dataset created: {output_file}")
repo_url = os.getenv("PROJECT_ID")
output_file = repo_url.replace("/","-")+"_dataset.jsonl"
create_jsonl_dataset(repo_url, output_file)