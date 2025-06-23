from resllm.parse_config import ConfigParser
from resllm.utils import format_string
from resllm.extract_functions import (
    extract_functions,
    remove_duplicate_functions,
    check_function_syntax,
    replace_function,
    get_function_name,
)
import os
import shutil
import datetime
from openai import OpenAI


class RewardPrompter:
    """
    Class for generating reward functions for Atari games using OpenAI's API.
    Manages prompt generation, API communication, output organization, and logging.
    """

    def __init__(
        self, config: ConfigParser, game: str, context: dict, seed: int | None = None
    ) -> None:
        """
        Initialize the RewardPrompter with configuration and API setup.

        Args:
            config (ConfigParser): Configuration parser instance with settings.
            game (str): Name of the Atari game to generate prompts for.
            context (dict): Context dictionary with game-specific information.
            seed (int, optional): Seed for deterministic output (if supported by model).
        """
        self.client = OpenAI(api_key=self._get_api_key())
        self.config = config
        self.game = game.lower()
        self.context = context
        self.seed = seed
        self.model = self.config.get("openai.model")
        self.temperature = self.config.get("openai.temperature")
        self.max_retries = self.config.get("prompt.max_retries")

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

    def _get_system_prompt(self, context: dict) -> str:
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

    def _get_prompts(self, context: dict) -> list[str]:
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

    def _get_error_prompt(
        self, context: dict, error_message: str, function_name: str
    ) -> str:
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

        template = self.config.get("prompt.error_prompt")
        if not template:
            raise ValueError("prompt.error_prompt must be defined in the config.")

        error_prompt = format_string(template, context=context)

        return error_prompt

    def _call_openai(self, conversation: list[dict]) -> str:
        """
        Call the OpenAI chat completion API with the conversation.

        Args:
            conversation (list of dict): List of conversation entries in OpenAI chat format.

        Returns:
            str: The content of the assistant's reply.
        """
        response = self.client.chat.completions.create(
            messages=conversation,  # type: ignore
            model=self.model,
            seed=self.seed,
            temperature=self.temperature,
        )

        content = response.choices[0].message.content
        return content.strip() if content is not None else ""

    def _create_output_folder(self) -> str:
        """
        Create a timestamped output folder for a game's prompt results.

        Returns:
            str: Path to the created output folder.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        config_name = self.config.get("general.config_name")
        game_folder = os.path.join("out", self.game)

        if self.config.get("general.clear", False) and os.path.exists(game_folder):
            for name in os.listdir(game_folder):
                if name.endswith(f"-{config_name}"):
                    shutil.rmtree(os.path.join(game_folder, name))

        output_folder = os.path.join(game_folder, f"{timestamp}-{config_name}")
        os.makedirs(output_folder, exist_ok=True)

        return output_folder

    def _log_output(
        self,
        folder: str,
        conversation: list[dict],
        errors: list[str],
        functions: list[str],
    ) -> None:
        """
        Log conversation, errors, and the combined reward function code to output files.

        Args:
            folder (str): Path to the output folder.
            conversation (list of dict): List of conversation entries.
            errors (list of str): Collected error messages, if any.
            functions (list of str): List of extracted Python code blocks.
        """
        with open(os.path.join(folder, "conversation.txt"), "w") as f:
            for entry in conversation:
                f.write(f"{entry['role'].upper()}: {entry['content']}\n\n")

        if errors:
            with open(os.path.join(folder, "errors.txt"), "w") as f:
                f.write("\n".join(errors))

        with open(os.path.join(folder, "reward_function.py"), "w") as f:
            f.write(f"from ocatari.ram.{self.game} import *\n\n")
            for method in functions:
                f.write(method + "\n\n")

        with open(os.path.join(folder, "config.toml"), "w") as f:
            f.write(str(self.config))

    def master_prompt(self):
        """
        Main execution loop: iterates through configured games, generates prompts,
        calls OpenAI API, extracts reward functions, and logs all output.
        """
        ######################################################
        # Initialize conversation and output structures
        ######################################################
        print(f"Starting prompt generation for game '{self.game}'...")
        output_folder = self._create_output_folder()
        conversation = []
        generated_functions = []
        errors = []

        ######################################################
        # Generate initial prompt and call OpenAI API
        ######################################################
        try:
            print(f"Getting system prompt for game '{self.game}'...")
            system_prompt = self._get_system_prompt(self.context)
            conversation = [{"role": "system", "content": system_prompt}]
        except ValueError as e:
            print(f"Error generating system prompt for game '{self.game}': {str(e)}")
            errors.append(f"Error for game '{self.game}': {str(e)}\n")

        ######################################################
        # Call OpenAI API to generate reward functions
        ######################################################
        # TODO:fix prompt (not fixing anything) (maybe replace?)
        try:
            prompts = self._get_prompts(self.context)
            for idx, prompt_text in enumerate(prompts):
                print(
                    f"Generating prompt {idx + 1}/{len(prompts)} for game '{self.game}'..."
                )
                conversation.append({"role": "user", "content": prompt_text})
                response_text = self._call_openai(conversation)
                conversation.append({"role": "assistant", "content": response_text})
                print(f"Response received for prompt {idx + 1}/{len(prompts)}.")
                extracted_functions = extract_functions(response_text)
                print(f"Extracted {len(extracted_functions)} functions from response.")
                generated_functions.extend(extracted_functions)
        except Exception as e:
            print(f"Error generating prompts for game '{self.game}': {str(e)}")
            errors.append(f"Error for game '{self.game}': {str(e)}\n")

        ######################################################
        # Deduplicate functions
        ######################################################
        print(f"Deduplicating functions for game '{self.game}'...")
        if generated_functions:
            generated_functions = remove_duplicate_functions(generated_functions)
        else:
            print(f"No valid functions generated for game '{self.game}'.")
            errors.append(f"No valid functions generated for game '{self.game}'.\n")

        ######################################################
        # Check syntax of generated functions and fix errors
        ######################################################
        print(f"Checking syntax of generated functions for game '{self.game}'...")
        while self.max_retries > 0:
            syntax_errors = False
            try:
                for function in generated_functions:
                    success, syntax_error = check_function_syntax(function)
                    function_name = get_function_name(function)

                    if success:
                        continue

                    print(f"Syntax error in function: {function_name}")
                    errors.append(
                        f"Syntax error in function: {function_name}\n{function}\nError: {syntax_error}\n"
                    )

                    syntax_errors = True
                    self.max_retries -= 1

                    print(
                        f"Attempting to fix syntax error in function: {function_name}..."
                    )
                    prompt_text = self._get_error_prompt(
                        self.context,
                        syntax_error if syntax_error is not None else "",
                        function,
                    )
                    conversation.append({"role": "user", "content": prompt_text})
                    response_text = self._call_openai(conversation)
                    conversation.append({"role": "assistant", "content": response_text})
                    print(
                        f"Response received for syntax fix attempt for game '{self.game}'."
                    )

                    fixed_functions = extract_functions(response_text)
                    print(
                        f"Extracted {len(fixed_functions)} fixed functions from response."
                    )
                    if fixed_functions:
                        print(
                            f"Replacing function in generated functions for game '{self.game}'."
                        )
                        for fixed_function in fixed_functions:
                            replace_function(generated_functions, fixed_function)
                    else:
                        print(f"Failed to fix function: {function}")
                        errors.append(
                            f"Failed to fix function:\n{function}\nError: {syntax_error}\n"
                        )

                if not syntax_errors:
                    print(f"All functions have valid syntax for game '{self.game}'.")
                    break
            except Exception as e:
                print(f"Error checking syntax for game '{self.game}': {str(e)}")
                errors.append(
                    f"Error checking syntax for game '{self.game}': {str(e)}\n"
                )

        ######################################################
        # Check functions in HackAtari and fix errors
        ######################################################
        print(f"Validating functions in HackAtari for game '{self.game}'...")
        # TODO: Implement HackAtari integration to validate functions

        ######################################################
        # Log all outputs: conversation, errors, and functions
        ######################################################
        print(f"Logging output for game '{self.game}' to folder: {output_folder}")
        self._log_output(output_folder, conversation, errors, generated_functions)
        print(f"Output logged successfully for game '{self.game}'.")
