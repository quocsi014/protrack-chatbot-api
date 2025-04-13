import os
from dotenv import load_dotenv


class AppConfig:
    def __init__(self):
        load_dotenv()

        self.CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
        self.CHROMA_PORT = int(
            os.getenv("CHROMA_PORT", 8081))
        self.CHROMA_PASSWD = os.getenv("CHROMA_PASSWD", "admin")

        self.OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
        self.OPENROUTER_MODEL = os.getenv(
            "OPENROUTER_MODEL", "deepseek/deepseek-r1-zero:free")
        self.OPENROUTER_CHAT_ENDPOINT = os.getenv(
            "OPENROUTER_CHAT_ENDPOINT",
            "https://openrouter.ai/api/v1/chat/completions")
