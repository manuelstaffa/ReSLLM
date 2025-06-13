def test_config():
    from reprompt.parse_config import get_active_config

    active_config = get_active_config()

    print(f"Active Config test: {active_config}")
