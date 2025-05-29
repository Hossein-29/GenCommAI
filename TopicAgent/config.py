from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
class Settings(BaseSettings):
    OPENAI_API_KEY: str

load_dotenv()

# settings = Settings(OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"))
settings = Settings(OPENAI_API_KEY="tpsg-Y8I6IHw7blcJfxShj2do6iRk4r9Jzdb")