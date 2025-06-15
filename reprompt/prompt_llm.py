import os
import re
import datetime
from openai import OpenAI
from reprompt.parse_config import get_active_config
from reprompt.utils import format_string, read_file


class RewardPrompter:
    """
    Class for generating reward functions for Atari games using OpenAI's API.
    Manages prompt generation, API communication, output organization, and logging.
    """

    def __init__(self, game, seed=None) -> None:
        """
        Initialize the RewardPrompter with configuration and API setup.

        Args:
            seed (int, optional): Seed for deterministic output (if supported by model).
        """
        self.config = get_active_config()
        self.client = OpenAI(api_key=self._get_api_key())
        self.game = game.lower()
        self.model = self.config.get("openai.model")
        self.temperature = self.config.get("openai.temperature")
        self.max_retries = self.config.get("prompt.max_retries")
        self.seed = seed

    def _get_api_key(self) -> str:
        """
        Retrieve or prompt for OpenAI API key.

        Returns:
            str: OpenAI API key.

        Raises:
            FileNotFoundError: If API key is not found and not provided interactively.
        """
        try:
            with open("secret/openai-api-key", "r") as file:
                return file.read().strip()
        except FileNotFoundError:
            api_key = input("OpenAI API key not found. Enter API key: ").strip()
            save = input("Save this API key for future use? [y/N] ").strip().lower()
            if save in ["y", "yes"]:
                os.makedirs("secret", exist_ok=True)
                with open("secret/openai-api-key", "w") as file:
                    file.write(api_key)

            return api_key

    def _get_system_prompt(self, context) -> str:
        """
        Retrieve the system prompt from the configuration.

        Args:
            context (dict): Context dictionary to fill in the prompt.

        Returns:
            str: The system prompt string.

        Raises:
            ValueError: If the system prompt is not defined in the config.
        """
        system_prompt = self.config.get("prompt.system_prompt")
        if not system_prompt:
            raise ValueError("prompt.system_prompt must be defined in the config.")

        system_prompt = format_string(system_prompt, context=context)

        return system_prompt

    def _get_prompts(self, context) -> list[str]:
        """
        Generate prompt(s) for a given game based on configuration.

        Args:
            context (dict): Context dictionary to fill in the prompt.

        Returns:
            list of str: List of formatted prompts for the game.

        Raises:
            ValueError: If prompt.reward_prompt is not a string or list of strings.
        """
        templates = self.config.get("prompt.reward_prompt")

        if isinstance(templates, list):
            return [format_string(template, context=context) for template in templates]
        else:
            raise ValueError("prompt.reward_prompt must be a list of strings.")

    def _get_error_prompt(self, context, error_message, function_name) -> str:
        """
        Generate an error prompt for a given game.

        Args:
            context (dict): Context dictionary to fill in the prompt.
            error_message (str): Error message to include in the prompt.
            function_name (str): Function name to include in the prompt.

        Returns:
            str: Formatted error prompt for the game.
        """
        context.update(
            {
                "error_message": error_message,
                "function_name": function_name,
            }
        )

        template = self.config.get("prompt.error_template")
        if not template:
            raise ValueError("prompt.error_template must be defined in the config.")

        error_prompt = format_string(template, context=context)

        return error_prompt

    def _create_output_folder(self) -> str:
        """
        Create a timestamped output folder for a game's prompt results.

        Returns:
            str: Path to the created output folder.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        config_name = self.config.get("general.config_name")
        output_folder = f"out/{self.game}/{timestamp}-{config_name}"
        os.makedirs(output_folder, exist_ok=True)

        return output_folder

    def _extract_functions(self, responses) -> list[str]:
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

    def _log_output(self, folder, conversation, errors, methods) -> None:
        """
        Log conversation, errors, and the combined reward function code to output files.

        Args:
            folder (str): Path to the output folder.
            conversation (list of dict): List of conversation entries.
            errors (str): Collected error messages, if any.
            methods (list of str): List of extracted Python code blocks.
        """
        with open(os.path.join(folder, "conversation.txt"), "w") as f:
            for entry in conversation:
                f.write(f"{entry['role'].upper()}: {entry['content']}\n\n")

        if errors:
            with open(os.path.join(folder, "errors.txt"), "w") as f:
                f.write(errors)

        with open(os.path.join(folder, "reward_function.py"), "w") as f:
            f.write(f"from ocatari.ram.{self.game} import *\n\n")
            for method in methods:
                f.write(method + "\n\n")

        with open(os.path.join(folder, "config.toml"), "w") as f:
            f.write(str(self.config))

    def _call_openai(self, conversation) -> str:
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

    def _check_syntax(self, function_code: str) -> str | None:
        """
        Check the syntax of a single Python function.

        Args:
            function_code (str): The Python function code as a string.

        Returns:
            str or None: Returns the syntax error message if invalid, else None.
        """
        try:
            compile(function_code, "<string>", "exec")
            return None
        except SyntaxError as e:
            return f"SyntaxError: {e.msg} at line {e.lineno}, offset {e.offset}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _get_method_name(self, function_code: str) -> str | None:
        """
        Extracts the function name from a Python function definition string.

        Args:
            function_code (str): The full Python function code.

        Returns:
            str or None: The function name if found, else None.
        """
        match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", function_code)

        return match.group(1) if match else None

    def _remove_duplicate_methods(self, generated_methods: list[str]) -> list[str]:
        """
        Remove duplicate methods from the list based on their function names,
        preserving the first occurrence of each function.

        Args:
            generated_methods (list of str): List of Python function code strings.

        Returns:
            list of str: List with duplicates removed.
        """
        seen = set()
        unique_methods = []

        for method in generated_methods:
            name = self._get_method_name(method)
            if name and name not in seen:
                seen.add(name)
                unique_methods.append(method)
            elif not name:
                # If no function name found, keep it (or skip depending on your policy)
                unique_methods.append(method)

        return unique_methods

    def _define_context(self) -> dict:
        """
        Define the context for the game, including game name and any other relevant details.

        Args:
            game (str): The name of the game.

        Returns:
            dict: Context dictionary with game-specific information.
        """
        context = {
            "game": self.game,
            "model": self.model,
            "temperature": self.temperature,
            "seed": self.seed,
            "parent_objects": read_file("context/games/game_objects.py"),
            "game_objects": read_file(f"context/games/{self.game}/game_objects.py"),
            "game_description": read_file(
                f"context/games/{self.game}/game_description.txt"
            ),
        }

        return context

    def master_prompt(self):
        """
        Main execution loop: iterates through configured games, generates prompts,
        calls OpenAI API, extracts reward functions, and logs all output.
        """

        ######################################################
        # Initialize conversation and output structures
        ######################################################
        context = self._define_context()

        system_prompt = self._get_system_prompt(context)
        conversation = [{"role": "system", "content": system_prompt}]

        generated_methods = []
        errors = ""
        output_folder = self._create_output_folder()

        ######################################################
        # Generate initial prompts and call OpenAI API
        ######################################################
        try:
            prompts = self._get_prompts(context)
            for prompt_text in prompts:
                conversation.append({"role": "user", "content": prompt_text})
                response_text = self._call_openai(conversation)
                conversation.append({"role": "assistant", "content": response_text})

                extracted_methods = self._extract_functions([response_text])
                generated_methods.extend(extracted_methods)
        except Exception as e:
            print(f"Error generating prompts for game '{self.game}': {str(e)}")
            errors += f"Error for game '{self.game}': {str(e)}\n"

        if not generated_methods:
            raise ValueError(f"No valid methods generated for game '{self.game}'.")

        ######################################################
        # Check syntax of generated methods and fix errors
        ######################################################
        # TODO: fix error handling

        attempt = 0
        has_errors = False
        while attempt < self.max_retries and generated_methods and has_errors:
            try:
                for method in generated_methods:
                    success, syntax_error = self._check_syntax(method)
                    if syntax_error:
                        has_errors = True
                        errors += f"Syntax error in method:\n{method}\nError: {syntax_error}\n"
                    else:
                        continue

                    prompt_text = self._get_error_prompt(
                        self.game, syntax_error, method
                    )
                    conversation.append({"role": "user", "content": prompt_text})
                    response_text = self._call_openai(conversation)
                    conversation.append({"role": "assistant", "content": response_text})

                    fixed_methods = self._extract_functions([response_text])
                    if fixed_methods:
                        gen_methods_dict = {
                            self._get_method_name(method): method
                            for method in generated_methods
                            if self._get_method_name(method)
                        }
                    else:
                        errors += f"Failed to fix method: {method}\n"
                        continue

                    for fixed in fixed_methods:
                        fixed_name = self._get_method_name(fixed)
                        if fixed_name in gen_methods_dict:
                            idx = generated_methods.index(gen_methods_dict[fixed_name])
                            generated_methods[idx] = fixed
                            gen_methods_dict[fixed_name] = fixed
                        else:
                            generated_methods.append(fixed)
                            gen_methods_dict[fixed_name] = fixed
            except Exception as e:
                errors += f"Error checking syntax for game '{self.game}': {str(e)}\n"

        ######################################################
        # Check methods in HackAtari and fix errors
        ######################################################
        # TODO: Implement HackAtari integration to validate methods

        ######################################################
        # Log all outputs: conversation, errors, and methods
        ######################################################
        self._log_output(output_folder, conversation, errors, generated_methods)
