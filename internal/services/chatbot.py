from internal.adapters.chroma.repositories import (
    DocumentationRepo, MeetingRepo
)
from internal.adapters.open_router import OpenRouterClient
from typing import List
from internal.domains import Answer, ErrSomethingWentWrong
import logging


class ChatBotService:
    def __init__(self,
                 doc_repo: DocumentationRepo,
                 meeting_repo: MeetingRepo,
                 open_router_client: OpenRouterClient,
                 embedding_model,
                 ):
        self.__doc_repo = doc_repo
        self.__meeting_repo = meeting_repo
        self.__open_router_client = open_router_client
        self.__embedding_model = embedding_model

    def summary_file(self, project_id: str, file_id: str, locale: str = "en") -> Answer:
        file = self.__doc_repo.get_file_document(project_id, file_id)
        return self.__open_router_client.summary_content(file.contents, locale=locale)

    def summary_meeting(self,
                        project_id: str,
                        meeting_id: str,
                        file_ids: List[str] = None,
                        locale: str = "en",
                        ) -> Answer:
        meeting_contents = self.__meeting_repo.get_meeting_content(
            project_id=project_id,
            meeting_id=meeting_id,
        )

        files = []
        for id in file_ids:
            files.append(self.__doc_repo.get_file_document(project_id, id))

        try:
            return self.__open_router_client.summary_content(meeting_contents,
                                                             files,
                                                             locale=locale,
                                                             is_meeting=True)
        except Exception as e:
            logging.error(
                "ChatBotService OpenRouterClient.SummaryContent Error: %s", e)
            raise ErrSomethingWentWrong

    def ask_with_rag(self,
                     project_id: str,
                     file_ids: List[str] = [],
                     meeting_ids: List[str] = [],
                     question: str = "",
                     ):

        query_embedding = self.__embedding_model.encode([question])[0]
        meeting_ids, file_ids = []
        if len(file_ids) > 0:
            file_content = self.__doc_repo.query(
                project_id=project_id,
                file_ids=file_ids,
                query_embedding=query_embedding,
            )

        if len(meeting_ids) > 0:
            meeting_content = self.__meeting_repo.query(
                project_id=project_id,
                file_ids=file_ids,
                query_embedding=query_embedding,
            )

        return self.__open_router_client.ask(question, file_content, meeting_content)

    def ask_without_rag(self,
                        project_id: str,
                        file_ids: List[str] = [],
                        meeting_ids: List[str] = [],
                        question: str = "",
                        ):

        file_content = []
        meeting_content = []

        for id in file_ids:
            file_ids += self.__doc_repo.get_file_document(
                project_id, id).contents
        for id in meeting_ids:
            meeting_content += self.__meeting_repo.get_meeting_content(
                project_id, id)

        return self.__open_router_client.ask(question, file_content, meeting_content)
