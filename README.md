# RePrompt

## Important Prompt Properties
- Explain the function shape
- Explain not to use undefined objects/variable
- Explain to only provide full implementations
- Explain not to provide changes to game state


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

## Config Parser

Config Parser for RePrompt.

Access config:  
```python
from reprompt.parse_config import ConfigParser

overrides = {
    "<key>": <value>,
}
ConfigParser(path=args.config, overrides=overrides)  
config = get_active_config()  
```

Access config values:  
```python
from reprompt.parse_config import get_active_config

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
