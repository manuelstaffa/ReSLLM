from reprompt.parse_config import ConfigParser, get_active_config
import tyro
from dataclasses import dataclass
from typing import Optional, Annotated, Literal


@dataclass
class Args:
    config: Annotated[str, tyro.conf.arg(aliases=["-c"])] = "default.json"
    """Path to configuration JSON file."""

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
    # set_active_config(config)
    config = get_active_config()

    print(f"Final Configuration: {config}")
    print(
        f"Using model: {config.get('openai.model')} with temperature: {config.get('openai.temperature')}"
    )

    print(f"Env: {config.get('env')}")
    print(f"Env: {config["env"]}")

    context = {
        "game": config.get("env.game"),
        "model": config["openai"]["model"],
        "temperature": config["openai.temperature"],
    }
    prompt = config.format("prompt.template", context=context)
    print(f"Prompt with context: {prompt}")


if __name__ == "__main__":
    main()
