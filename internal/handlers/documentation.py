from fastapi import APIRouter, Form, UploadFile, File, Path, HTTPException
from internal.services import DocumentationService


class DocumentationHandler:
    def __init__(self, doc_service: DocumentationService):
        self.__doc_service = doc_service
        self.router = APIRouter()
        self.router.add_api_route(
            "/upload",
            self.upload_file_handler,
            methods=["POST"]
        )
        self.router.add_api_route(
            "/{file_id}",
            self.delete_file_handler,
            methods=["DELETE"]
        )

    async def upload_file_handler(
        self,
        project_id: str = Path(...),
        file: UploadFile = File(...),
        file_id: str = Form(...)
    ):
        try:
            result = await self.__doc_service.upload_file(
                project_id=project_id,
                file_id=file_id,
                file=file
            )
            return {
                "message": "Success",
                "project_id": project_id,
                "file_id": file_id,
                **result
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    async def delete_file_handler(
        self,
        project_id: str = Path(...),
        file_id: str = Path(...)
    ):
        try:
            result = self.__doc_service.delete_file(
                project_id=project_id,
                file_id=file_id
            )
            if result["status"] == "not_found":
                raise HTTPException(status_code=404, detail="No files found")
            return {
                "message": "Success",
                "project_id": project_id,
                "file_id": file_id,
                **result
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
