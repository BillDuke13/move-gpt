# move-gpt
GPT Fine-tuning Model for Move Programming Language

## Key Features

- Retrieves Move code files from a specified GitHub repository
- Extracts prompts from code comments or generates prompts using the Claude API
- Creates a JSONL dataset file containing prompt-completion pairs
- Fine-tunes a GPT model using the generated dataset

## Prerequisites

- Python 3.x
- Azure OpenAI service API key
- Anthropic API key
- GitHub repository containing Move code

## Installation

1. Clone the repository
2. Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
3. Set up the required environment in the `.env` file:
```bash
# AZ_ENDPOINT: Azure OpenAI endpoint
# AZ_API_KEY: Azure OpenAI API key
# AZ_MODEL_ID: Azure OpenAI model ID
# ANTHROPIC_API_KEY: Anthropic API key
# PROJECT_ID: GitHub repository URL (e.g., username/repo)
mv .env.example .env
```

## Usage

### Generate DataSet

Example Dataset:

https://huggingface.co/datasets/billduke13/movelang-dataset

To generate a dataset, run the following command:
```bash
python dataset/main.py
```

### Conversational Model

To run the conversational model, use the following command:
```bash
python conversation/main.py
```

## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
