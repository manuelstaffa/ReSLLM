import os
from openai import OpenAI


def get_api_key():
    # Load your OpenAI API key from an environment variable or a secure location
    with open("RePrompt/secret/openai-api-key.txt", "r") as file:
        api_key = file.read().strip()
        return api_key


client = OpenAI(api_key=get_api_key())

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are my helpful assistant."},
        {
            "role": "user",
            "content": "Give me a python function to calculate the factorial of a number.",
        },
    ],
    # temperature=1.0,             # Sampling randomness (0.0 to 2.0). Higher → more random.
    # top_p=1.0,                   # Nucleus sampling probability (0.0 to 1.0). Alternative to temperature.
    # max_tokens=None,             # Max tokens in the response. Defaults to model limit.
    # presence_penalty=0.0,        # Penalize new tokens based on whether they appear in the text so far.
    # frequency_penalty=0.0,       # Penalize tokens that appear frequently.
    # logit_bias={},               # Modify likelihood of specific tokens (token_id: bias_value).
    # user=None,                   # String ID to track end-user (for abuse detection/logging).
    # n=1,                         # Number of completions to generate for each prompt.
    # stop=None,                   # Sequence or list of sequences where the API stops generating further tokens.
    # seed=None,                   # Integer seed for reproducible results.
    # stream=False,                # Whether to stream partial progress (for real-time responses).
    # tools=None,                  # List of tool definitions (e.g., function-calling tools).
    # tool_choice=None,            # Specify tool to use ("none", "auto", or a specific tool name).
    # response_format=None,        # "text" or "json" (relevant for function-calling with JSON responses).
    # logprobs=None,               # Include token-level log probabilities (only supported in some models).
    # max_tokens=100,               # Example override — limit to 100 tokens in this case.
)

print(response.choices[0].message.content)
print(response.choices[0].message.content.strip())
