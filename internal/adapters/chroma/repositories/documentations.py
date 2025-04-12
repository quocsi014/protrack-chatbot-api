import uuid
from chromadb import HttpClient
from typing import List


class DocumentationRepo:
    def __init__(self, client: HttpClient):
        self.client = client
        self.collection = self.client.get_or_create_collection(
            name="docs",
            embedding_function=None
        )

    def add_documents(
        self,
        project_id: str,
        file_id: str,
        texts: List[str],
        embeddings: List[List[float]]
    ):
        metadatas = [{
            "source": "user_upload",
            "project_id": project_id,
            "file_id": file_id
        } for _ in texts]

        ids = [f"{project_id}-{file_id}-{uuid.uuid4()}" for _ in texts]

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def delete_by_file(self, project_id: str, file_id: str) -> int:
        results = self.collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"file_id": {"$eq": file_id}}
                ]
            }
        )

        if not results["ids"]:
            return 0

        self.collection.delete(ids=results["ids"])
        return len(results["ids"])

    def get_file_documents(self, project_id: str, file_id: str) -> List[str]:
        results = self.collection.get(
            where={
                "$and": [
                    {"project_id": {"$eq": project_id}},
                    {"file_id": {"$eq": file_id}}
                ]
            }
        )
        return results.get("documents", [])

    def query(
        self,
        project_id: str,
        query_embedding: List[float],
        top_k: int = 3
    ) -> List[str]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"project_id": {"$eq": project_id}},
            include=["documents", "distances", "metadatas"]  # Thêm metadata
        )

        min_distance = 1.5
        filtered = [
            doc for doc, dist in zip(results["documents"][0], results["distances"][0])
            # if dist < min_distance
        ]

        return filtered[:top_k]
