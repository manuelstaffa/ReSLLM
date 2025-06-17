# RePrompt

## Important Prompt Properties
- Prompt: explannation of the function name/return for the reward function 
- Prompt: do not to use undefined objects/variable
- Prompt: only provide full implementations of classes nd functions (not just header/definition)
- Prompt: do not to provide changes to game state
- Error prompt: only provide updated functions 


## Current prompt format placeholders

```toml
text = """This is a prompt for {game} with model {model}"""
```

Current placeholder options
| Name | Value |
|------|-------|
| `{game}` | Current game the reward function is generated for |
| `{model}` | Current OpenAI model |
| `{temperature}` | Temperature to generate answers |
| `{parent_object}` | Game object template with properties and functions |
| `{game_objects}` | Game-specific objects |
| `{ram_extraction}` | OC_Atari ram extraction |
| `{game_description}` | Textual game description |
| `{game_description_long}` | Long textual game description |

Additional placeholders for the error prompt

| Name | Value |
|------|-------|
| `{error_message}` | The error trace of the error to fix, including the function code |
| `{function_name}` | The name of the function where the error occurred |


## Structure

General file structure of RePrompt.

```bash
RePrompt
├── context
│   ├── config
│   │   └── <config>.toml
│   └── games
│       ├── game_objects.py
│       └── <game>
│           ├── game_description.txt
│           ├── game_objects.py
│           └── <game>.py
├── out
│   └── <game>
│       └── <run>
│           ├── errors.txt
│           ├── conversation.txt
│           ├── config.toml
│           └── reward_function.py
├── reprompt
│   ├── parse_config.py
│   ├── prompt_llm.py
│   └── utils.py
├── secret
│   └── openai-api-key
├── main.py
├── requirements.txt
└── README.md
```

## Command Line Arguments

Specified in <config_name>.toml, with applicable overrides specified below.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `` | type | `<content>` | use |
| `--config` `-c` | str | `<config name, filename, or path (default: default.toml)>` | Name of the config file to use |
| `--model` | str | `<openai model (gpt-4o, gpt-4-turbo, gpt-4, gpt-3.5-turbo)>` | The OpenAI model to use |
| `--clear` | none | `<none>` | Flag to clear previous runs for the same game with the same config |

## Config Parser

Config Parser for RePrompt.

Create config parser:  
```python
from reprompt.parse_config import ConfigParser

overrides = {
    "<key>": <value>,
}
ConfigParser(path=args.config, overrides=overrides)  
```

Access config values:  
```python
from reprompt.parse_config import get_active_config

config = get_active_config

config.get('<category>')  
config.get('<category>.<value>')  
# config['<category>']
# config["<category>"]["<value>"]
# config["<category>.<value>"]
```

Custom string formatter:
```python
from reprompt.utils import format_string

context = {
    "<key>": <value>,
}
prompt = format_string("<string with {key}>", context=context)
```
