from __future__ import annotations
from typing import Union
from pathlib import Path
import base64, json
import io
from PIL import Image
import httpx
from .base import Agent
from .config import settings
from openai import OpenAI


_JSON_SIG = """You are a product expert. Extract brand and model. You Only use latin.
Return ONLY valid JSON exactly with keys `brand` and `model` in lowercase Latin letters.
If unknown, output {"brand": null, "model": null}."""

class ProductClassifierAgent(Agent):
    name = "product-identifier"

    def run(self, inp: Union[str, Path, Image.Image]):
        if isinstance(inp, (str, Path)) and Path(inp).suffix:
            img = Image.open(inp)
            content = self._img2b64(img)
            mode = "image"
        elif isinstance(inp, Image.Image):
            content = self._img2b64(inp)
            mode = "image"
        else:
            content = str(inp)
            mode = "text"

        payload = self._build_payload(content, mode)
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url="https://api.metisai.ir/openai/v1"
        )
        # Use the OpenAI client for chat completion (sync)
        response = client.chat.completions.create(**payload)
        msg = response.choices[0].message.content.strip()
        try:
            js = json.loads(msg)
            if js.get("brand") and js.get("model"):
                return f"{js['brand']}-{js['model']}"
        except json.JSONDecodeError:
            pass
        return None
    @staticmethod
    def _img2b64(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode()

    @staticmethod
    def _build_payload(content: str, mode: str):
        if mode == "text":
            return {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": _JSON_SIG},
                    {"role": "user", "content": content},
                ],
                "temperature": 0,
            }
        # vision
        return {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": _JSON_SIG},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{content}",
                            },
                        },
                        {"type": "text", "text": "write the exact model of the product in this format"
                        "brand: <model_name>"},
                    ],
                },
            ],
            "temperature": 0,
        }
    
if __name__ == "__main__":
    def main():
        agent = ProductClassifierAgent()
        brand_model = agent.run("مانیتور ال جی یو پی پنجاه و پنج یو ان بیست و هفت اینچ")  
        print(brand_model)
        brand_model = agent.run("ایسوس ویوو بوک ۱۵ ")
        print(brand_model)
        # brand_model = agent.run("/Users/roham/Documents/Projects/LLmHackathon/app/agent/tmp/macbookAIR.jpg")
        # print(brand_model)
        # brand_model = agent.run("/Users/roham/Documents/Projects/LLmHackathon/app/agent/tmp/macbookPro.jpg")
        # print(brand_model)

    main()