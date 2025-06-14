import os
import re
import datetime
from openai import OpenAI
from reprompt.parse_config import get_active_config
from reprompt.utils import format_prompt, read_file


class RewardPrompter:
    """
    Class for generating reward functions for Atari games using OpenAI's API.
    Manages prompt generation, API communication, output organization, and logging.
    """

    def __init__(self, seed=None):
        """
        Initialize the RewardPrompter with configuration and API setup.

        Args:
            seed (int, optional): Seed for deterministic output (if supported by model).
        """
        self.config = get_active_config()
        self.client = OpenAI(api_key=self._get_api_key())
        self.games = self.config.get("env.game")
        self.model = self.config.get("openai.model")
        self.temperature = self.config.get("openai.temperature")
        self.seed = seed
        self.system_prompt = self.config.get("prompt.system_message")

    def _get_api_key(self):
        """
        Retrieve or prompt for OpenAI API key.

        Returns:
            str: OpenAI API key.

        Raises:
            FileNotFoundError: If API key is not found and not provided interactively.
        """
        try:
            with open("RePrompt/secret/openai-api-key", "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            api_key = input("OpenAI API key not found. Enter API key: ").strip()
            save = input("Save this API key for future use? [y/N] ").strip().lower()
            if save in ["y", "yes"]:
                os.makedirs("RePrompt/secret", exist_ok=True)
                with open("RePrompt/secret/openai-api-key", "w") as file:
                    file.write(api_key)
            return api_key

    def _get_prompts(self, game):
        """
        Generate prompt(s) for a given game based on configuration.

        Args:
            game (str): Game name to fill in the prompt context.

        Returns:
            list of str: List of formatted prompts for the game.

        Raises:
            ValueError: If prompt.template is not a string or list of strings.
        """
        context = {
            "game": game,
            "model": self.model,
            "temperature": self.temperature,
            "seed": self.seed,
            "parent_objects": read_file("RePrompt/context/game_objects.py"),
            "game_objects": read_file(f"RePrompt/context/{game}/game_objects.py"),
            "game_description": read_file(
                f"RePrompt/context/{game}/game_description.txt"
            ),
        }

        template = self.config.get("prompt.template")

        if isinstance(template, list):
            return [format_prompt(pt, context=context) for pt in template]
        elif isinstance(template, str):
            return [format_prompt(template, context=context)]
        else:
            raise ValueError("prompt.template must be a string or list of strings.")

    def _create_output_folder(self, game):
        """
        Create a timestamped output folder for a game's prompt results.

        Args:
            game (str): Name of the game.

        Returns:
            str: Path to the created output folder.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        config_name = self.config.get("config_name", "default")
        output_folder = f"RePrompt/out/{game}/{timestamp}-{config_name}"
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def _extract_functions(self, responses):
        """
        Extract all Python code blocks from a list of LLM responses.

        Args:
            responses (list of str): List of LLM responses containing Python code blocks.

        Returns:
            list of str: List of extracted Python code blocks.
        """
        code_blocks = []
        code_pattern = re.compile(r"```(?:python)?(.*?)```", re.DOTALL | re.IGNORECASE)

        for response in responses:
            matches = code_pattern.findall(response)
            for code in matches:
                code_blocks.append(code.strip())

        return code_blocks

    def _log_output(self, folder, conversation, errors, methods, game):
        """
        Log conversation, errors, and the combined reward function code to output files.

        Args:
            folder (str): Path to the output folder.
            conversation (list of dict): List of conversation entries.
            errors (str): Collected error messages, if any.
            methods (list of str): List of extracted Python code blocks.
            game (str): The game name for import path.
        """
        with open(os.path.join(folder, "conversation.txt"), "w") as f:
            for entry in conversation:
                f.write(f"{entry['role'].upper()}: {entry['content']}\n\n")

        if errors:
            with open(os.path.join(folder, "errors.txt"), "w") as f:
                f.write(errors)

        with open(os.path.join(folder, "reward_function.py"), "w") as f:
            f.write(f"from ocatari.ram.{game} import *\n\n")
            for method in methods:
                f.write(method + "\n\n")

    def _call_openai(self, conversation):
        """
        Call the OpenAI chat completion API with the conversation.

        Args:
            conversation (list of dict): List of conversation entries in OpenAI chat format.

        Returns:
            str: The content of the assistant's reply.
        """
        response = self.client.chat.completions.create(
            messages=conversation,
            model=self.model,
            seed=self.seed,
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()

    def master_prompt(self):
        """
        Main execution loop: iterates through configured games, generates prompts,
        calls OpenAI API, extracts reward functions, and logs all output.
        """
        for game in self.games:
            conversation = [{"role": "system", "content": self.system_prompt}]
            generated_methods = []
            errors = ""
            output_folder = self._create_output_folder(game)

            try:
                prompts = self._get_prompts(game)
                for prompt_text in prompts:
                    conversation.append({"role": "user", "content": prompt_text})
                    response_text = self._call_openai(conversation)
                    conversation.append({"role": "assistant", "content": response_text})

                    extracted_methods = self._extract_functions([response_text])
                    generated_methods.extend(extracted_methods)

            except Exception as e:
                errors += f"Error for game '{game}': {str(e)}\n"

            self._log_output(
                output_folder, conversation, errors, generated_methods, game
            )
