import os
import datetime
from openai import OpenAI

"""
def get_api_key():
    # Load your OpenAI API key from an environment variable or a secure location
    with open("RePrompt/secret/openai-api-key", "r") as file:
        api_key = file.read().strip()
        return api_key


client = OpenAI(api_key=get_api_key())

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are my helpful assistant."},
        {
            "role": "user",
            "content": "Give me a list of 5 interesting facts about the history of artificial intelligence.",
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
"""


class RePrompter:
    def __init__(self, game, model="gpt-4o", seed=None):
        self.client = client
        self.game = game
        self.model = model
        self.seed = seed
        self.system_fingerprint = None
        self.conversation_history = [
            {
                "role": "system",
                "content": "You are a helpful assistant that creates reward functions for reinforcement learning researchers.",
            },
        ]

    def prompt(self, prompt_text):
        """Generate a response to a prompt using the OpenAI API."""

        # Add the prompt to the conversation history
        self.conversation_history.append({"role": "user", "content": prompt_text})

        # Call the completion endpoint
        response = self.client.chat.completions.create(
            messages=self.conversation_history,
            model=self.model,
            seed=self.seed,
            top_p=0,  # Nucleus sampling probability (0.0 to 1.0). Alternative to temperature.
            # temperature=1.0,             # Sampling randomness (0.0 to 2.0). Higher → more random.
            # max_tokens=None,             # Max tokens in the response. Defaults to model limit.
            # presence_penalty=0.0,        # Penalize new tokens based on whether they appear in the text so far.
            # frequency_penalty=0.0,       # Penalize tokens that appear frequently.
            # logit_bias={},               # Modify likelihood of specific tokens (token_id: bias_value).
            # user=None,                   # String ID to track end-user (for abuse detection/logging).
            # n=1,                         # Number of completions to generate for each prompt.
            # stop=None,                   # Sequence or list of sequences where the API stops generating further tokens.
            # stream=False,                # Whether to stream partial progress (for real-time responses).
            # tools=None,                  # List of tool definitions (e.g., function-calling tools).
            # tool_choice=None,            # Specify tool to use ("none", "auto", or a specific tool name).
            # response_format=None,        # "text" or "json" (relevant for function-calling with JSON responses).
            # logprobs=None,               # Include token-level log probabilities (only supported in some models).
            # max_tokens=100,               # Example override — limit to 100 tokens in this case.
        )
        # Get system fingerprint
        self.system_fingerprint = response.system_fingerprint
        self.model = response.model

        response_text = response.choices[0].message.content.strip()

        self._add_to_conversation_history(prompt_text, response_text)
        self._log_prompt(prompt_text, response_text)

        return response_text

    def _add_to_conversation_history(self, request, answer):
        self.conversation_history.append({"role": "user", "content": request})
        self.conversation_history.append({"role": "system", "content": answer})

    def _log_prompt(self, prompt_text, response):
        # create response folder if it does not exist
        if not os.path.exists(f"RePrompt/context/{self.game}/responses"):
            os.makedirs(f"RePrompt/context/{self.game}/responses")

        # Save the response together with prompt to file
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        log = prompt_text + "\n---------------\n" + response
        with open(
            f"RePrompt/context/{self.game}/responses/{timestamp}_{self.seed}_{self.system_fingerprint}.txt",
            "w",
        ) as file:
            file.write(log)
