import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PERPLEXITY_API_KEY")
print(f"API Key loaded: {api_key[:10]}..." if api_key else "API Key NOT found!")

client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

response = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Hello, Perplexity!"}]
)

print(response.choices[0].message.content)