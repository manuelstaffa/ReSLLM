from reprompt.parse_config import ConfigParser, get_active_config
from reprompt.prompt_llm import RewardPrompter
import tyro
from dataclasses import dataclass
from typing import Optional, Annotated, Literal


@dataclass
class Args:
    try:
        config: Annotated[str, tyro.conf.arg(aliases=["-c"])] = "default.toml"
        """Path to configuration TOML file."""
    except Exception:
        config: str = "default.toml"
        """Path to configuration TOML file."""

    model: Optional[Literal["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]] = None
    """OpenAI model to use."""

    temperature: Optional[float] = None
    """Temperature for sampling."""


def main():
    args = tyro.cli(Args)

    overrides = {
        "openai.model": args.model,
        "openai.temperature": args.temperature,
    }
    ConfigParser(path=args.config, overrides=overrides)
    config = get_active_config()

    games = config.get("env.games")
    if not games:
        raise ValueError("No games specified in the configuration.")
    if not isinstance(games, list):
        raise ValueError("The 'env.games' configuration must be a list of game names.")
    if not all(isinstance(game, str) for game in games):
        raise ValueError("All game names in 'env.games' must be strings.")

    for game in games:
        prompter = RewardPrompter(game=game)
        prompter.master_prompt()

    """print(f"Final Configuration: {config}")
    print(
        f"Using model: {config.get('openai.model')} with temperature: {config.get('openai.temperature')}"
    )

    print(f"Env: {config.get('env')}")
    print(f"Env: {config['env']}")

    context = {
        "game": config.get("env.game"),
        "model": config["openai"]["model"],
        "temperature": config["openai.temperature"],
    }
    prompt = config.format("prompt.template", context=context)
    print(f"Prompt with context: {prompt}")"""


if __name__ == "__main__":
    main()
