from typing import List
from fastapi import UploadFile, HTTPException
from internal.adapters.chroma.repositories import MeetingRepo
from internal.adapters.psql.repositories import MeetingRepo as PMeetingRepo
import io
import aiohttp
from io import BytesIO
from config import AppConfig


class MeetingService:
    def __init__(self, repo: MeetingRepo, embedding_model, pRepo: PMeetingRepo, cfg: AppConfig):
        self.__repo = repo
        self.__embedding_model = embedding_model
        self.__prepo = pRepo
        self.__cfg = cfg

    async def sync_meeting_with_get_data(
        self,
        project_id: str,
        meeting_id: str,
    ) -> dict:
        try:

            meeting = self.__prepo.get_meeting(meeting_id)
            call_id = meeting.call_id
            if not call_id:
                raise ValueError("Missing call_id in meeting")

            transcription_api = f"https://chat.stream-io-api.com/video/call/default/{call_id}/transcriptions?api_key=9wageyvh7sus"
            headers = {
                "accept": "application/json",
                "Authorization": self.__cfg.STREAM_TOKEN,
                "Stream-Auth-Type": "jwt",
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(transcription_api) as resp:
                    if resp.status != 200:
                        raise ValueError(
                            f"Cannot fetch transcriptions: {resp.status}")
                    transcription_data = await resp.json()

                full_content = ""
                for t in transcription_data.get("transcriptions", []):
                    url = t.get("url")
                    if not url:
                        continue

                    async with session.get(url) as file_resp:
                        if file_resp.status != 200:
                            print(f"Failed to fetch {url}")
                            continue
                        text = await file_resp.text()
                        full_content += text.strip() + "\n"

            if not full_content:
                raise ValueError("No transcription content fetched")

            full_content = "Description:\n" + (
                meeting.des or "") + "\n" + full_content
            fake_file = UploadFile(
                filename="merged_transcript.txt",
                file=BytesIO(full_content.encode("utf-8"))
            )

            return await self.sync_meeting(
                project_id=project_id,
                meeting_id=meeting_id,
                file=fake_file
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Sync from stream failed: {str(e)}"
            )

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
