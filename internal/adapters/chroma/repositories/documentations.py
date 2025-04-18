import uuid
from chromadb import HttpClient
from typing import List
from internal.domains import File


class DocumentationRepo:
    def __init__(self, client: HttpClient):
        self.__client = client
        self.__collection = self.__client.get_or_create_collection(
            name="docs",
            embedding_function=None
        )

    def add_documents(
        self,
        project_id: str,
        file_id: str,
        file_name: str,
        texts: List[str],
        embeddings: List[List[float]]
    ):
        metadatas = [{
            "source": "user_upload",
            "project_id": project_id,
            "file_id": file_id,
            "file_name": file_name,
        } for _ in texts]

        ids = [f"{project_id}-{file_id}-{uuid.uuid4()}" for _ in texts]

        self.__collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def delete_by_file(self, project_id: str, file_id: str) -> int:
        results = self.__collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"file_id": {"$eq": file_id}}
                ]
            }
        )

        if not results["ids"]:
            return 0

        self.__collection.delete(ids=results["ids"])
        return len(results["ids"])

    def get_file_document(self, project_id: str, file_id: str) -> File:
        results = self.__collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"file_id": {"$eq": file_id}}
                ]
            }
        )
        return File(file_id=file_id,
                    file_name=results.get("metadatas", [{}])[
                        0].get("file_name"),
                    contents=results.get("documents", []),)

    def get_file_documents(self, project_id: str,
                           file_ids: List[str]) -> List[str]:
        results = self.__collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"file_id": {"$in": file_ids}}
                ]
            }
        )
        return results.get("documents", [])

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

    def query(
        self,
        project_id: str,
        file_ids: List[str],
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[str]:
        where_clause = {"project_id": {"$eq": project_id}}

        if file_ids and file_ids.__len__ > 0:
            where_clause["file_id"] = {"$in": file_ids}

        results = self.__collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "distances", "metadatas"]
        )

        # min_distance = 1.5
        filtered = [
            doc for doc, dist in zip(results["documents"][0],
                                     results["distances"][0])
            # if dist < min_distance
        ]

        return filtered[:top_k]
