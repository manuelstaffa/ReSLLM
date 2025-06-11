# RePrompt

## Structure
---

```bash
RePrompt
├── context
│   ├── config
│   │   ├── default.json
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
│           ├── log.txt
│           ├── conversation_history.json
│           ├── config.json
│           └── <game>_reward.py
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