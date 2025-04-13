from internal.adapters.chroma.repositories import (
    DocumentationRepo, MeetingRepo
)
from internal.adapters.open_router import OpenRouterClient
from typing import List


class ChatBotService:
    def __init__(self,
                 doc_repo: DocumentationRepo,
                 meeting_repo: MeetingRepo,
                 open_router_client: OpenRouterClient
                 ):
        self.__doc_repo = doc_repo
        self.__meeting_repo = meeting_repo
        self.__open_router_client = open_router_client

    def summary_file():
        pass

    def summary_meeting(self,
                        project_id: str,
                        meeting_id: str,
                        file_ids: List[str] = None,
                        ):
        meeting_contents = self.__meeting_repo.get_meeting_content(
            project_id=project_id,
            meeting_id=meeting_id,
        )

        return self.__open_router_client.summary_content(meeting_contents,
                                                         is_meeting=True)
