import os
import datetime
from openai import OpenAI
from reprompt.parse_config import get_active_config
from reprompt.utils import format_prompt, read_file


class RewardPrompter:
    def __init__(self, seed=None):
        self.config = get_active_config()
        self.client = OpenAI(api_key=self._get_api_key())
        self.games = self.config.get("env.game")
        self.model = self.config.get("openai.model")
        self.seed = seed
        self.system_prompt = self.config.get("prompt.system_message")

    def _get_api_key(self):
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
        context = {
            "game": game,
            "model": self.model,
            "temperature": self.config.get("openai.temperature"),
            "seed": self.seed,
        }

        template = self.config.get("prompt.template")

        if isinstance(template, list):
            return [format_prompt(pt, context=context) for pt in template]
        elif isinstance(template, str):
            return [format_prompt(template, context=context)]
        else:
            raise ValueError("prompt.template must be a string or list of strings.")

    def _create_output_folder(self, game):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        config_name = self.config.get("config_name", "default")
        output_folder = f"RePrompt/out/{game}/{timestamp}-{config_name}"
        os.makedirs(output_folder, exist_ok=True)
        return output_folder

    def _log_output(self, folder, conversation, errors, methods):
        with open(os.path.join(folder, "conversation.txt"), "w") as f:
            for entry in conversation:
                f.write(f"{entry['role'].upper()}: {entry['content']}\n\n")

        if errors:
            with open(os.path.join(folder, "errors.txt"), "w") as f:
                f.write(errors)

        with open(os.path.join(folder, "reward_function.py"), "w") as f:
            for method in methods:
                f.write(method + "\n\n")

    def _call_openai(self, conversation):
        response = self.client.chat.completions.create(
            messages=conversation,
            model=self.model,
            seed=self.seed,
            temperature=self.config.get("openai.temperature"),
        )
        return response.choices[0].message.content.strip()

    def master_prompt(self):
        """
        Loop through all configured games, generate prompts, and call the OpenAI API.
        Logs conversation, errors, and generated code.
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

                    # Optional: extract functions from the response (simple approach)
                    extracted = self._extract_functions(response_text)
                    generated_methods.extend(extracted)

            except Exception as e:
                errors += f"Error for game '{game}': {str(e)}\n"

            self._log_output(output_folder, conversation, errors, generated_methods)

    def _extract_functions(self, response_text):
        """
        Naive function extraction - looks for 'def ' lines.
        Customize this for more robust function extraction.
        """
        methods = []
        lines = response_text.splitlines()
        current_func = []
        inside_func = False

        for line in lines:
            if line.strip().startswith("def "):
                if current_func:
                    methods.append("\n".join(current_func))
                current_func = [line]
                inside_func = True
            elif inside_func:
                current_func.append(line)

        if current_func:
            methods.append("\n".join(current_func))

        return methods
