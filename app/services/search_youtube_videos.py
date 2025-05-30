from openai import OpenAI
import os

client = OpenAI(base_url="https://api.metisai.ir/openai/v1", api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4.1",
    tools=[{ "type": "web_search_preview" }],
    input="What was a positive news story from today?",
)

print(response)