from internal.services import ChatBotService
from fastapi import APIRouter, Path, Body
from internal.domains import Response
from typing import List
from pydantic import BaseModel


class DocIdsRequest(BaseModel):
    doc_ids: List[str] = []


class ChatbotHandler:
    def __init__(self, chatbot_service: ChatBotService):
        self.__chatbot_service = chatbot_service
        self.router = APIRouter()
        self.router.add_api_route(
            "/summary/{meeting_id}",
            self.summary_meeting,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/summary/file/{file_id}",
            self.summary_file,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/ask",
            self.ask,
            methods=["POST"]
        )

        self.router.add_api_route(
            "/ask-raw/",
            self.ask_,
            methods=["POST"]
        )

    def summary_meeting(
        self,
        project_id: str = Path(...),
        meeting_id: str = Path(...),
        body: DocIdsRequest = Body(),
    ):
        doc_ids = body.doc_ids
        try:
            data = self.__chatbot_service.summary_meeting(
                project_id, meeting_id, doc_ids)
            return Response(None, data)
        except Exception as e:
            return Response(e, None)

    def summary_file(
        self,
        project_id: str = Path(...),
        file_id: str = Path(...),
    ):
        try:
            data = self.__chatbot_service.summary_file(
                project_id, file_id)
            return Response(None, data)
        except Exception as e:
            return Response(e, None)

    def ask(self,
            project_id: str = Path(...),
            question: str = Body(),
            file_context: List[str] = Body(default=[]),
            meeting_context: List[str] = Body(default=[]),
            ):
        try:
            data = self.__chatbot_service.ask_with_rag(
                project_id, file_context, meeting_context)
            return Response(None, data)
        except Exception as e:
            return Response(e, None)

    def ask_(self,
             project_id: str = Path(...),
             question: str = Body(),
             file_context: List[str] = Body(default=[]),
             meeting_context: List[str] = Body(default=[]),
             ):
        try:
            data = self.__chatbot_service.ask_without_rag(
                project_id, file_context, meeting_context, question)
            return Response(None, data)
        except Exception as e:
            return Response(e, None)
