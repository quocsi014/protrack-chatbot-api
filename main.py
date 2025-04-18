import uvicorn
from config import AppConfig
import os
import sys
from sentence_transformers import SentenceTransformer
from chromadb import HttpClient
from internal.adapters.chroma.repositories import (
    DocumentationRepo, MeetingRepo)
from internal.adapters.open_router import OpenRouterClient
from fastapi import (
    FastAPI, APIRouter)
from fastapi.middleware.cors import CORSMiddleware
from internal.services import (
    DocumentationService, ChatBotService, MeetingService)
from internal.handlers import (
    DocumentationHandler, MeetingHandler, ChatbotHandler)

sys.path.append(os.path.dirname(__file__))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load config
cfg = AppConfig()

# dependency setup
chromaClient = HttpClient(
    host=cfg.CHROMA_HOST,
    port=cfg.CHROMA_PORT,
    headers={"X-Chroma-Token": cfg.CHROMA_PASSWD}
)

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# repositories
doc_repo = DocumentationRepo(chromaClient)
meeting_repo = MeetingRepo(chromaClient)

# clients
open_router_client = OpenRouterClient(cfg)

# services
doc_service = DocumentationService(doc_repo, model)
chatbot_service = ChatBotService(
    doc_repo, meeting_repo, open_router_client, model)
meeting_service = MeetingService(meeting_repo, model)

# handlers
doc_handler = DocumentationHandler(doc_service)
meeting_handler = MeetingHandler(meeting_service)
chatbot_handler = ChatbotHandler(chatbot_service)

v1_router = APIRouter(prefix="/chatbot/api/v1/{project_id}")

v1_router.include_router(doc_handler.router, prefix="/docs")
v1_router.include_router(meeting_handler.router, prefix="/meetings")
v1_router.include_router(chatbot_handler.router, prefix="/chat")

app.include_router(v1_router)
