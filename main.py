from reprompt.parse_config import ConfigParser, get_active_config
from reprompt.prompt_llm import RewardPrompter
from reprompt.utils import read_file
import tyro
from dataclasses import dataclass
from typing import Optional, Annotated, Literal


@dataclass
class Args:
    try:
        config: Annotated[str, tyro.conf.arg(aliases=["-c"])] = "default.toml"  # type: ignore
        """Path to configuration TOML file."""
    except Exception:
        config: str = "default.toml"
        """Path to configuration TOML file."""

    model: Optional[Literal["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]] = None
    """OpenAI model to use."""

    temperature: Optional[float] = None
    """Temperature for sampling."""

    seed: Optional[int] = None
    """Seed for random number generation."""


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
        context = {
            "game": game,
            "model": config.get("openai.model"),
            "temperature": config.get("openai.temperature"),
            "seed": config.get("seed"),
            "parent_objects": read_file("context/games/game_objects.py"),
            "game_objects": read_file(f"context/games/{game}/game_objects.py"),
            "ram_extraction": read_file(f"context/games/{game}/{game}.py"),
            "game_description": read_file(f"context/games/{game}/game_description.txt"),
            "game_description_long": read_file(
                f"context/games/{game}/game_description_long.txt"
            ),
        }

        prompter = RewardPrompter(
            config=config, game=game, context=context, seed=args.seed
        )
        prompter.master_prompt()


if __name__ == "__main__":
    main()
