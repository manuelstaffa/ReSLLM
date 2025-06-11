import argparse
from reprompt.parse_config import ConfigParser


def main():
    parser = argparse.ArgumentParser(
        description="Generate reward functions using OpenAI API."
    )
    parser.add_argument("--config", type=str, help="Path to configuration JSON file.")
    parser.add_argument("--model", type=str, help="Override the model in config.")
    args = parser.parse_args()

    overrides = {"model": args.model}
    cfg = ConfigParser(path=args.config or None, overrides=overrides)

    print("Final Configuration:")
    print(cfg)

    # Example usage:
    print("Using model:", cfg.get("openai_api.model"))


if __name__ == "__main__":
    main()
