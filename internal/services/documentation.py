from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from typing import List
from fastapi import UploadFile, HTTPException
from internal.adapters.chroma.repositories import DocumentationRepo
import io
from internal.domains import File
import aiohttp
from tempfile import SpooledTemporaryFile


class DocumentationService:
    def __init__(self,
                 repo: DocumentationRepo,
                 embedding_model):
        self.__repo = repo
        self.__embedding_model = embedding_model

    async def upload_file(
        self,
        project_id: str,
        file: File,
    ) -> dict:
        try:
            content = await file.file.read()
            if len(content) == 0:
                raise ValueError("Empy file")

            text = self._extract_text(file.file_name, content)
            chunks = self._split_text(text)

            if not chunks:
                raise ValueError("Cannot split file")

            embeddings = self.__embedding_model.encode(
                chunks,
                normalize_embeddings=True
            ).tolist()

            self.__repo.add_documents(
                project_id=project_id,
                file_id=file.file_id,
                file_name=file.file_name,
                texts=chunks,
                embeddings=embeddings
            )

            return {
                "project_id": project_id,
                "file_id": file.file_id,
                "file_name": file.file_name,
                "chunks": len(chunks),
                "status": "success"
            }

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {str(e)}"
            )

    async def sync_file(self, project_id: str, file: File):
        async with aiohttp.ClientSession() as session:
            async with session.get(file.file_url) as resp:
                if resp.status == 200:
                    temp = SpooledTemporaryFile()
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        temp.write(chunk)
                    temp.seek(0)

                    file.file = UploadFile(file=temp)
                    return file
                else:
                    raise Exception(f"Không tải được file từ {file.file_url}")

    def delete_file(
        self,
        project_id: str,
        file_id: str
    ) -> dict:
        try:
            deleted_count = self.__repo.delete_by_file(project_id, file_id)
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
            query_embedding = self.__embedding_model.encode([query_text])[0]

            results = self.__repo.query(
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
            return self.__repo.get_file_documents(project_id, file_id)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error: {str(e)}"
            )

    def _extract_text(self, filename: str, content: bytes) -> str:
        return self._extract_pdf(content)

    def _extract_pdf(self, content: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(content))
            return "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")

    def _split_text(self, text: str) -> List[str]:

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)
