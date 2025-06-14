# RePrompt

## Structure

General file structure of RePrompt.

```bash
RePrompt
├── context
│   ├── config
│   │   ├── default.toml
│   │   └── default.yaml
│   ├── game_objects.py
│   └── games
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
│   ├── build_prompt.py
│   ├── prompt_llm.py
│   ├── test_grader.py
│   └── test_response.py
├── secret
│   └── openai-api-key.txt
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
ConfigParser(path=args.config, overrides=overrides)  
config = get_active_config()  
```

Access config values:  
```python
config.get('<category>')  
config.get('<category>.<value>')  
# config['<category>']
# config["<category>"]["<value>"]
# config["<category>.<value>"]
```

Custom format:
```python
context = {
    "<key>": <value>,
}
prompt = config.format("<fstring as string>", context=context)
```
