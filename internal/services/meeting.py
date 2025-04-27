from typing import List
from fastapi import UploadFile, HTTPException
from internal.adapters.chroma.repositories import MeetingRepo
import io


class MeetingService:
    def __init__(self, repo: MeetingRepo, embedding_model):
        self.__repo = repo
        self.__embedding_model = embedding_model

    async def sync_meeting(
        self,
        project_id: str,
        meeting_id: str,
        file: UploadFile
    ) -> dict:
        try:
            content = await file.read()
            if len(content) == 0:
                raise ValueError("Empty file")

            text = self._extract_text(file.filename, content)
            chunks = self._split_text(text)

            if not chunks:
                raise ValueError("Cannot split content")

            embeddings = self.__embedding_model.encode(
                chunks,
                normalize_embeddings=True
            ).tolist()

            self.__repo.sync_meeting(
                project_id=project_id,
                meeting_id=meeting_id,
                texts=chunks,
                embeddings=embeddings
            )

            return {
                "project_id": project_id,
                "meeting_id": meeting_id,
                "chunks": len(chunks),
                "status": "success"
            }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {str(e)}"
            )

    def delete_meeting(
        self,
        project_id: str,
        meeting_id: str
    ) -> dict:
        try:
            deleted_count = self.__repo.delete_by_meeting(
                project_id, meeting_id)

            return {
                "project_id": project_id,
                "meeting_id": meeting_id,
                "deleted_chunks": deleted_count,
                "status": "success" if deleted_count > 0 else "not_found"
            }

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
            raise ValueError(f"Error reading PDF: {str(e)}")

    def _split_text(self, text: str) -> List[str]:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n"]
        )
        return splitter.split_text(text)
