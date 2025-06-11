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

    overrides = {"model": args.model, "temperature": args.temperature}

    cfg = ConfigParser(path=args.config or None, overrides=overrides)

    print(f"Final Configuration: {cfg}")
    print(
        f"Using model: {cfg.get('openai_api.model')} with temperature: {cfg.get('openai_api.temperature')}"
    )

    context = {
        "game": "Freeway",
        "model": cfg.get("openai_api.model"),
        "temperature": cfg.get("openai_api.temperature"),
    }
    prompt = cfg.format("prompt.template", context=context)
    print(f"Prompt with context: {prompt}")


if __name__ == "__main__":
    main()
