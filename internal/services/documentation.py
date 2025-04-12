from typing import List
from fastapi import UploadFile, HTTPException
from internal.adapters.chroma.repositories import DocumentationRepo
import io


class DocumentationService:
    def __init__(self, repo: DocumentationRepo, embedding_model):
        self.repo = repo
        self.embedding_model = embedding_model

    async def upload_file(
        self,
        project_id: str,
        file_id: str,
        file: UploadFile
    ) -> dict:
        try:
            content = await file.read()
            if len(content) == 0:
                raise ValueError("Empy file")

            text = self._extract_text(file.filename, content)
            chunks = self._split_text(text)

            if not chunks:
                raise ValueError("Cannot split file")

            embeddings = self.embedding_model.encode(chunks).tolist()

            self.repo.add_documents(
                project_id=project_id,
                file_id=file_id,
                texts=chunks,
                embeddings=embeddings
            )

            return {
                "project_id": project_id,
                "file_id": file_id,
                "chunks": len(chunks),
                "status": "success"
            }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {str(e)}"
            )

    def delete_file(
        self,
        project_id: str,
        file_id: str
    ) -> dict:
        try:
            deleted_count = self.repo.delete_by_file(project_id, file_id)
            return {
                "project_id": project_id,
                "file_id": file_id,
                "deleted_chunks": deleted_count,
                "status": "success" if deleted_count > 0 else "not_found"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error: {str(e)}"
            )

    def query_documents(
        self,
        project_id: str,
        query_text: str,
        top_k: int = 3
    ) -> List[str]:
        try:
            query_embedding = self.embedding_model.encode([query_text])[0]

            results = self.repo.query(
                project_id=project_id,
                query_embedding=query_embedding,
                top_k=top_k
            )

            return results

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error: {str(e)}"
            )

    def get_file_content(
        self,
        project_id: str,
        file_id: str
    ) -> List[str]:
        try:
            return self.repo.get_file_documents(project_id, file_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error: {str(e)}"
            )

    def _extract_text(self, filename: str, content: bytes) -> str:
        if filename.endswith(".pdf"):
            return self._extract_pdf(content)
        elif filename.endswith(".txt"):
            return content.decode("utf-8")
        else:
            raise ValueError("Invalid file")

    def _extract_pdf(self, content: bytes) -> str:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content))
            return "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def _split_text(self, text: str) -> List[str]:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
