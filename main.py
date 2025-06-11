import argparse
from reprompt.parse_config import ConfigParser


def main():
    parser = argparse.ArgumentParser(
        description="Generate reward functions using OpenAI API."
    )
    parser.add_argument(
        "-c", "--config", type=str, help="Path to configuration JSON file."
    )
    parser.add_argument("--model", type=str, help="OpenAI model to use.")
    parser.add_argument("--temperature", type=float, help="Temperature for sampling.")

    args = parser.parse_args()

    overrides = {"openai.model": args.model, "openai.temperature": args.temperature}
    config = ConfigParser(path=args.config or None, overrides=overrides)

    print(f"Final Configuration: {config}")
    print(
        f"Using model: {config.get('openai.model')} with temperature: {config.get('openai.temperature')}"
    )

    print(f"Env: {config.get('env')}")

    context = {
        "game": config.get("env.game"),
        "model": config["openai"]["temperature"],
        "temperature": config["openai.temperature"],
    }
    prompt = config.format("prompt.template", context=context)
    print(f"Prompt with context: {prompt}")


if __name__ == "__main__":
    main()
