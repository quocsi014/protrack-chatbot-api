from fastapi import Request, responses
from internal.adapters.psql.repositories import ProjectRepo
from internal.helpers import jwt
from config import AppConfig


class AuthMiddleware:
    def __init__(self, cfg: AppConfig, projectRepo: ProjectRepo):
        self.__projectRepo = projectRepo
        self.__cfg = cfg

    async def Auth(self, req: Request, next: callable):
        auth_header = req.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return responses.JSONResponse(status_code=401, content="Unauthorized")

        token = auth_header.replace("Bearer ", "")
        project_id = req.path_params["project_id"]
        member_ids = self.__projectRepo.get_member_ids(project_id)

        payload = jwt.verify_jwt(
            token, self.__cfg.AUTH_JWT_SECRET, algorithms=["HS256"])
        print(member_ids)
        print(payload)

        if token != "123":
            return responses.JSONResponse(status_code=401, content="Unauthorized")

        response = await next(req)
        return response
