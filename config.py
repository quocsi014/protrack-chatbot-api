import os
from dotenv import load_dotenv


class AppConfig:
    def __init__(self):
        load_dotenv()

        # Chroma config
        self.CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
        self.CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8081))
        self.CHROMA_PASSWD = os.getenv("CHROMA_PASSWD", "admin")

        # OpenRouter config
        self.OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
        self.OPENROUTER_MODEL = os.getenv(
            "OPENROUTER_MODEL", "deepseek/deepseek-r1-zero:free")
        self.OPENROUTER_CHAT_ENDPOINT = os.getenv(
            "OPENROUTER_CHAT_ENDPOINT",
            "https://openrouter.ai/api/v1/chat/completions"
        )

        # PostgreSQL config
        # self.PSQL_HOST = os.getenv("PSQL_HOST", "localhost")
        # self.PSQL_PORT = int(os.getenv("PSQL_PORT", 5432))
        # self.PSQL_USER = os.getenv("PSQL_USER", "postgres")
        # self.PSQL_PSSWD = os.getenv("PSQL_PSSWD", "postgres")
        # self.PSQL_DB = os.getenv("PSQL_DB", "your_db_name")  # nếu có tên DB

        self.AUTH_JWT_SECRET = os.getenv("AUTH_JWT_SECRET")

        self.PROTRACK_URL = os.getenv("PROTRACK_URL", "http://localhost:4000/")

        self.STREAM_TOKEN = os.getenv("STREAM_TOKEN", "yy2fqqc4zd6p")
