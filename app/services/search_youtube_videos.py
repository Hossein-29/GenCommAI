from openai import OpenAI
from pydantic import BaseModel
import os

client = OpenAI(base_url="https://api.metisai.ir/openai/v1", api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4.1-mini",
    tools=[{ "type": "web_search_preview" }],
    input="Find youtube videos about the following product give the results as a json list of youtube urls containing only:\niphone 16 pro max 256 gb",
)

print(response.output_text)