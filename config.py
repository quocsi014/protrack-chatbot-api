import os
from dotenv import load_dotenv


class AppConfig:
    def __init__(self):
        load_dotenv()

        self.CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
        self.CHROMA_PORT = int(
            os.getenv("CHROMA_PORT", 8081))
        self.CHROMA_PASSWD = os.getenv("CHROMA_PASSWD", "admin")
