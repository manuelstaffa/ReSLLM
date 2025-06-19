# RePrompt

## Important Prompt Properties
- Prompt: explanation of the function name/return for the reward function 
- Prompt: do not to use undefined objects/variable
- Prompt: only provide full implementations of classes nd functions (not just header/definition)
- Prompt: do not to provide changes to game state
- Error prompt: only provide updated functions 


## Reward Shaping

| Symbol | Meaning |
|--------|---------|
| R(s,a,s') | Original reward function |
| R'(s,a,s') | Updated reward function |
| Φ | Potential function providing a measurement/immediate reward, maps state to number |
| y | Discount factor that determines how the immediate rewards influence the total reward |

- Potential-Based Reward Shaping (PBRS)
  - R'(s,a,s') = R(s,a,s') + γ * Φ(s') − Φ(s)
  - Include additional potential function that grades progress to goal in addition to reward function
  - E.g. distance function as potential function in addition to reward function that awards points 
  when reaching the end
  - Helps mitigate sparse rewards by adding incremental reward signals
  - Guides exploration in large environments where the agent may otherwise never/rarely receive a reward
  - Helps the RL algorithm to converge faster to effective policies
  - Policy Invariance: preserves optimal policy
- State-Action Potential-Based Shaping (PBRSA)
  - R'(s,a,s') = R(s,a,s') + γ * Φ(s',a') − Φ(s,a)
  - Generalization of standard PBRS that additionally incorporates actions into the potential function
  - Useful in environments where the action taken matters as much as the state
  - E.g. distance function as potential function if the player takes action to dodge an enemy attack in 
  addition to reward function that awards points when reaching the end
  - Helps mitigate sparse rewards by adding incremental reward signals
  - Guides exploration in large environments where the agent may otherwise never/rarely receive a reward
  and encourages agent to take tactical choices
  - Helps the RL algorithm to converge faster to effective policies
  - Policy Invariance: preserves optimal policy

| Symbol | Meaning |
|--------|---------|
| G(z) | Global reward for the full system configuration z |
| z_-i | Configuration without the contribution of agent i, or a default action for agent i |
| D_i(z) | Difference reward (how much better or worse the global reward is because of the action done by agent i) |
| i | Agent i in a multi-agent system |

- Difference Rewards (D)
  - D_i​(z) = G(z) − G(z_−i​)
  - Useful in multi-agent environments
  - Enables better credit assignment by showing the individual contribution of an agent
  - Reduces noise by removing the contribution of the actions of other agents
  - Encourages agent to work towards common goal, encouraging cooperation
  - No policy invariance: no guarantee that optimal individual behavior leads to globally optimal team behavior
  - High computational cost

| Symbol | Meaning |
|--------|---------|
| π(a\|s) | Agents original policy |
| A(s,a) | Advice function that encodes preferences for actions in states |
| β | Temperature/scaling factor how strong the advice is followed |
| e^(β * A(s,a)) | Converts advice into multiplicative weighting |

- Potential-Based Advice / Policy Shaping (PBA)
  - π'(a|s) ∝ π(a|s) * e^(β * A(s,a))
  - Encourages or discourages specific actions without forcing them
  - Provides external guidance that encourages exploration toward desirable behaviors
  - Soft influence: advice biases, but does not override the learned policy
  - No guarantee of policy invariance: suboptimal advice can degrade performance
  - E.g. advice function that returns whether a certain path is dangerous (-1) or safe (+1)
  - Can use LLM to generate A(s,a)

| Symbol | Meaning |
|--------|---------|
| R(s,a,s') | Original reward function |
| R'(s,a,s') | Updated reward function |
| H(s,a,s') | Heuristic reward as a manually defined function |

- Heuristic/Manual Reward Shaping
  - R'(s,a,s') = R(s,a,s') + H(s,a,s')
  - Accelerate learning by encouraging intermediate goals
  - Custom, manually created heuristic function designed with domain knowledge
  - Helps mitigate sparse rewards by adding incremental reward signals
  - No policy invariance guarantee: poorly designed heuristics can lead to suboptimal behavior
  - Biases agent’s behavior which may encourage shortcuts or unintended strategies

| Symbol | Meaning |
|--------|---------|
| R(s,a,s') | Original reward function |
| R'(s,a,s') | Updated reward function |
| f_θ(s,a,s') | Learned shaping reward, parameterized by θ (e.g. a neural network) |

- Learned Reward Shaping
  - R'(s,a,s') = R(s,a,s') + f_θ​(s,a,s')
  - Automatically encodes useful shaping information when manual reward shaping is hard
  - Useful in sparse reward environments, learning from demonstrations, or when there is no known optimal
  - Sources of Learned Reward Shaping
    - Inverse Reinforcement Learning (IRL): learn the entire reward function from expert demonstrations
    - Preference-Based Reward Learning: learn from human preferences
    - Auxiliary Models: use predictive models (e.g. predicting next state) to define progress-based shaping
    - LLM-Based Reward Models: use LLMs to generate or critique reward signals based on game descriptions or instructions
  - Helps mitigate sparse rewards by adding incremental reward signals
  - Automatically captures complex heuristics
  - No policy invariance guarantee: can lead to suboptimal policies if the learned shaping is incorrect
  - Requires data collection (e.g. demonstrations, instructions)
  - Can increase computational complexity

| Type | Function | Policy Invariance | Strength | Typical Use Case |
|------|----------|-------------------|----------|------------------|
| Potential-Based | R'(s,a,s') = R(s,a,s') + γ * Φ(s') − Φ(s) | yes | Safe, theoretically grounded | Navigation, planning tasks |
| State-Action PBRS | R'(s,a,s') = R(s,a,s') + γ * Φ(s',a') − Φ(s,a) | yes | More fine-grained guidance | Action-dependent environments |
| Difference Rewards | D_i​(z) = G(z) − G(z_−i​) | yes | Reduces credit assignment issues | Multi-agent RL |
| Policy Shaping | π'(a|s) ∝ π(a|s) * e^(β * A(s,a)) | no | Incorporates external advice | Human-in-the-loop RL, games |
| Heuristic Shaping | R'(s,a,s') = R(s,a,s') + H(s,a,s') | no | Fast, flexible, task-specific | Games, robotics, sparse rewards |
| Learned Shaping | R'(s,a,s') = R(s,a,s') + f_θ​(s,a,s') | no | Learns complex task structure | Imitation learning, preference RL |


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
