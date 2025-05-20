from fastapi import APIRouter, Form, UploadFile, File, Path, Body, HTTPException
from internal.services import MeetingService
from internal.domains import Response
from pydantic import BaseModel


class SyncMeetingReq(BaseModel):
    meeting_id: str = ""
    call_id: str = ""
    token: str = ""


class MeetingHandler:
    def __init__(self, meeting_service: MeetingService):
        self.__meeting_service = meeting_service
        self.router = APIRouter()
        self.router.add_api_route(
            "/sync",
            self.sync_meeting_handler,
            methods=["POST"]
        )
        self.router.add_api_route(
            "/upload",
            self.upload_meeting,
            methods=["POST"]
        )
        self.router.add_api_route(
            "/{meeting_id}",
            self.delete_meeting_handler,
            methods=["DELETE"]
        )

    async def sync_meeting_handler(
        self,
        project_id: str = Path(...),
        req: SyncMeetingReq = Body(...),
    ):
        try:
            result = await self.__meeting_service.sync_meeting_with_get_data(
                project_id=project_id,
                meeting_id=req.meeting_id,
                token=req.token,
            )
            return Response(None, result)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    async def upload_meeting(
        self,
        project_id: str = Path(...),
        file: UploadFile = File(...),
        meeting_id: str = Form(...),
    ):
        try:
            result = await self.__meeting_service.sync_meeting(
                project_id=project_id,
                meeting_id=meeting_id,
                file=file,
            )
            return result
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    async def delete_meeting_handler(
        self,
        project_id: str = Path(...),
        meeting_id: str = Path(...)
    ):
        try:
            result = self.__meeting_service.delete_meeting(
                project_id=project_id,
                meeting_id=meeting_id
            )
            if result["status"] == "not_found":
                raise HTTPException(
                    status_code=404, detail="No meetings found")
            return Response(None, result)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
