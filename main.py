from typing import Optional
from fastapi import Form, FastAPI, UploadFile, File, Path, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from internal.services import DocumentationService
from internal.adapters.chroma.repositories import DocumentationRepo
from chromadb import HttpClient
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import sys
import os
from config import AppConfig

sys.path.append(os.path.dirname(__file__))
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load config
cfg = AppConfig()

# dependency setup
chromaClient = HttpClient(
    host=cfg.CHROMA_HOST,
    port=cfg.CHROMA_PORT,
    headers={"X-Chroma-Token": cfg.CHROMA_PASSWD}
)

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

docRepo = DocumentationRepo(chromaClient)
docService = DocumentationService(docRepo, model)


@app.post("/chatbot/{project_id}/files/upload")
async def upload_file_handler(
    project_id: str = Path(...),
    file: UploadFile = File(...),
    file_id: str = Form(...)
):
    try:
        result = await docService.upload_file(
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
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@app.delete("/chatbot/{project_id}/files/{file_id}")
async def delete_file_handler(
    project_id: str = Path(...),
    file_id: str = Path(...)
):
    try:
        result = docService.delete_file(
            project_id=project_id,
            file_id=file_id
        )

        if result["status"] == "not_found":
            raise HTTPException(
                status_code=404,
                detail="No files found"
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
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


class QueryRequest(BaseModel):
    query_text: str
    top_k: Optional[int] = 3


@app.post("/chatbot/{project_id}/query")
async def query_documents_handler(
    project_id: str = Path(...),
    request: QueryRequest = ...
):
    try:
        results = docService.query_documents(
            project_id=project_id,
            query_text=request.query_text,
            top_k=request.top_k
        )

        return {
            "project_id": project_id,
            "query": request.query_text,
            "results": results
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


@app.get("/chatbot/{project_id}/files/{file_id}")
async def get_file_content_handler(
    project_id: str = Path(...),
    file_id: str = Path(...)
):
    try:
        documents = docService.get_file_content(project_id, file_id)

        return {
            "project_id": project_id,
            "file_id": file_id,
            "documents": documents,
            "count": len(documents)
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
