import uuid
from chromadb import HttpClient
from typing import List


class MeetingRepo:
    def __init__(self, client: HttpClient):
        self.__client = client
        self.__collection = self.__client.get_or_create_collection(
            name="meetings",
            embedding_function=None
        )

    def sync_meeting(
        self,
        project_id: str,
        meeting_id: str,
        texts: List[str],
        embeddings: List[List[float]]
    ):
        metadatas = [{
            "source": "user_upload",
            "project_id": project_id,
            "meeting_id": meeting_id
        } for _ in texts]

        ids = [f"{project_id}-{meeting_id}-{uuid.uuid4()}" for _ in texts]

        self.delete_by_meeting(project_id, meeting_id)

        self.__collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def delete_by_meeting(self, project_id: str, meeting_id: str) -> int:
        results = self.__collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"meeting_id": {"$eq": meeting_id}}
                ]
            }
        )

        if not results["ids"]:
            return 0

        self.__collection.delete(ids=results["ids"])
        return len(results["ids"])

    def get_meeting_content(self,
                            project_id: str,
                            meeting_id: str
                            ) -> List[str]:
        results = self.__collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"meeting_id": {"$eq": meeting_id}}
                ]
            }
        )
        return results.get("documents", [])
