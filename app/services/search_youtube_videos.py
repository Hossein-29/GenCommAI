from openai import OpenAI
from pydantic import BaseModel
import os

client = OpenAI(base_url="https://api.metisai.ir/openai/v1", api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-4.1-mini",
    tools=[{ "type": "web_search_preview" }],
    input="""
        Find YouTube videos about the following product and return the results as a JSON list of YouTube URLs. Each URL should be a string and the JSON object should only contain the URLs of videos that are related to "iphone 16 pro max 256 gb". The output should be structured like this:

        {
        "videos": [
            "https://www.youtube.com/watch?v=video_id_1",
            "https://www.youtube.com/watch?v=video_id_2",
            "https://www.youtube.com/watch?v=video_id_3"
        ]
        }

        """,
)

print(response.output_text)