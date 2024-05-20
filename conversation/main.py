import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(azure_endpoint=os.getenv("AZ_ENDPOINT"),
                     api_version="2023-09-15-preview",
                     api_key=os.getenv("AZ_API_KEY"))

while True:
    prompt = input("LFG! \n Start type here: \n")
    response = client.completions.create(model=os.getenv("AZ_MODEL_ID"),
                                         prompt=prompt,
                                         temperature=1,
                                         max_tokens=100,
                                         top_p=0.5,
                                         frequency_penalty=0,
                                         presence_penalty=0,
                                         best_of=1,
                                         stop=None,
                                         stream=True
                                         )

    print("Type completion \n")
    for chunk in response:
        if hasattr(chunk, "choices") and len(chunk.choices) > 0:
            content = chunk.choices[0].text
            print(content, end="", flush=True)

    print()