from resllm.config import ConfigParser
from resllm.utils import format_string
from resllm.functions import (
    extract_functions,
    remove_duplicate_functions,
    check_function_syntax,
    replace_function,
    get_function_name,
)
from resllm.core import run_episodes
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
        self.game = game
        self.context = context
        self.seed = seed
        self.model = self.config.get("openai.model")
        self.temperature = self.config.get("openai.temperature")
        self.max_retries = self.config.get("prompt.max_retries")
        self.conversation = []
        self.generated_functions = []
        self.errors = []
        self.rewards = []

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

    def _get_error_prompt(self, context: dict, error_message: str) -> str:
        """
        Generate an error prompt for a given game.

        Args:
            context (dict): Context dictionary to fill in the prompt.
            error_message (str): Error message to include in the prompt.

        Returns:
            str: Formatted error prompt for the game.
        """
        context.update(
            {
                "error_message": error_message,
            }
        )

        template = self.config.get("prompt.error_prompt")
        if not template:
            raise ValueError("prompt.error_prompt must be defined in the config.")

        error_prompt = format_string(template, context=context)

        return error_prompt

    def _call_openai(self) -> str:
        """
        Call the OpenAI chat completion API with the conversation.

        Returns:
            str: The content of the assistant's reply.
        """
        response = self.client.chat.completions.create(
            messages=self.conversation,  # type: ignore
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
        filename: str,
        content: str | list,
        delimiter: str = "\n\n",
        overwrite: bool = False,
    ) -> None:
        """
        Log content to a specified file in the output folder.

        Args:
            folder (str): Path to the output folder.
            filename (str): Name of the file to write to.
            content (str or list): Content to write. Lists will be joined with delimiter.
            delimiter (str, optional): Separator for list content. Defaults to "\n\n".
            overwrite (bool, optional): Whether to overwrite the file. Defaults to False (append).
        """
        file_path = os.path.join(folder, filename)

        mode = "w" if overwrite else "a"
        with open(file_path, mode) as f:
            if isinstance(content, list):
                f.write(delimiter.join(content))
            else:
                f.write(content)

            if isinstance(content, list) or not content.endswith(delimiter):
                f.write(delimiter)

    def _check_and_fix_syntax(self, output_folder: str) -> bool:
        """
        Check the syntax of generated functions and attempt to fix any syntax errors.

        Args:
            output_folder (str): Path to the output folder where reward_function.py is saved.

        Returns:
            bool: If syntax errors were found.
        """
        syntax_errors = False
        try:
            for function in self.generated_functions:
                success, syntax_error = check_function_syntax(function)
                function_name = get_function_name(function)

                if success:
                    continue

                print(f"Syntax error in function: {function_name}")
                self.errors.append(
                    f"Syntax error in function: {function_name}\n{function}\nError: {syntax_error}\n"
                )

                syntax_errors = True

                print(f"Attempting to fix syntax error in function: {function_name}...")
                prompt_text = self._get_error_prompt(
                    self.context,
                    syntax_error if syntax_error is not None else "",
                )
                self.conversation.append({"role": "user", "content": prompt_text})
                response_text = self._call_openai()
                self.conversation.append(
                    {"role": "assistant", "content": response_text}
                )
                print("Response received for syntax fix attempt.")

                fixed_functions = extract_functions(response_text)
                print(f"Extracted {len(fixed_functions)} functions from response.")

                if fixed_functions:
                    for fixed_function in fixed_functions:
                        replace_function(self.generated_functions, fixed_function)
                else:
                    print(f"Failed to fix function: {function}")
                    self.errors.append(
                        f"Failed to fix function:\n{function}\nError: {syntax_error}\n"
                    )

        except Exception as e:
            print(f"Error checking syntax: {str(e)}")
            self.errors.append(f"Error checking syntax: {str(e)}\n")
            syntax_errors = True

        return syntax_errors

    def _check_and_fix_hackatari(self, output_folder: str) -> bool:
        """
        Check the generated functions in HackAtari and attempt to fix errors.

        Args:
            output_folder (str): Path to the output folder where reward_function.py is saved.

        Returns:
            bool: If errors were found.
        """
        hackatari_errors = False
        try:
            print("Running HackAtari validation...")
            rewardfunc_path = os.path.join(output_folder, "reward_function.py")
            success, hackatari_rewards, hackatari_error = run_episodes(
                game=self.game,
                rewardfunc_path=rewardfunc_path,
                num_episodes=self.config.get("env.num_episodes", 5),
                obs_mode=self.config.get("env.obs_mode", "dqn"),
            )

            if success:
                self.rewards.append(str(hackatari_rewards))
                print("All functions validated successfully in HackAtari.")
                return False  # no errors

            print(f"Error validating functions in HackAtari: {hackatari_error}")
            self.errors.append(
                f"Error validating functions in HackAtari: {hackatari_error}\n"
            )
            hackatari_errors = True

            print("Attempting to fix HackAtari error...")
            prompt_text = self._get_error_prompt(
                self.context,
                hackatari_error if hackatari_error is not None else "",
            )
            self.conversation.append({"role": "user", "content": prompt_text})
            response_text = self._call_openai()
            self.conversation.append({"role": "assistant", "content": response_text})
            print("Response received for HackAtari fix attempt.")

            fixed_functions = extract_functions(response_text)
            print(f"Extracted {len(fixed_functions)} fixed functions from response.")

            if fixed_functions:
                for fixed_function in fixed_functions:
                    replace_function(self.generated_functions, fixed_function)
            else:
                print("Failed to fix HackAtari error.")
                self.errors.append(
                    f"Failed to fix HackAtari error:\n{hackatari_error}\n"
                )

        except Exception as e:
            print(f"Error checking HackAtari compatibility: {str(e)}")
            self.errors.append(f"Error checking HackAtari compatibility: {str(e)}\n")
            hackatari_errors = True

        return hackatari_errors

    def master_prompt(self):
        """
        Main execution loop: iterates through configured games, generates prompts,
        calls OpenAI API, extracts reward functions, and logs all output.
        """
        ######################################################
        # Initialize conversation and output structures
        ######################################################
        print(
            f"Starting reward function generation for game '{self.game}' with config '{self.config.get('general.config_name')}'..."
        )
        output_folder = self._create_output_folder()

        ######################################################
        # Generate initial prompt and call OpenAI API
        ######################################################
        try:
            print("Getting system prompt...")
            system_prompt = self._get_system_prompt(self.context)
            self.conversation.append({"role": "system", "content": system_prompt})
        except ValueError as e:
            print(f"Error generating system prompt: {str(e)}")
            self.errors.append(f"Error generating system prompt: {str(e)}\n")

        ######################################################
        # Call OpenAI API to generate reward functions
        ######################################################
        try:
            prompts = self._get_prompts(self.context)
            for idx, prompt_text in enumerate(prompts):
                print(f"Generating prompt {idx + 1}/{len(prompts)}")
                self.conversation.append({"role": "user", "content": prompt_text})
                response_text = self._call_openai()
                self.conversation.append(
                    {"role": "assistant", "content": response_text}
                )
                print(f"Response received for prompt {idx + 1}/{len(prompts)}.")
                extracted_functions = extract_functions(response_text)
                print(f"Extracted {len(extracted_functions)} functions from response.")
                self.generated_functions.extend(extracted_functions)

            if self.generated_functions:
                self.generated_functions = remove_duplicate_functions(
                    self.generated_functions
                )
            else:
                print("No valid functions generated.")
                self.errors.append("No valid functions generated.")

            self._log_output(
                output_folder,
                "reward_function.py",
                [f"from ocatari.ram.{self.game} import *"] + self.generated_functions,
                overwrite=True,
            )

        except Exception as e:
            print(f"Error generating prompts: {str(e)}")
            self.errors.append(f"Error generating prompts: {str(e)}")

        ######################################################
        # Validate and fix generated functions
        ######################################################
        print("Starting validation...")

        for attempt in range(1, self.max_retries + 1):
            print(f"Validation attempt {attempt}/{self.max_retries}...")

            syntax_errors = self._check_and_fix_syntax(output_folder)
            self.generated_functions = remove_duplicate_functions(
                self.generated_functions
            )

            self._log_output(
                output_folder,
                "reward_function.py",
                [f"from ocatari.ram.{self.game.lower()} import *"]
                + self.generated_functions,
                overwrite=True,
            )

            hackatari_errors = self._check_and_fix_hackatari(output_folder)
            self.generated_functions = remove_duplicate_functions(
                self.generated_functions
            )

            self._log_output(
                output_folder,
                "reward_function.py",
                [f"from ocatari.ram.{self.game} import *\n\n"]
                + self.generated_functions,
                overwrite=True,
            )

            if not syntax_errors and not hackatari_errors:
                print("No errors found in functions after validation.")
                break

        else:
            print("Reached maximum retry attempts.")

        ######################################################
        # Log all outputs: conversation, errors, and functions
        ######################################################
        print(f"Logging output to folder: {output_folder}")
        self._log_output(output_folder, "config.toml", str(self.config))
        self._log_output(
            output_folder,
            "conversation.txt",
            [f"{e['role'].upper()}: {e['content']}" for e in self.conversation],
        )
        self._log_output(output_folder, "errors.txt", self.errors)
        self._log_output(output_folder, "rewards.txt", self.rewards)
        print("Output logged successfully.")
