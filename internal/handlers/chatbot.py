from internal.services import ChatBotService
from fastapi import APIRouter, Path


class ChatbotHandler:
    def __init__(self, chatbot_service: ChatBotService):
        self.__chatbot_service = chatbot_service
        self.router = APIRouter()
        self.router.add_api_route(
            "/summary/{meeting_id}",
            self.summary_meeting,
            methods=["POST"]
        )

    def summary_meeting(
        self,
        project_id: str = Path(...),
        meeting_id: str = Path(...)
    ):
        return self.__chatbot_service.summary_meeting(project_id, meeting_id)
