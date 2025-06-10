from openai import OpenAI


def get_api_key():
    # Load your OpenAI API key from an environment variable or a secure location
    with open("RePrompt/secret/openai-api-key.txt", "r") as file:
        api_key = file.read().strip()
        return api_key


client = OpenAI(api_key=get_api_key())

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant writing Python functions.",
        },
        {
            "role": "user",
            "content": "Write a Python function that returns the factorial of a number.",
        },
    ],
)

generated_code = response.choices[0].message.content
print("Generated Code:\n", generated_code)

grader = client.beta.graders.python.create(
    submission=generated_code,
    test="""
assert factorial(5) == 120
assert factorial(0) == 1
assert factorial(1) == 1
""",
)

print(grader.result)  # 'pass' or 'fail'
print(grader.logs)  # Test output, helpful for debugging failures
